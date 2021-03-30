import Pyro5.api 
from sys import stdin

urls_done = set()
adj_graph = {}

def process(line):
    # get worker nodes
    ns = Pyro5.api.locate_ns()
    server_list = ns.list()
    worker_uris = []
    for server in server_list:
        if server != 'Pyro.NameServer':
            worker_uris.append(server_list[server])
    workers = [Pyro5.client.Proxy(uri) for uri in worker_uris]

    # parse and process line
    ls = line.split()
    if ls[0] == 'seed':
        # below code is for test purpose only
        if ls[1] in urls_done:
            print("The given URL has already been scraped")
            return
        child_urls, error_urls = workers[0].scrape([ls[1]]) #remember input is list of urls not url

        urls_done.add(ls[1])
        adj_graph[ls[1]] = set()
        for i in child_urls[ls[1]]:
            if i not in adj_graph[ls[1]]:
                adj_graph[ls[1]].add(i)

    if ls[0] == 'print':
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
    
   