#### How SSL Support Works


The default behavior for the proxy when port 80 and 443 are exposed is as follows:

* If a container has a usable cert, port 80 will redirect to 443 for that container so that HTTPS is always preferred when available.
* If the container does not have a usable cert, a 503 will be returned.

Note that in the latter case, a browser may get an connection error as no certificate is available
to establish a connection.  A self-signed or generic cert named `default.crt` and `default.key`
will allow a client browser to make a SSL connection (likely w/ a warning) and subsequently receive
a 500.

To serve traffic in both SSL and non-SSL modes without redirecting to SSL, you can include the
environment variable `HTTPS_METHOD=noredirect` (the default is `HTTPS_METHOD=redirect`).  You can also
disable the non-SSL site entirely with `HTTPS_METHOD=nohttp`, or disable the HTTPS site with 
`HTTPS_METHOD=nohttps`. `HTTPS_METHOD` must be specified on each container for which you want to 
override the default behavior.  If `HTTPS_METHOD=noredirect` is used, Strict Transport Security (HSTS) 
is disabled to prevent HTTPS users from being redirected by the client.  If you cannot get to the HTTP 
site after changing this setting, your browser has probably cached the HSTS policy and is automatically 
redirecting you back to HTTPS.  You will need to clear your browser's HSTS cache or use an incognito 
window / different browser.

## How does it work

The system consists of 4 main parts:

* Main Nginx reverse proxy container.
* Container that generates the main Nginx config based on container metadata.
* Container that automatically handles the acquisition and renewal of Let's Encrypt TLS certificates.
* The actual websites living in their own containers. In this example, a very simple website, talking to a very simple API.

### The main Nginx reverse proxy container
This is the only publicly exposed container, routes traffic to the backend servers and provides TLS termination.

Uses the official [nginx](https://hub.docker.com/_/nginx/) Docker image.

It is defined in `docker-compose.yml` under the **nginx** service block:

```
services:
  nginx:
    restart: always
    image: nginx:1.11.13-alpine
    container_name: nginx
    ports:
      - "80:80/tcp"
      - "443:443/tcp"
    depends_on:
      - whoami
    volumes:
      - "/etc/nginx/conf.d"
      - "/etc/nginx/vhost.d"
      - "/usr/share/nginx/html"
      - "./volumes/proxy/certs:/etc/nginx/certs:ro"
```

As you can see it shares a few volumes:
* Configuration folder: used by the container that generates the configuration file.
* Default Nginx root folder: used by the Let's Encrypt container for challenges from the CA. 
* Certificates folder: written to by the Let's Encrypt container, this is where the TLS certificates are maintained. 

### The configuration generator container
This container inspects the other running containers and based on their metadata (like **VIRTUAL_HOST** environment variable) and a template file it generates the Nginx configuration file for the main Nginx container. When a new container is spinning up this container detects that, generates the appropriate configuration entries and restarts Nginx. 

Uses the [jwilder/docker-gen](https://hub.docker.com/r/jwilder/docker-gen/) Docker image.

It is defined in `docker-compose.yml` under the **nginx-gen** service block:

```
services:
  ...

  dockergen:
    image: jwilder/docker-gen
    container_name: dockergen
    command: -notify-sighup nginx -watch -wait 5s:30s /etc/docker-gen/templates/nginx.tmpl /etc/nginx/conf.d/default.conf
    volumes_from:
      - nginx
    volumes:
      - "/var/run/docker.sock:/tmp/docker.sock:ro"
      - "./nginx.tmpl:/etc/docker-gen/templates/nginx.tmpl:ro"
```

The container reads the `nginx.tmpl` template file (source: [jwilder/nginx-proxy](https://github.com/jwilder/nginx-proxy)) via a volume shared with the host.

It also mounts the Docker socket into the container in order to be able to inspect the other containers (the `"/var/run/docker.sock:/tmp/docker.sock:ro"` line). 
**Security warning**: mounting the Docker socket is usually discouraged because the container getting (even read-only) access to it can get root access to the host. In our case, this container is not exposed to the world so if you trust the code running inside it the risks are probably fairly low. But definitely something to take into account. See e.g. [The Dangers of Docker.sock](https://raesene.github.io/blog/2016/03/06/The-Dangers-Of-Docker.sock/) for further details.

NOTE: it would be preferrable to have docker-gen only handle containers with exposed ports (via `-only-exposed` flag in the `entrypoint` script above) but currently that does not work, see e.g. <https://github.com/jwilder/nginx-proxy/issues/438>.

### The Let's Encrypt container
This container also inspects the other containers and acquires Let's Encrypt TLS certificates based on the **LETSENCRYPT_HOST** and **LETSENCRYPT_EMAIL** environment variables. At regular intervals it checks and renews certificates as needed. 

Uses the [jrcs/letsencrypt-nginx-proxy-companion](https://hub.docker.com/r/jrcs/letsencrypt-nginx-proxy-companion/) Docker image.

It is defined in `docker-compose.yml` under the **letsencrypt-nginx-proxy-companion** service block:

```
services:
  ...

    letsencrypt-nginx-proxy-companion:
    restart: always
    image: jrcs/letsencrypt-nginx-proxy-companion
    container_name: letsencrypt-nginx-proxy-companion
    depends_on:
      - dockergen
    volumes_from:
      - nginx
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock:ro"
      - "./volumes/proxy/certs:/etc/nginx/certs:rw"
    environment:
      - NGINX_DOCKER_GEN_CONTAINER=dockergen

```

The container uses a volume shared with the host and the Nginx container to maintain the certificates.

It also mounts the Docker socket in order to inspect the other containers. See the security warning above in the docker-gen section about the risks of that.

### The whoami website 

Simple HTTP docker service that prints it's container ID

    $ docker run -d -p 8000:8000 --name whoami -t jwilder/whoami
    736ab83847bb12dddd8b09969433f3a02d64d5b0be48f7a5c59a594e3a6a3541
    
    $ curl $(hostname --all-ip-addresses | awk '{print $1}'):8000
    I'm 736ab83847bb


```
services:
  ...

    whoami:
    restart: always
    image: jwilder/whoami
    container_name: whoami
    environment:
      - VIRTUAL_HOST=whoami.com
      - VIRTUAL_PORT=8000
      - LETSENCRYPT_HOST=whoami.com
      - LETSENCRYPT_EMAIL=email@gmail.com

```
The important part here are the environment variables. These are used by the config generator and certificate maintainer containers to set up the system.
