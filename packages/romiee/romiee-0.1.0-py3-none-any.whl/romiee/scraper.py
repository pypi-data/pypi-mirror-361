import requests
from bs4 import BeautifulSoup

def fetch_html(url):
    response = requests.get(url)
    return response.text

def extract_title(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup.title.string if soup.title else "No title found"
