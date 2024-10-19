import torch
from transformers import LlamaForCausalLM, pipeline, PreTrainedTokenizerFast, BitsAndBytesConfig, BartModel, BartForCausalLM, BartTokenizer, AutoTokenizer, AutoModelForSeq2SeqLM
from sentence_transformers import SentenceTransformer
import re
import time

class JobAnalyzer:
    model_path = "./models/"
    model = None
    context = ""
    max_length = 1300
    models = {
        'default': {
            'directory': 'llama-3.1-8b',
            'type': 'llama',
            '8-bit': True
        },
        'llama-3.1': {
            'directory': 'llama-3.1-8b',
            'type': 'llama',
        },
        'keywords': {
            'directory': 'tech-keywords-extractor',
            'type': 'bart',
            '8-bit': False
        },
        'summary': {
            'directory': 'bart-large-cnn',
            'type': 'bart',
            '8-bit': False
        }
    }

    def set_model(self, name='default'):
        if self.model != None:
            print(f"Unloading existing model")
            del self.model
            del self.tokenizer
            torch.cuda.empty_cache()
            time.sleep(5)
        config = self.models[name]
        pretrained = {
            'llama': LlamaForCausalLM.from_pretrained,
            'bart': AutoModelForSeq2SeqLM.from_pretrained
        }[config['type']]
        tokenizer = {
            'llama': PreTrainedTokenizerFast.from_pretrained,
            'bart': BartTokenizer.from_pretrained
        }[config['type']]
        self.tokenizer = tokenizer(self.model_path + config['directory'])

        quantization_config = BitsAndBytesConfig(load_in_8bit=config['8-bit'])

        print(f"Loading model {name} using {self.device}")

        self.model = pretrained(
            self.model_path + config['directory'],
            torch_dtype='auto',
            device_map={'': self.device},
            quantization_config=quantization_config
        )

    def __init__(self):
        # Set device to GPU
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        # self.device = "cpu"
        print("DEVICE >>>> ", self.device)
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')

    def clear_context(self):
        self.context = ""

    def add_context(self, content):
        self.context += content

    # Gets a summary of provided text or uses the local context if not specified
    def get_summary(self, text=None):
        if text is None:
            text = self.context
        summarizer = pipeline('summarization', model="./ai/models/bart-base-job-info-summarizer", device=self.device)
        summary = summarizer(text, max_length=200, min_length=100, do_sample=False)

        return summary

    # Runs a query agains the text provided, otherwise will use the current context
    def generate(self, prompt, text=None):
        # If a model has not been set yet, initialize it with the default model
        if self.model == None:
            self.set_model()
        if text == None:
            text = self.context
        input_text = f"Context:\n{text}\n\nQuestion: {prompt}\nAnswer:"
        inputs = self.tokenizer(input_text, return_tensors="pt").to('cuda')
        with torch.no_grad():
            output = self.model.generate(
                **inputs,
                max_length=self.max_length,
                temperature=0.85,
            )

        response = self.tokenizer.decode(output[0], skip_special_tokens=True)
        output_text = response.replace(input_text, "")
        output_text = re.sub(r'\w*Question:.*$', '', output_text, flags=re.DOTALL)

        return output_text

if __name__ == "__main__":
    print("Starting job analyzer")
    analyzer = JobAnalyzer()
    job = open("test/example_job1.txt")
    job_description = job.read()
    job.close()
    analyzer.add_context("[JOB DESCRIPTION]:\n" + job_description)
    print(f"Characters in job: {len(analyzer.context)}")
    summary = analyzer.get_summary()
    print(f"Summary: {summary}")

    pay = analyzer.get_pay()
    print(f"Pay: {pay}")

    tags = analyzer.get_tags()
    print(f"Tags: {tags}")
