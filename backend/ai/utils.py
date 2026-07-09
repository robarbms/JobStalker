from datetime import datetime
from huggingface_hub import hf_hub_download

def log(message: str, level="info"):
    ct = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # fd = datetime.now().strftime("%Y-%m-%d")

    log_msg = message
    if level != None:
        log_msg = "[{0}] {1}: {2}".format(level.upper(), ct, message)
        
    print(log_msg)

def download_hf_model(repo_id: str, output: str):
    local_dir = 'backend/ai/models/' + output + '/'
    filenames = ['config.json', 'merges.txt', 'vocab.json', 'model.safetensors']

    for filename in filenames:
        hf_hub_download(repo_id=repo_id, filename=filename, local_dir=local_dir)

if __name__ == "__main__": 
    download_hf_model(repo_id='avisena/bart-base-job-info-summarizer', output='bart-base-job-info-summarizer')
