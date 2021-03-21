from bs4 import BeautifulSoup
import requests


def href_checker(href):
    return href and href.startswith('http') and not href.endswith(('.css', 
     '.js', '.pdf', '.jpeg', 'tiff', '.svg', '.png', '#', 'javascript:void(0)'))


def scrape(url_list):
    child_urls = {}
    # should it be a set to avoid duplicates or are duplicates
    # needed for computing pagerank?
    error_urls = []
    for url in url_list:
        try:
            response = requests.get(url)
            page = BeautifulSoup(response.text, 'html.parser')
            child_url_list = []
            for link in page.find_all(href=href_checker):
                child_url_list.append(link['href'])
            child_urls[url] = child_url_list
        except:
            error_urls.append(url)
    return child_urls


# testing
print(scrape(['https://www.iiit.ac.in/', 'https://scholar.google.com/intl/en/scholar/about.html']))
