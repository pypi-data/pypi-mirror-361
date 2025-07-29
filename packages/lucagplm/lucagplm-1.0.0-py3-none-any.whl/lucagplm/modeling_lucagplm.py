import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import PreTrainedModel
from transformers.modeling_outputs import BaseModelOutput
from typing import Optional, List, Union, Tuple
from .configuration_lucagplm import LucaGPLMConfig

def gelu(x):
    return x * 0.5 * (1.0 + torch.erf(x / math.sqrt(2.0)))

def rotate_half(x):
    x1, x2 = x.chunk(2, dim=-1)
    return torch.cat((-x2, x1), dim=-1)

def apply_rotary_pos_emb(x, cos, sin):
    cos = cos[:, : x.shape[-2], :]
    sin = sin[:, : x.shape[-2], :]
    return (x * cos) + (rotate_half(x) * sin)

class RotaryEmbedding(torch.nn.Module):
    def __init__(self, dim: int, *_, **__):
        super().__init__()
        inv_freq = 1.0 / (10000 ** (torch.arange(0, dim, 2).float() / dim))
        self.register_buffer("inv_freq", inv_freq)

        self._seq_len_cached = None
        self._cos_cached = None
        self._sin_cached = None

    def _update_cos_sin_tables(self, x, seq_dimension=1):
        seq_len = x.shape[seq_dimension]

        if (seq_len != self._seq_len_cached or 
            self._cos_cached is None or 
            self._sin_cached is None or
            self._cos_cached.device != x.device):
            self._seq_len_cached = seq_len
            t = torch.arange(x.shape[seq_dimension], device=x.device).type_as(self.inv_freq)
            freqs = torch.einsum("i,j->ij", t, self.inv_freq)
            emb = torch.cat((freqs, freqs), dim=-1).to(x.device)

            self._cos_cached = emb.cos()[None, :, :]
            self._sin_cached = emb.sin()[None, :, :]

        return self._cos_cached, self._sin_cached

    def forward(self, q: torch.Tensor, k: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        self._cos_cached, self._sin_cached = self._update_cos_sin_tables(k, seq_dimension=-2)

        return (
            apply_rotary_pos_emb(q, self._cos_cached, self._sin_cached),
            apply_rotary_pos_emb(k, self._cos_cached, self._sin_cached),
        )

try:
    from apex.normalization import FusedLayerNorm as _FusedLayerNorm
    class LucaGPLM1bLayerNorm(_FusedLayerNorm):
        @torch.jit.unused
        def forward(self, x):
            if not x.is_cuda:
                return super().forward(x)
            else:
                with torch.cuda.device(x.device):
                    return super().forward(x)
except ImportError:
    from torch.nn import LayerNorm as LucaGPLM1bLayerNorm

class LucaGPLM1LayerNorm(nn.Module):
    def __init__(self, hidden_size, eps=1e-12, affine=True):
        super().__init__()
        self.hidden_size = (hidden_size,) if isinstance(hidden_size, int) else tuple(hidden_size)
        self.eps = eps
        self.affine = bool(affine)
        if self.affine:
            self.weight = nn.Parameter(torch.ones(hidden_size))
            self.bias = nn.Parameter(torch.zeros(hidden_size))
        else:
            self.weight, self.bias = None, None

    def forward(self, x):
        dims = tuple(-(i + 1) for i in range(len(self.hidden_size)))
        means = x.mean(dims, keepdim=True)
        x_zeromean = x - means
        variances = x_zeromean.pow(2).mean(dims, keepdim=True)
        x = x_zeromean / torch.sqrt(variances + self.eps)
        if self.affine:
            x = (self.weight * x) + self.bias
        return x

class LucaGPLMMultiheadAttention(nn.Module):
    def __init__(
        self,
        embed_dim,
        num_heads,
        kdim=None,
        vdim=None,
        dropout=0.0,
        bias=True,
        add_bias_kv: bool = False,
        add_zero_attn: bool = False,
        self_attention: bool = False,
        encoder_decoder_attention: bool = False,
        use_rotary_embeddings: bool = False,
    ):
        super().__init__()
        self.embed_dim = embed_dim
        self.kdim = kdim if kdim is not None else embed_dim
        self.vdim = vdim if vdim is not None else embed_dim
        self.qkv_same_dim = self.kdim == embed_dim and self.vdim == embed_dim

        self.num_heads = num_heads
        self.dropout = dropout
        self.head_dim = embed_dim // num_heads
        assert (
            self.head_dim * num_heads == self.embed_dim
        ), "embed_dim must be divisible by num_heads"
        self.scaling = self.head_dim**-0.5

        self.self_attention = self_attention
        self.encoder_decoder_attention = encoder_decoder_attention

        assert not self.self_attention or self.qkv_same_dim, (
            "Self-attention requires query, key and " "value to be of the same size"
        )

        self.k_proj = nn.Linear(self.kdim, embed_dim, bias=bias)
        self.v_proj = nn.Linear(self.vdim, embed_dim, bias=bias)
        self.q_proj = nn.Linear(embed_dim, embed_dim, bias=bias)

        self.out_proj = nn.Linear(embed_dim, embed_dim, bias=bias)

        if add_bias_kv:
            self.bias_k = nn.Parameter(torch.Tensor(1, 1, embed_dim))
            self.bias_v = nn.Parameter(torch.Tensor(1, 1, embed_dim))
        else:
            self.bias_k = self.bias_v = None

        self.add_zero_attn = add_zero_attn

        self.reset_parameters()

        self.rot_emb = None
        if use_rotary_embeddings:
            self.rot_emb = RotaryEmbedding(dim=self.head_dim)

    def reset_parameters(self):
        nn.init.xavier_uniform_(self.k_proj.weight, gain=nn.init.calculate_gain("relu"))
        nn.init.xavier_uniform_(self.v_proj.weight, gain=nn.init.calculate_gain("relu"))
        nn.init.xavier_uniform_(self.q_proj.weight, gain=nn.init.calculate_gain("relu"))
        nn.init.xavier_uniform_(self.out_proj.weight, gain=nn.init.calculate_gain("relu"))
        
        if self.out_proj.bias is not None:
            nn.init.constant_(self.out_proj.bias, 0.0)
        if self.bias_k is not None:
            nn.init.xavier_normal_(self.bias_k)
        if self.bias_v is not None:
            nn.init.xavier_normal_(self.bias_v)

    def forward(
        self,
        query,
        key: Optional[torch.Tensor] = None,
        value: Optional[torch.Tensor] = None,
        key_padding_mask: Optional[torch.Tensor] = None,
        need_weights: bool = True,
        attn_mask: Optional[torch.Tensor] = None,
        need_head_weights: bool = False,
    ) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
        if need_head_weights:
            need_weights = True

        tgt_len, bsz, embed_dim = query.size()
        assert embed_dim == self.embed_dim

        if self.self_attention:
            q = self.q_proj(query)
            k = self.k_proj(query)
            v = self.v_proj(query)
        else:
            assert key is not None and value is not None
            q = self.q_proj(query)
            k = self.k_proj(key)
            v = self.v_proj(value)

        q *= self.scaling

        if self.bias_k is not None:
            assert self.bias_v is not None
            k = torch.cat([k, self.bias_k.repeat(1, bsz, 1)])
            v = torch.cat([v, self.bias_v.repeat(1, bsz, 1)])
            if attn_mask is not None:
                attn_mask = torch.cat(
                    [attn_mask, attn_mask.new_zeros(attn_mask.size(0), 1)], dim=1
                )
            if key_padding_mask is not None:
                key_padding_mask = torch.cat(
                    [
                        key_padding_mask,
                        key_padding_mask.new_zeros(key_padding_mask.size(0), 1),
                    ],
                    dim=1,
                )

        q = q.contiguous().view(tgt_len, bsz * self.num_heads, self.head_dim).transpose(0, 1)
        if k is not None:
            k = k.contiguous().view(-1, bsz * self.num_heads, self.head_dim).transpose(0, 1)
        if v is not None:
            v = v.contiguous().view(-1, bsz * self.num_heads, self.head_dim).transpose(0, 1)

        assert k is not None
        src_len = k.size(1)

        if self.rot_emb:
            q, k = self.rot_emb(q, k)

        attn_weights = torch.bmm(q, k.transpose(1, 2))
        assert list(attn_weights.size()) == [bsz * self.num_heads, tgt_len, src_len]

        if attn_mask is not None:
            attn_mask = attn_mask.unsqueeze(0)
            attn_weights += attn_mask

        if key_padding_mask is not None:
            attn_weights = attn_weights.view(bsz, self.num_heads, tgt_len, src_len)
            attn_weights = attn_weights.masked_fill(
                key_padding_mask.unsqueeze(1).unsqueeze(2).to(torch.bool), float("-inf")
            )
            attn_weights = attn_weights.view(bsz * self.num_heads, tgt_len, src_len)

        attn_weights_float = F.softmax(attn_weights, dim=-1)
        attn_weights = attn_weights_float.type_as(attn_weights)
        attn_probs = F.dropout(
            attn_weights_float.type_as(attn_weights),
            p=self.dropout,
            training=self.training,
        )

        assert v is not None
        attn = torch.bmm(attn_probs, v)
        assert list(attn.size()) == [bsz * self.num_heads, tgt_len, self.head_dim]
        attn = attn.transpose(0, 1).contiguous().view(tgt_len, bsz, embed_dim)
        attn = self.out_proj(attn)

        attn_weights_output: Optional[torch.Tensor] = None
        if need_weights:
            attn_weights_output = attn_weights_float.view(
                bsz, self.num_heads, tgt_len, src_len
            ).type_as(attn).transpose(1, 0)
            if not need_head_weights:
                # average attention weights over heads
                attn_weights_output = attn_weights_output.mean(dim=0)

        return attn, attn_weights_output

class LucaGPLMTransformerLayer(nn.Module):
    def __init__(
        self,
        embed_dim,
        ffn_embed_dim,
        attention_heads,
        add_bias_kv=True,
        use_lucagplm1b_layer_norm=False,
        use_rotary_embeddings: bool = False,
    ):
        super().__init__()
        self.embed_dim = embed_dim
        self.ffn_embed_dim = ffn_embed_dim
        self.attention_heads = attention_heads
        self.use_rotary_embeddings = use_rotary_embeddings
        
        LucaGPLMLayerNorm = LucaGPLM1bLayerNorm if use_lucagplm1b_layer_norm else LucaGPLM1LayerNorm

        self.pre_layer_norm = LucaGPLMLayerNorm(self.embed_dim)

        self.self_attn = LucaGPLMMultiheadAttention(
            self.embed_dim,
            self.attention_heads,
            add_bias_kv=add_bias_kv,
            add_zero_attn=False,
            self_attention=True,
            use_rotary_embeddings=self.use_rotary_embeddings,
        )

        # post layer norm
        self.post_layer_norm = LucaGPLMLayerNorm(self.embed_dim)

        # dimension increase by the fully connected layer
        self.fc1 = nn.Linear(self.embed_dim, self.ffn_embed_dim)

        # dimension reduction by the fully connected layer
        self.fc2 = nn.Linear(self.ffn_embed_dim, self.embed_dim)

    def forward(
        self,
        x,
        self_attn_mask=None,
        self_attn_padding_mask=None,
        need_head_weights=False
    ):
        residual = x
        x = self.pre_layer_norm(x)
        x, attn = self.self_attn(
            query=x,
            key=x,
            value=x,
            key_padding_mask=self_attn_padding_mask,
            need_weights=True,
            need_head_weights=need_head_weights,
            attn_mask=self_attn_mask,
        )
        x = residual + x

        residual = x
        x = self.post_layer_norm(x)
        x = gelu(self.fc1(x))
        x = self.fc2(x)
        x = residual + x

        return x, attn

class LucaGPLMEmbeddings(nn.Module):
    def __init__(self, config: LucaGPLMConfig):
        super().__init__()
        
        # Store config flags for forward pass
        self.no_position_embeddings = getattr(config, 'no_position_embeddings', False)
        self.no_token_type_embeddings = getattr(config, 'no_token_type_embeddings', False)
        self.use_embed_layer_norm = getattr(config, 'use_embed_layer_norm', True)
        self.embed_scale = getattr(config, 'embed_scale', 1.0)
        self.token_dropout = getattr(config, 'token_dropout', False)
        
        # Token ids for special tokens (matching old model)
        self.mask_idx = getattr(config, 'mask_token_id', 4)
        self.padding_idx = getattr(config, 'pad_token_id', 0)

        self.embed_tokens = nn.Embedding(config.vocab_size, config.hidden_size, padding_idx=config.pad_token_id)
        
        # Only create position embeddings if not disabled
        if not self.no_position_embeddings:
            self.embed_pos = nn.Embedding(config.max_position_embeddings, config.hidden_size)
        else:
            self.embed_pos = None
            
        # Only create token type embeddings if not disabled    
        if not self.no_token_type_embeddings:
            self.embed_type = nn.Embedding(config.type_vocab_size, config.hidden_size)
        else:
            self.embed_type = None
            
        # Only create layer norm if enabled
        if self.use_embed_layer_norm:
            self.embed_layer_norm = LucaGPLM1bLayerNorm(config.hidden_size)
        else:
            self.embed_layer_norm = None

    def forward(
        self,
        input_ids: torch.Tensor,
        token_type_ids: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        input_shape = input_ids.size()
        seq_length = input_shape[1]

        # Start with token embeddings and apply embed_scale
        inputs_embeds = self.embed_scale * self.embed_tokens(input_ids)
        
        # Add position embeddings if enabled
        if not self.no_position_embeddings and self.embed_pos is not None:
            if position_ids is None:
                position_ids = torch.arange(seq_length, dtype=torch.long, device=input_ids.device)
                position_ids = position_ids.unsqueeze(0).expand(input_shape)
            position_embeddings = self.embed_scale * self.embed_pos(position_ids)
            inputs_embeds = inputs_embeds + position_embeddings

        # Add token type embeddings if enabled
        if not self.no_token_type_embeddings and self.embed_type is not None:
            if token_type_ids is None:
                token_type_ids = torch.zeros(input_shape, dtype=torch.long, device=input_ids.device)
            token_type_embeddings = self.embed_scale * self.embed_type(token_type_ids)
            inputs_embeds = inputs_embeds + token_type_embeddings
        
        # Apply layer norm if enabled
        if self.use_embed_layer_norm and self.embed_layer_norm is not None:
            embeddings = self.embed_layer_norm(inputs_embeds)
        else:
            embeddings = inputs_embeds

        # Apply token dropout (matching old model behavior)
        if self.token_dropout and self.training:
            # Zero out masked token embeddings
            embeddings = embeddings.masked_fill((input_ids == self.mask_idx).unsqueeze(-1), 0.0)
            
            # Apply token dropout scaling
            mask_ratio_train = 0.15 * 0.8
            padding_mask = input_ids.eq(self.padding_idx)
            src_lengths = (~padding_mask).sum(-1)
            mask_ratio_observed = (input_ids == self.mask_idx).sum(-1).to(embeddings.dtype) / src_lengths
            embeddings = embeddings * (1 - mask_ratio_train) / (1 - mask_ratio_observed)[:, None, None]

        # Apply padding mask to embeddings
        padding_mask = input_ids.eq(self.padding_idx)
        if padding_mask.any():
            embeddings = embeddings * (1 - padding_mask.unsqueeze(-1).type_as(embeddings))

        return embeddings

class LucaGPLMEncoder(nn.Module):
    def __init__(self, config: LucaGPLMConfig):
        super().__init__()

        self.layers = nn.ModuleList([
            LucaGPLMTransformerLayer(
                config.hidden_size,
                4 * config.hidden_size,  # ffn_embed_dim = 4 * embed_dim
                config.num_attention_heads,
                add_bias_kv=False,
                use_lucagplm1b_layer_norm=True,
                use_rotary_embeddings=True,
            )
            for _ in range(config.num_hidden_layers)
        ])
        
        self.use_last_layer_norm = getattr(config, 'use_last_layer_norm', True)
        if self.use_last_layer_norm:
            self.last_layer_norm = LucaGPLM1bLayerNorm(config.hidden_size)
        else:
            self.last_layer_norm = None

        self.padding_idx = config.pad_token_id
        self.gradient_checkpointing = False

    def forward(
        self,
        hidden_states: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        output_attentions: bool = False,
        output_hidden_states: bool = False,
        return_dict: bool = True,
        need_head_weights: bool = False,
        repr_layers: Optional[List[int]] = None,
        use_last_layer_norm: bool = True,
    ) -> Union[Tuple[torch.Tensor], BaseModelOutput]:
        all_hidden_states = () if output_hidden_states else None
        all_attentions = () if output_attentions else None
        
        if repr_layers is None:
            repr_layers = [-1]
        
        # 转换为原始模型的索引系统
        layer_size = len(self.layers)
        repr_layers = [(i + layer_size + 1) % (layer_size + 1) for i in repr_layers]
        repr_layers = set(repr_layers)
        hidden_representations = {}

        # Process attention mask - 原始模型期望的是padding mask
        if attention_mask is None:
            padding_mask = hidden_states.new_zeros(hidden_states.shape[:2]).eq(self.padding_idx)
        else:
            # 原始模型中 padding_mask 是 True 表示 padding位置
            padding_mask = attention_mask.eq(0)

        # 0: embedding layer
        if 0 in repr_layers:
            hidden_representations[0] = hidden_states

        # 转换为 (seq_len, batch_size, hidden_size) 格式，与原始模型一致
        hidden_states = hidden_states.transpose(0, 1)
        
        if not padding_mask.any():
            padding_mask = None

        # 是否需要返回head weights
        if need_head_weights or output_attentions:
            attn_weights = []

        for layer_idx, layer_module in enumerate(self.layers):
            if output_hidden_states:
                all_hidden_states = all_hidden_states + (hidden_states.transpose(0, 1),)

            if self.gradient_checkpointing and self.training:
                layer_outputs = self._gradient_checkpointing_func(
                    layer_module.__call__,
                    hidden_states,
                    None,  # self_attn_mask
                    padding_mask,
                    need_head_weights or output_attentions,
                )
            else:
                layer_outputs = layer_module(
                    hidden_states,
                    self_attn_mask=None,
                    self_attn_padding_mask=padding_mask,
                    need_head_weights=need_head_weights or output_attentions,
                )

            hidden_states, attn = layer_outputs

            if (layer_idx + 1) in repr_layers:
                hidden_representations[layer_idx + 1] = hidden_states.transpose(0, 1)

            if need_head_weights or output_attentions:
                # (H, B, L, L) => (B, H, L, L)
                attn_weights.append(attn.transpose(1, 0))

        # 应用最后的layer norm
        if self.last_layer_norm is not None and use_last_layer_norm:
            hidden_states = self.last_layer_norm(hidden_states)

        # 转换回 (batch_size, seq_len, hidden_size) 格式
        hidden_states = hidden_states.transpose(0, 1)

        # last hidden representation should have layer norm applied
        if (layer_idx + 1) in repr_layers:
            hidden_representations[layer_idx + 1] = hidden_states

        if output_hidden_states:
            all_hidden_states = all_hidden_states + (hidden_states,)

        if need_head_weights or output_attentions:
            # 将attention weights转换为正确格式
            if attn_weights:
                # B x Layers x H x L x L
                all_attentions = torch.stack(attn_weights, 1)
                if padding_mask is not None:
                    attention_mask_expanded = 1 - padding_mask.type_as(all_attentions)
                    attention_mask_expanded = attention_mask_expanded.unsqueeze(1) * attention_mask_expanded.unsqueeze(2)
                    all_attentions = all_attentions * attention_mask_expanded[:, None, None, :, :]
            
            if not output_attentions:
                all_attentions = None

        if not return_dict:
            return tuple(v for v in [hidden_states, all_hidden_states, all_attentions] if v is not None)

        return BaseModelOutput(
            last_hidden_state=hidden_states,
            hidden_states=all_hidden_states,
            attentions=all_attentions,
        )

class LucaGPLMPreTrainedModel(PreTrainedModel):
    config_class = LucaGPLMConfig
    base_model_prefix = "lucagplm"
    supports_gradient_checkpointing = True
    _no_split_modules = ["LucaGPLMTransformerLayer"]

    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.bias is not None:
                module.bias.data.zero_()
        elif isinstance(module, nn.Embedding):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.padding_idx is not None:
                module.weight.data[module.padding_idx].zero_()
        elif isinstance(module, (LucaGPLM1LayerNorm, LucaGPLM1bLayerNorm)):
            if hasattr(module, 'weight') and module.weight is not None:
                module.weight.data.fill_(1.0)
            if hasattr(module, 'bias') and module.bias is not None:
                module.bias.data.zero_()

class LucaGPLMModel(LucaGPLMPreTrainedModel):
    """
    The LucaGPLM model for extracting sequence representations and optionally predicting contacts.
    Based on the original LucaGPLM implementation but restructured to use modern transformers architecture.
    """
    
    def __init__(self, config: LucaGPLMConfig):
        super().__init__(config)
        self.config = config
        self.embeddings = LucaGPLMEmbeddings(self.config)
        self.encoder = LucaGPLMEncoder(self.config)
        self.post_init()

    def get_input_embeddings(self):
        return self.embeddings.embed_tokens

    def set_input_embeddings(self, value):
        self.embeddings.embed_tokens = value

    def forward(
        self,
        input_ids: Optional[torch.Tensor] = None,
        attention_mask: Optional[torch.Tensor] = None,
        token_type_ids: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.Tensor] = None,
        inputs_embeds: Optional[torch.Tensor] = None,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        return_contacts: Optional[bool] = None,
        return_dict: Optional[bool] = None,
        need_head_weights: Optional[bool] = None,
        repr_layers: Optional[List[int]] = None,
        use_last_layer_norm: Optional[bool] = True,
    ) -> Union[Tuple[torch.Tensor], BaseModelOutput]:
        
        output_attentions = output_attentions if output_attentions is not None else getattr(self.config, 'output_attentions', False)
        output_hidden_states = output_hidden_states if output_hidden_states is not None else getattr(self.config, 'output_hidden_states', False)
        return_contacts = return_contacts if return_contacts is not None else False
        return_dict = return_dict if return_dict is not None else getattr(self.config, 'use_return_dict', True)
        need_head_weights = need_head_weights if need_head_weights is not None else return_contacts  # Need attention weights for contacts
        use_last_layer_norm = use_last_layer_norm if use_last_layer_norm is not None else True

        # Force output_attentions=True when return_contacts=True since we need attention weights
        if return_contacts:
            output_attentions = True
            need_head_weights = True

        if input_ids is not None and inputs_embeds is not None:
            raise ValueError("You cannot specify both input_ids and inputs_embeds at the same time")
        elif input_ids is not None:
            input_shape = input_ids.size()
        elif inputs_embeds is not None:
            input_shape = inputs_embeds.size()[:-1]
        else:
            raise ValueError("You have to specify either input_ids or inputs_embeds")

        batch_size, seq_length = input_shape
        device = input_ids.device if input_ids is not None else inputs_embeds.device

        # Create attention mask if not provided
        if attention_mask is None:
            attention_mask = torch.ones(input_shape, device=device)

        # Get embeddings
        if inputs_embeds is None:
            embedding_output = self.embeddings(
                input_ids=input_ids,
                position_ids=position_ids,
                token_type_ids=token_type_ids,
            )
        else:
            embedding_output = inputs_embeds

        # Pass through encoder
        encoder_outputs = self.encoder(
            embedding_output,
            attention_mask=attention_mask,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
            need_head_weights=need_head_weights,
            repr_layers=repr_layers,
            use_last_layer_norm=use_last_layer_norm,
        )
        
        sequence_output = encoder_outputs[0]
        
        # Handle contact prediction
        contacts = None
        if return_contacts and encoder_outputs.attentions is not None:
            # Simple contact prediction using attention weights
            # This is a simplified implementation - you can enhance this later
            attentions = encoder_outputs.attentions
            # Average over layers and heads, then symmetrize
            averaged_attention = attentions.mean(dim=(1, 2))  # Average over layers and heads
            contacts = (averaged_attention + averaged_attention.transpose(-1, -2)) / 2
            
            # Remove special tokens (BOS/EOS) if present
            if attention_mask is not None:
                # Find actual sequence positions (non-padding)
                seq_lens = attention_mask.sum(dim=1)
                # For now, keep the full contact map - you can trim special tokens later if needed

        if not return_dict:
            outputs = (sequence_output, ) + encoder_outputs[1:]
            if contacts is not None:
                outputs = outputs + (contacts,)
            return outputs

        # Create output object with contacts
        output = BaseModelOutput(
            last_hidden_state=sequence_output,
            hidden_states=encoder_outputs.hidden_states,
            attentions=encoder_outputs.attentions,
        )
        
        # Add contacts as an attribute if computed
        if contacts is not None:
            output.contacts = contacts
            
        return output

__all__ = [
    "LucaGPLMModel",
    "LucaGPLMPreTrainedModel",
]
