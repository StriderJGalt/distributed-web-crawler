import Pyro5.api 
from sys import stdin
import networkx as nx 
import matplotlib.pyplot as plt 
import multiprocessing
import threading 

lock = threading.Lock()

G = nx.DiGraph() 
urls_done = set()
adj_graph = {}
temp = []

def scraping_function(i, urls):
    ns = Pyro5.api.locate_ns()
    server_list = ns.list()
    worker_uris = []

    for server in server_list:
        if server != 'Pyro.NameServer':
            worker_uris.append(server_list[server])
    workers = [Pyro5.client.Proxy(uri) for uri in worker_uris]

    child_urls, error_urls = workers[i].scrape(urls)
    lock.acquire()
    
    for url in child_urls:
        urls_done.add(url)
    for url in child_urls:
        adj_graph[url] = set()
        for i in child_urls[url]:
            if i not in adj_graph[url]:
                adj_graph[url].add(i)

    for a in child_urls:
        temp.extend(child_urls[a])

    lock.release()


def process(line):
    # get worker nodes
    ns = Pyro5.api.locate_ns()
    server_list = ns.list()
    worker_uris = []
    for server in server_list:
        if server != 'Pyro.NameServer':
            worker_uris.append(server_list[server])
    workers = [Pyro5.client.Proxy(uri) for uri in worker_uris]
    # process_pool = multiprocessing.Pool(len(workers))
    # parse and process line
    ls = line.split()
    if ls[0] == 'seed':
        # below code is for test purpose only
        if ls[1] in urls_done:
            print("The given URL has already been scraped")
            return
        n = int(ls[2])
        urls = [ls[1]]
        while n:
            n -= 1
            for url in urls:
                if url in urls_done:
                    urls.remove(url)
                    continue

            dist = len(urls)//len(workers)
            print(dist, len(urls))
            if dist > 0:
                temp = []
                threads = []
                for i in range(len(workers)):
                    t = threading.Thread(target=scraping_function, args=(i, urls[i * dist: min(dist * (i + 1), len(urls))]))
                    threads.append(t)
                    t.start()

                for i in range(1,len(threads)):
                    threads[i].join()

            else:
                print("dsadsadasd")
                child_urls, error_urls = workers[0].scrape(urls)
                for url in urls:
                    urls_done.add(url)
                for url in child_urls:
                    adj_graph[url] = set()
                    for i in child_urls[url]:
                        if i not in adj_graph[url]:
                            adj_graph[url].add(i)
                temp = []
                for a in child_urls:
                    temp.extend(child_urls[a])
                print(temp)
            urls = temp


            # G.add_node(ls[1])
            # for url in child_urls:
            #     adj_graph[url] = set()
            #     for i in child_urls[url]:
            #         if i not in adj_graph[url]:
            #             adj_graph[url].add(i)

                    # G.add_node(i)
                    # G.add_edge(url, i)

            # temp = []
            # for a in child_urls:
            #     temp.extend(child_urls[a])
            # urls = temp

    if ls[0] == 'print':
        nx.draw(G,with_labels=True) 
        plt.show()
        print(adj_graph)
        if ls[1] in adj_graph:
            print(adj_graph[ls[1]])
        else:
            print("The URL has not been scraped")

    if ls[0] == 'update':
        child_urls, error_urls = workers[0].scrape([ls[1]]) #remember input is list of urls not url
        if ls[1] not in urls_done:
            urls_done.add(ls[1])
        adj_graph[ls[1]] = set()
        for i in child_urls[ls[1]]:
            if i not in adj_graph[ls[1]]:
                adj_graph[ls[1]].add(i)


if __name__ == '__main__':
    for line in stdin:
        if line == '' or line == 'quit': # If empty string is read then stop the loop
            break
        process(line) # perform some operation(s) on given string


