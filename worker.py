import Pyro5.api
from bs4 import BeautifulSoup
import requests

def href_checker(href):
    return href and href.startswith('http') and not href.endswith(('.css', 
    '.js', '.pdf', '.jpeg', 'tiff', '.svg', '.png', '#', 'javascript:void(0)'))


@Pyro5.api.expose
@Pyro5.api.behavior(instance_mode="single")
class Worker:
    def __init__(self):
        self.pages = {}

    def scrape(self,url_list):
        child_urls = {}
        # should it be a set to avoid duplicates or are duplicates
        # needed for computing pagerank?
        error_urls = []
        for url in url_list:
            try:
                response = requests.get(url)
                self.pages[url] = response.text
                page = BeautifulSoup(response.text, 'html.parser')
                child_url_list = []
                for link in page.find_all(href=href_checker):
                    child_url_list.append(link['href'])
                child_urls[url] = child_url_list
            except:
                error_urls.append(url)
        return child_urls, error_urls


# testing
# print(scrape(['https://www.iiit.ac.in/', 'https://scholar.google.com/intl/en/scholar/about.html']))

   

daemon = Pyro5.server.Daemon()         
ns = Pyro5.api.locate_ns()     
server_list = ns.list()
worker_number = len(server_list.keys())    
uri = daemon.register(Worker) 
ns.register("Worker_" + str(worker_number), uri)   

print("Ready.")
daemon.requestLoop()    