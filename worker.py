import Pyro5.api
from requests_html import HTMLSession


@Pyro5.api.expose
@Pyro5.api.behavior(instance_mode="single")
class Worker:
    def __init__(self):
        self.pages = {}
        self.session = HTMLSession()

    def scrape(self,url_list):
        child_urls = {}
        error_urls = []
        for url in url_list:
            try:
                r = self.session.get(url)
                withoutrender = r.html.absolute_links
                # r.html.render()
                withrender = r.html.absolute_links
                child_urls[url] = withoutrender.union(withrender)
                self.pages[url] = r.html
            except:
                error_urls.append(url)
        # print("child URLs")
        # print(child_urls)
        # print("error URLs")
        # print(error_urls)
        return child_urls, error_urls

    def get_pages(self,urls):
        return { url: self.pages[url] for url in urls }

    def test(self):
        return True


# testing
# w = Worker()
# print(w.scrape(["https://open.spotify.com/"]))

   

daemon = Pyro5.server.Daemon()         
ns = Pyro5.api.locate_ns()     
server_list = ns.list()
worker_number = len(server_list.keys())    
uri = daemon.register(Worker) 
ns.register("Worker_" + str(worker_number), uri)   

print("Ready.")
daemon.requestLoop()    