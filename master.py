import Pyro5.api 
from sys import stdin

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
        child_urls, error_urls = workers[0].scrape([ls[1]]) #remember input is list of urls not url
        print("child urls")
        print(child_urls)
        print("could not scrape follwing urls")
        print(error_urls)

    # if ls[0] == 'print':
        
    # if ls[0] == 'update':

if __name__ == '__main__':
    for line in stdin:
        if line == '' or line == 'quit': # If empty string is read then stop the loop
            break
        process(line) # perform some operation(s) on given string
    
   