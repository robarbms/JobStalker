from bs4 import BeautifulSoup
import requests

"""
    Gets the contents of a page and returns it as a soup object
"""
def getPage(url):
    request_headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
    }

    print("Getting page for {0}...".format(url))
    response = requests.get(url, headers=request_headers)
    if response.status_code == 200:
        print("Page successfully downloaded.")
        html_doc = response.text
        print("Received {0} bytes.".format(len(html_doc)))
        print("Parsing page...")
        soup = BeautifulSoup(html_doc, 'html.parser')
        print("Page sucessfully parsed. Returning as a soup object.")
        return soup
    else:
        msg = "Error: {0}. Unable to get page content for {1}".format(response.status_code, url)
        print(msg)
        return {
            'error': msg
        }
    

queries = [
    "frontend",
    "ui",
    "ux",
]