# Distributed Web Crawler

## About
Since web crawling is a highly I/O intensive task that is embarrassingly parallelisable, we have developed a distributed web crawler that extends parallelism beyond threads into multiple machines connected over a network. Users can add as many worker nodes (servers) as required, even during runtime. It also supports multiple clients so that multiple users can interact and retrieve results simultaneously. It also supports the crawling of web apps as it uses the chromium web kit to render the page. The client can compute the PageRank from the dataset as well as retrieve individual pages for other purposes. Auto removal of non responding servers is also supported.

## Required External libraries
* Requests-HTML
* Pyro5
* Pyviz
* NetworkX

## Usage
To activate a virtual env with the above libraries, execute in each terminal:  
    `source project_env/bin/activate`

To start the nameserver, execute in a terminal:  
    `pyro5-ns`

To start workers, execute the follwing in as many seperate terminals as required:  
    `python3 worker.py`

To start client, execute the follwing in a seperate terminal:  
    `python3 master.py`

## Supported Queries:
* seed seed_url n
  - Crawl the urls present in the seed_url page uptill depth n.
  - Eg: `seed https://iiit.ac.in 2`
      Scrapes all the urls till depth 2 from `iiit.ac.in`(which is at depth 0).
* update url
  - Updates the adjacency list of the url in all worker nodes
  - Eg: `update https://iiit.ac.in`
* graph root_url depth
  - Saves the graph showing the pages linked to from root_url till given depth as 'graph.html' and opens it in browser. 
  - Eg: `graph https://iiit.ac.in 2`
* pagerank
  - Calculates the pagerank of whole graph and saves it in 'ppagerank.json'
  - It also supports a flag --graph which generates a graph with the pagerank indicated by the size of the node.
  - Eg: `pagerank`
* getpage url
  - Retrieves the html of the page from the worker and save it as 'page.html'
  - Eg: `getpage https://iiit.ac.in`
* quit
  - shutdowns the client
  - user can also use ctrl-d to exit
  - Eg: quit

## Connecting over internet
The clients and servers are connected to each other with the unique address provided by the nameserver. The nameserver's address need not be fixed when all the machines are on the same local network since the name server responds to a broadcast lookup. However if you want to connect over the internet, you will need to intialize with a fixed hostname or ip address and port number by  
`pyro5-ns -h ip_address -p port_number`  
We must also setup port forwarding in our router and allow access through any firewalls. Try using `telnet` to check if the port is visible from the other computer. This IP address must then be hardcoded in the workers and client replacing the ns.lookup() function. (See comment in code).

## Team SpaceBar
* Adarsh Dharmadevan
* Apoorva Thirupathi
* Gadela Keshav
* Guru Ravi Shanker
* Joseph Cherukara
