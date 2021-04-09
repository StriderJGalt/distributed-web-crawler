import Pyro5.api 
from sys import stdin
from pyvis.network import Network
import threading


MIN_URL_LIMIT = 20


lock = threading.Lock()
scraped_urls = set()
adjacency_list = {}
worker_uris = []
next_level_urls = set()

def scrape(worker_uri,urls):
    print("scraping")
    print(urls)
    child_dict = {}
    try:
        worker = Pyro5.client.Proxy(worker_uri)
        child_dict, error_urls = worker.scrape(urls)
    except:
        print("".join(Pyro5.errors.get_pyro_traceback()))
        error_urls = urls
        worker_uris.remove(worker_uri)
    print("child_dict = {}".format(child_dict))
    lock.acquire()
    for parent_url in child_dict.keys():
        child_urls = child_dict[parent_url]
        scraped_urls.add(parent_url)
        if child_urls:
            adjacency_list[parent_url] = child_urls
            next_level_urls.update(child_urls)
    print("next_level_urls = {}".format(next_level_urls))
    lock.release()

def process(line):

    # get worker nodes
    ns = Pyro5.api.locate_ns()
    server_list = ns.list()
    worker_uris = []
    for server in server_list:
        if server != 'Pyro.NameServer':
            try:
                worker = Pyro5.client.Proxy(server_list[server])
                if worker.test():
                    worker_uris.append(server_list[server])
            except:
                pass
    if not worker_uris:
        print("No workers detected")
        return
    print(worker_uris)

    ls = line.split()

    if ls[0] == 'seed':
        if len(ls) != 3:
            print("Error: invalid number of arguments!")
            print("Usage: seed seed_url depth_pages_to_be_scraped")
            return

        scrape_depth = int(ls[2])
        urls_to_be_scraped = {ls[1]}
        next_level_urls.clear()

        for l in range(scrape_depth):

            # print("urls_to_be_scraped = {}".format(urls_to_be_scraped))
            # remove already scraped urls and add their children
            urls_to_be_scraped_list = list(urls_to_be_scraped)
            for url in urls_to_be_scraped_list:
                if url in scraped_urls:
                    urls_to_be_scraped.remove(url)
                    next_level_urls.update(adjacency_list[url])

            
            # scrape the urls using the workers
            num_urls_per_worker = max(
                (len(urls_to_be_scraped)//len(worker_uris))+1,
                MIN_URL_LIMIT)
            worker_index = 0
            threads = {}
            while urls_to_be_scraped:
                urls = []
                for i in range(min(len(urls_to_be_scraped),
                               num_urls_per_worker)):
                    urls.append(urls_to_be_scraped.pop())
                threads[worker_index] = threading.Thread(
                    target=scrape, args=(worker_uris[worker_index],urls))
                threads[worker_index].start()
                worker_index += 1
            for i in range(worker_index):
                threads[i].join()

            # have to write code to handle error urls

            # loading next level of urls to be scraped
            urls_to_be_scraped = next_level_urls.copy()
        
        print("DONE")
        return

    if ls[0] == 'graph':
        net = Network()
        net.add_nodes(scraped_urls)
        for x in adjacency_list.keys():
            for y in adjacency_list[x]:
                net.add_node(y) #since error urls are not handled rn
                net.add_edge(x,y)
        # net.enable_physics(False)
        if len(ls)>1:
            if ls[1] == "-s":
                net.show_buttons()
            else:
                print("Command not supported")
                return
        net.show("graph.html")
        print("DONE")        
        return

    if ls[0] == 'update':
        url = ls[1]
        if url not in scraped_urls:
            print("Given url has not been scraped yet")
            print("please use seed command instead")
            return
        worker = Pyro5.client.Proxy(worker_uris[0])
        child_urls, error_urls = workers.scrape([url])
        adjacency_list[url].update(child_urls[url])
        print("DONE")
        return

    if ls[0] == 'print':
        print(adjacency_list)

    else:
        print("Command not supported")
        return


if __name__ == '__main__':
    for line in stdin:
        if line == '\n':
            continue
        if line == '' or line == 'quit\n': 
            break
        process(line) 
    
   
