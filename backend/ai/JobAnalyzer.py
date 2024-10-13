import torch
from transformers import LlamaForCausalLM, pipeline, PreTrainedTokenizerFast
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from utils import log
import re

class JobAnalyzer:
    model_path = "./models/"
    def __init__(self):
        self.tokenizer = PreTrainedTokenizerFast.from_pretrained(self.model_path)
        log(f"Cuda version: {torch.version.cuda}")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        log(f"Loading model using {device}")

        self.model = LlamaForCausalLM.from_pretrained(
            self.model_path,
            torch_dtype="auto",
            device_map={"": device}
        )
        log("Model loaded")

        self.pipeline = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer)
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
    
    def get_tags(self):
        query = "Give me a comma separated list languages, technologies, programming libraries and software required by the job description."
        log(f"Query: {query}")
        response = self.generate(query)

        return response
    
    def get_pay(self):
        query = "Give a 1 sentence summary of the pay for the job description."
        response = self.generate(query)

        return response
    
    def get_summary(self):
        summarizer = pipeline("summarization", model=self.model, tokenizer=self.tokenizer, max_length=10000)
        summary = summarizer(self.job)

        return summary

    def generate(self, prompt, includes=['job'], k=3):
        input_text = f"Context:\n{self.job}\n\nQuestion: {prompt}\nAnswer:"

        log(f"Text length: {len(input_text)}")

        inputs = self.tokenizer(input_text, return_tensors="pt").to('cuda')

        with torch.no_grad():
            output = self.model.generate(**inputs, max_new_tokens=100)

        log(f"Output length: {len(output)}")
        response = self.tokenizer.decode(output[0], skip_special_tokens=True)
        output_text = response.replace(input_text, "")
        output_text = re.sub(r'\w*Question:.*$', '', output_text, flags=re.DOTALL)

        log(f"Response length: {len(response)}, output length: {len(output_text)}")

        return output_text
        
    def set_resume(self, resume_text: str):
        self.resume = "[RESUME]:\n" + resume_text
    
    def set_job(self, job_description: str):
        self.job = "[JOB DESCRIPTION]:\n" + job_description

if __name__ == "__main__":
    log("Starting job analyzer")
    analyzer = JobAnalyzer()
    job = open("test/example_job4.txt")
    analyzer.set_job(job.read())
    job.close()
    log(f"Characters in job: {len(analyzer.job)}")
    response = analyzer.get_summary()
    log(response)
