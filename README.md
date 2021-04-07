# DistributedWebCrawler

It consists of a master process as well as various workers. The master when given a seed URL it will crawl all linked pages upto a to a given depth n and display the connectivity graph. It will also calculate the page rank for each page.

## Required libraries
* BeautifulSoup4
* Requests
* Pyro5
* Pyviz

## Usage
To activate virtual env with the above libraries, execute in each terminal
    `source project_env/bin/activate`

To start nameserver, execute in a terminal
    `pyro5-ns`

To start workers, execute the follwing in as many seperate terminals as required
    `python3 worker.py`

To start master, execute the follwing in a seperate terminal
    `python3 master.py`

Currently supported queries:
* seed url_of_root_page n
  - Srapes the urls present in the url_of_root_page uptill depth n with respect to bfs.
  Eg: `seed https://iiit.ac.in 2`
      Scrapes all the urls till depth 2 from `iiit.ac.in` url(at depth 1).
* graph [-s]
  - Saves the graph to specified file and open in browser. Use -s flag if u need to view graph settings.
  Eg: `graph -s`
* update url
  - Updates the adjacency list of the url
  Eg: `update https://iiit.ac.in`


use ctrl-d to exit

## Team SpaceBar
* Adarsh Dharmadevan
* Apoorva Thirupathi
* Gadela Keshav
* Guru Ravi Shanker
* Joseph Cherukara
