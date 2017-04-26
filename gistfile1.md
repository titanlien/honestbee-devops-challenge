# Part 1 - Docker and common architectures
Write a docker-compose file to simulate load balancer TLS termination.
You can use dockerfiles that you wrote yourself or just pull directly from Docker hub.

Architecture:
- nginx container with TLS certificates, serving on https.
- hello world backend in the language of your choice, serving on http.

Please take security into account, however it is fine if the certificates are self-signed and the browser displays a warning.

# Part 2 - Tooling
Write a tool in python, ruby or go that checks that for each Docker container running on a machine, it is running the last version of its tag. 

Example output : 
```
CONTAINER ID    TAG     UP TO DATE?
cedab5d579e2    1.7     TRUE
db620dfb3d80    latest  FALSE
```
