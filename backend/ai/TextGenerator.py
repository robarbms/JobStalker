from transformers import LlamaTokenizer, LlamaForCausalLM, pipeline

class TextGenerator:
    model_path = "models/"
    def __init__(self):
        self.tokenizer = LlamaTokenizer.from_pretrained("llama-3.2-3b")