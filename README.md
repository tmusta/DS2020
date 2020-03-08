# DS2020

Course project for distributed systems - course by Toni Musta. 

Volunteered algorithms

Pre-requisities:
docker

How to run:
1. Start docker daemon `sudo dockerd`
2. `git clone https://github.com/tmusta/DS2020`
3. `cd DS2020`
4. Start docker-composer `sudo docker-compose up`
5. To run a node: 
5.1. Open a new terminal
5.2 Run `docker exec -ti DS2020_genalg.com_1 bash` or `docker exec -ti DS2020_node1_1 bash` or `docker exec -ti DS2020_node2_1 bash`
5.3 Inside the container `cd code && python3 net.py`
