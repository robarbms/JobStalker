from datetime import datetime
from pathlib import Path
import asyncio
import os
import aiohttp
import aiofiles

def log(message: str, level="info"):
    ct = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fd = datetime.now().strftime("%Y-%m-%d")

    log_msg = message
    if level != None:
        log_msg = "[{0}] {1}: {2}".format(level.upper(), ct, message)
        
    print(log_msg)

async def download_file(session: aiohttp.ClientSession, url: str, out: str):
    """Downloads a single file asynchronously by streaming chunks to disk."""
    # Extract filename from URL
    filename = os.path.basename(url) or "downloaded_file"
    filepath = os.path.join(out, filename)
    
    print(f"Starting download: {url}")
    print(f"Outputting to: {filepath}")
    
    try:
        async with session.get(url) as response:
            # Check for bad HTTP response statuses (like 404 or 500)
            response.raise_for_status()
            
            # Open file asynchronously and stream contents
            async with aiofiles.open(filepath, "wb") as f:
                async for chunk in response.content.iter_chunked(8192): # 8KB chunks
                    await f.write(chunk)
                    
        print(f" Finished: {filename}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")

async def ensure_model():
    directory = './models/bart-large-cnn/'
    files = ['config.json', 'merges.txt', 'vocab.json', 'model.safetensors']
    repo_url = 'https://huggingface.co/facebook/bart-large-cnn/resolve/main/'
    has_files = True

    for file in files:
        file_path = Path(directory + file)
        if file_path.is_file() == False:
            has_files = False
            break

    if has_files:
        return True
    
    async with aiohttp.ClientSession() as session:
        tasks = [download_file(session, repo_url + file, directory + file) for file in files]

    await asyncio.gather(*tasks)
