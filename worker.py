import Pyro5.api
import multiprocessing as mp
import threading
from requests_html import HTMLSession

MIN_URL_LIMIT = 20

worker_number = -1

def get_other_workers():
    # returns array of worker proxies excluding self
    ns = Pyro5.api.locate_ns()
    server_list = ns.list()
    workers = []
    selfname = "Worker_" + str(worker_number)
    del server_list['Pyro.NameServer']
    for server in server_list:
        if server != selfname:
            try:
                worker = Pyro5.client.Proxy(server_list[server])
                if worker.test():
                    workers.append(worker)
            except:
                pass
    if not workers:
        print("No other workers detected")
    return workers


@Pyro5.api.expose
@Pyro5.api.behavior(instance_mode="single")
class Worker:
    def __init__(self):
        # stores the html of all scraped pages
        self.pages = {}
        # stores the child urls of each url
        self.adjacency_list = {}
        # stores which other worker contains the children of these urls
        self.worker_incharge = {}
        # used to make object thread safe
        self._lock = threading.Lock()
        self.val = 0

    def getval(self):
        with self._lock:
            return self.val
        
    def test(self):
        # used to check whether server is online
        return True

    def scrape(self,url_list):

        session = HTMLSession()
        child_urls = {}
        error_urls = []
        for url in url_list:
            try:
                # downloads the page
                r = session.get(url)
                # extract links
                withoutrender = r.html.absolute_links
                # render js
                # r.html.render()
                withrender = r.html.absolute_links
                # return links present in html as well after rendering
                child_urls[url] = withoutrender.union(withrender)
                # store the html for later retrieval
                with self._lock:
                    self.pages[url] = r.text
            except:
                error_urls.append(url)
        # print log
        print("child URLs len")
        print(len(child_urls))
        print("error URLs")
        print(error_urls)
        return child_urls, error_urls

    def get_page(self,url):
        if url in self.pages.keys():
            return self.pages[url]
        return
        # return { url: self.pages[url] for url in urls }

    def remove_duplicates(self,urls):
        # remove already scraped urls
        with self._lock:
            new_urls = []
            to_be_crawled_urls = [] 
            for url in urls:
                if url not in self.adjacency_list.keys():
                    new_urls.append(url)
                else:
                    to_be_crawled_urls += list(self.adjacency_list[url])
        return new_urls, to_be_crawled_urls

    @Pyro5.server.oneway #makes it a non blocking call
    def crawl(self, urls, depth):
        print("start crawling at depth {}".format(depth))
        with self._lock:
            self.val += 1
        while True:
            print("crawling depth {}".format(depth))
            # remove already scraped urls
            urls, urls_to_be_crawled = self.remove_duplicates(urls)
            # scrape
            cu, eu = self.scrape(urls)
            # update adjacency list
            with self._lock:
                self.adjacency_list.update(cu)
            # print('al')
            # print(self.adjacency_list)
            # collect after removing already scraped urls from child urls
            for url in cu.keys():
                urls_to_be_crawled += list(cu[url])
            print('no child urls to be crawled')
            print(len(urls_to_be_crawled))
            # return if crawl depth is satisfied
            if depth == 1:
                print('finish depth {}'.format(depth))
                print("returning")
                with self._lock:
                    self.val -= 1
                return
            # distribute child urls to other workers
            workers = get_other_workers()
            print("no other workers")
            print(len(workers))
            num_urls_per_worker = max(
                (len(urls_to_be_crawled)//(len(workers)+1))+1,
                MIN_URL_LIMIT)
            print('num_urls_per_worker')
            print(num_urls_per_worker)
            next_urls = []
            for i in range(min(len(urls_to_be_crawled),
                                    num_urls_per_worker)):
                        url = urls_to_be_crawled.pop()
                        next_urls.append(url)
            # print('next_urls')
            # print(next_urls)        
            worker_index = 0    # need a better way to id workers
            while urls_to_be_crawled:
                urlgroup = []
                with self._lock:
                    for i in range(min(len(urls_to_be_crawled),
                                    num_urls_per_worker)):
                        url = urls_to_be_crawled.pop()
                        urlgroup.append(url)
                        self.worker_incharge[url] = worker_index
                workers[worker_index].crawl(urlgroup,depth-1)
                worker_index += 1
            urls = next_urls
            print('finish depth {}'.format(depth))
            depth -= 1
        # self.crawl(next_urls,depth-1)
        
    def get(self, urls):
        al = {}
        for url in urls:
            try:
                al[url] = self.adjacency_list[url]
            except:
                pass
        return al

    def ret(self):
        return self.adjacency_list

    def upd(self, url):
        if url not in self.adjacency_list.keys():
            return
        print(url)
        cu, eu = self.scrape([url])
        print("Updated URLs")
        with self._lock:
            for k in cu.keys():
                # print(cu[k])
                self.adjacency_list[k] = cu[k]
                print(self.adjacency_list[k])
        return


daemon = Pyro5.server.Daemon() 
# If connecting over internet unccoment below and replace hostname and port
# ns = Pyro5.api.locate_ns(host="gramaguru.local", port=8880)        
ns = Pyro5.api.locate_ns()     
server_list = ns.list()
worker_number = len(server_list.keys())    
uri = daemon.register(Worker) 
ns.register("Worker_" + str(worker_number), uri)   

print("Ready.")
daemon.requestLoop()    