import requests
from bs4 import BeautifulSoup


def copy_html_after_div(url, div_class):
    # Define headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Send a GET request with headers
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to retrieve the page. Status code: {response.status_code}")

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the target div with the specified class
    target_div = soup.find("div", class_=div_class)
    if not target_div:
        raise Exception(f"Div with class '{div_class}' not found.")

    # Get all inner HTML after the target div
    html_after_div = ''
    for sibling in target_div.find_all_next():
        html_after_div += str(sibling)

    return html_after_div

# Example usage:
url = 'https://www.beatport.com/genre/progressive-house/15/top-100'
div_class = 'Table-style__TableData-sc-fdd08fbd-2 hKhaa'
inner_html = copy_html_after_div(url, div_class)
print(type(inner_html))