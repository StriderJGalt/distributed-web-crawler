from requests_html import HTMLSession
from bs4 import BeautifulSoup
import requests


session = HTMLSession()

def scrape(url_list):
        child_urls = {}
        error_urls = []
        for url in url_list:
            try:
                r = session.get(url)
                withoutrender = r.html.absolute_links
                r.html.render()
                withrender = r.html.absolute_links
                child_urls[url] = withoutrender.union(withrender)
            except:
                error_urls.append(url)
        return child_urls, error_urls

c,e = scrape(["https://open.spotify.com/",'https://www.spotify.com/us/legal/cookies-vendor-list/'])
print(c)
print(e)