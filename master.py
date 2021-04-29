import Pyro5.api 
from sys import stdin
from pyvis.network import Network
import networkx as nx


    
def get_workers():
    # get worker nodes
    ns = Pyro5.api.locate_ns()
    server_list = ns.list()
    del server_list['Pyro.NameServer']
    workers = []
    for server in server_list:
        try:
            worker = Pyro5.client.Proxy(server_list[server])
            if worker.test():
                workers.append(worker)
        except:
            pass
    if not workers:
        exit("No workers detected")
    return workers
    # print(worker_uris)


def get_list(rooturl,depth):
    workers = get_workers()
    adjacency_list = {}
    urls = [rooturl]
    for n in range(depth):
        child_dict = {}
        for worker in workers:
            child_dict.update(worker.get(urls))
        adjacency_list.update(child_dict)
        urls = set()
        for s in child_dict.values():
            urls.update(s)
    return adjacency_list

def get_graph():
    workers = get_workers()
    adjacency_list = {}
    for worker in workers:
        adjacency_list.update(worker.ret())
    return adjacency_list

def retval(workers):
    while 1:
        f = 0
        for worker in workers:
            print(worker.val())
            if worker.val() != 0:
                f = 1
        if f == 0:
            break
        sleep(1)

    return


def process(line):
    ls = line.split()

    if ls[0] == 'seed':
        if len(ls) != 3:
            print("Error: invalid number of arguments!")
            print("Usage: seed seed_url depth_pages_to_be_scraped")
            return

        workers = get_workers()
        print(workers)
        workers[0].crawl([ls[1]], int(ls[2]))
        # retval(workers)
        print("DONE")
        return

    if ls[0] == 'graph':
        if len(ls) != 3:
            print("Error: invalid number of arguments!")
            print("Usage: graph seed_url depth_pages_to_be_displayed")

        adjacency_list = get_list(ls[1], int(ls[2]))
        net = Network()
        for x in adjacency_list.keys():
            net.add_node(x) 
            for y in adjacency_list[x]:
                net.add_node(y) 
                net.add_edge(x,y)
        # net.enable_physics(False)
        net.show_buttons()
        net.show("graph.html")
        print("DONE")        
        return

    if ls[0] == 'update':
        if len(ls) != 2:
            print("Error: invalid number of arguments!")
            print("Usage: update url")
            return

        url = ls[1]
        # if url not in scraped_urls:
        #     print("Given url has not been scraped yet")
        #     print("please use seed command instead")
        #     return

        workers = get_workers()
        for worker in workers:
            worker.upd(url)
            break
        print("DONE")
        return

    if ls[0] == 'pagerank':
        if len(ls) != 1:
            print("Error: invalid number of arguments!")
            print("Usage: pagerank")
            return

        G = nx.DiGraph()
        adjacency_list = get_graph()
        for x in adjacency_list.keys():
            if x not in G:
                G.add_node(x) 
            for y in adjacency_list[x]:
                if y not in G:
                    G.add_node(y) 
                if G.has_edge(x, y) == 0:
                    G.add_edge(x,y)
        
        pr = nx.pagerank(G)
        print(pr)
        print("DONE")
        return


    if ls[0] == 'print':
        workers = get_workers()
        print(workers[0].get([ls[1]], ls[2]))

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
    
   
