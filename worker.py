import Pyro5.api
import multiprocessing as mp
import threading
from requests_html import HTMLSession

MIN_URL_LIMIT = 20

worker_number = -1

def get_other_workers():
    # get worker nodes
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
    # print(workers)


@Pyro5.api.expose
@Pyro5.api.behavior(instance_mode="single")
class Worker:
    def __init__(self):
        self.pages = {}
        self.adjacency_list = {}
        self.worker_incharge = {}
        self._lock = threading.Lock()
    
    def test(self):
        return True

    def scrape(self,url_list):
        session = HTMLSession()
        child_urls = {}
        error_urls = []
        for url in url_list:
            try:
                r = session.get(url)
                withoutrender = r.html.absolute_links
                # r.html.render()
                withrender = r.html.absolute_links
                child_urls[url] = withoutrender.union(withrender)
                with self._lock:
                    self.pages[url] = r.html
            except:
                error_urls.append(url)
        print("child URLs")
        print(child_urls)
        print("error URLs")
        print(error_urls)
        return child_urls, error_urls

    def get_pages(self,url):
        return self.pages[url]
        # return { url: self.pages[url] for url in urls }

    def remove_duplicates(self,urls):
        # with self._lock:
        # already_processed_urls = list(self.adjacency_list.keys())
        # print(urls)
        new_urls = []
        for url in urls:
            if url not in self.adjacency_list.keys():
                new_urls.append(url)
        return new_urls

    @Pyro5.server.oneway
    def crawl(self,urls, depth):
        while True:
            print("crawling depth {}".format(depth))
            # remove already scraped urls
            urls = self.remove_duplicates(urls)
            # scrape
            cu, eu = self.scrape(urls)
            # update adjacency list
            with self._lock:
                self.adjacency_list.update(cu)
            # print('al')
            # print(self.adjacency_list)
            # collect after removing already scraped urls from child urls
            urls_to_be_crawled = []
            for url in cu.keys():
                urls_to_be_crawled += self.remove_duplicates(cu[url])
            # print('child urls to be crawled')
            # print(urls_to_be_crawled)
            # return if crawl depth is satisfied
            if depth == 1:
                print("returning")
                return
            # distribute child urls to other workers
            workers = get_other_workers()
            # print("other workers")
            # print(workers)
            num_urls_per_worker = max(
                (len(urls_to_be_crawled)//(len(workers)+1))+1,
                MIN_URL_LIMIT)
            # print('num_urls_per_worker')
            # print(num_urls_per_worker)
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
        
# @Pyro5.api.expose
# @Pyro5.api.behavior(instance_mode="single")
# class Server:
#     def __init__(self):
#         self.job_queue = mp.Queue()
#         self.worker = Worker()

#     def test(self):
#         return True
   
#     def seed(self,urls, depth):
#         self.job_queue.put(('CRAWL',urls,depth))
#         return True

daemon = Pyro5.server.Daemon()         
ns = Pyro5.api.locate_ns()     
server_list = ns.list()
worker_number = len(server_list.keys())    
uri = daemon.register(Worker) 
ns.register("Worker_" + str(worker_number), uri)   

print("Ready.")
daemon.requestLoop()    