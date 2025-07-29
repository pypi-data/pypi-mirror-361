# LucaGPLM

LucaGPLM - The LUCA general purpose language model.

## Installation

You can install the package from source using pip:

```bash
pip install .
```

## Usage

```python
from lucagplm import LucaGPLMModel, LucaGPLMTokenizer

# Load model
model = LucaGPLMModel.from_pretrained("Yuanfei/lucavirus-large-step3.8M")
tokenizer = LucaGPLMTokenizer.from_pretrained("Yuanfei/lucavirus-large-step3.8M")

# Example usage
seq = "ATCG"
inputs = tokenizer(seq, seq_type="gene",return_tensors="pt")
outputs = model(**inputs)

seq = "NSQTA"
inputs = tokenizer(seq, seq_type="prot",return_tensors="pt")
outputs = model(**inputs)

print(outputs.last_hidden_state.shape)
```
