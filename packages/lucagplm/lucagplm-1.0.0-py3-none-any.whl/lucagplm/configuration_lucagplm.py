from transformers import PretrainedConfig

class LucaGPLMConfig(PretrainedConfig):
    model_type = "lucagplm"
    
    def __init__(
        self,
        vocab_size: int = -1,
        pad_token_id: int = 0,
        max_position_embeddings: int = 4096,
        type_vocab_size: int = 2,
        num_hidden_layers: int = 24,
        hidden_size: int = 1280,
        num_attention_heads: int = 20,
        ffn_dim: int = 5120,
        no_position_embeddings: bool = False,
        no_token_type_embeddings: bool = False,
        alphabet: str = "gene_prot",
        token_dropout: bool = True,
        attention_probs_dropout_prob: float = 0.1,
        hidden_dropout_prob: float = 0.1,
        classifier_dropout_prob: float = 0.1,
        use_embed_layer_norm: bool = True,
        use_last_layer_norm: bool = True,
        embed_scale: float = 1.0,
        ignore_index: int = -100,
        layer_norm_eps: float = 1e-12,
        initializer_range: float = 0.02,
        **kwargs
    ):
        super().__init__(pad_token_id=pad_token_id, **kwargs)
        
        self.alphabet = alphabet
        self.vocab_size = vocab_size
        self.max_position_embeddings = max_position_embeddings
        self.type_vocab_size = type_vocab_size
        self.no_token_type_embeddings = no_token_type_embeddings
        self.no_position_embeddings = no_position_embeddings
        self.num_hidden_layers = num_hidden_layers
        self.hidden_size = hidden_size
        self.num_attention_heads = num_attention_heads
        self.ffn_dim = ffn_dim
        self.token_dropout = token_dropout
        self.attention_probs_dropout_prob = attention_probs_dropout_prob
        self.hidden_dropout_prob = hidden_dropout_prob
        self.classifier_dropout_prob = classifier_dropout_prob
        self.ignore_index = ignore_index
        self.use_embed_layer_norm = use_embed_layer_norm
        self.use_last_layer_norm = use_last_layer_norm
        self.embed_scale = embed_scale
        self.layer_norm_eps = layer_norm_eps
        self.initializer_range = initializer_range

__all__ = ["LucaGPLMConfig"]