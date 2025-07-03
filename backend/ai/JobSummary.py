import torch
from transformers import pipeline

# Chunks a text into smaller chunks of specified size.
def chunk_text(text, chunk_size=500):
    words = text.split()
    chunks = [words[i:i+chunk_size] for i in range(0, len(words), chunk_size)]
    return chunks

# Gets a summary of a job description using BART base model.
def get_summary(description: str, skipAi=False):
    description = description.strip()
    if skipAi == False:
        try:
            words_count = len(description.split())
            if words_count<200:
                return description
            # Set device to GPU if available
            device = "cuda" if torch.cuda.is_available() else "cpu"
            chunks = chunk_text(description, 300)

            summarizer = pipeline('summarization', model="./ai/models/bart-large-cnn", device=device)
            if len(chunks) > 1:
                summaries = []
                for chunk in chunks:
                    if len(chunk) > 200:
                        chunk_summary = summarizer(' '.join(chunk), max_length=200, min_length=50, do_sample=False)
                        if chunk_summary and chunk_summary[0]:
                            summaries.append(chunk_summary[0]['summary_text'])
                    else:
                        summaries.append(' '.join(chunk))
                description = ' '.join(summaries)
            if len(description.split()) > 200:
                summary_obj = summarizer(description, max_length=200, min_length=50, do_sample=False)
                summary = summary_obj[0]['summary_text']
            else:
                summary = description
            summary = summary.replace("'", "") # Escape single quotes for SQL query
            summary = summary.strip()

            return summary
        except Exception as e:
            print(f"Error occurred while summarizing the job description: {e}")
    
    return description[0:400]
