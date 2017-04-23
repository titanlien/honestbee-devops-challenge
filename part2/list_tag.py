#!/urs/bin/env python

import docker

client = docker.from_env()
containers = client.containers.list(filters={'status':'running'})


print "CONTAINER ID\t", "TAG\t", "UP TO DATE?\t"
for cont in containers:
    _id  = cont.attrs['Id'][:12]
    try:
      name, tag = cont.attrs['Config']['Image'].split(':')
      ## if we could not get tag, just assume it's latest
    except ValueError:
      tag = "latest"
    if tag == 'latest':
        ret = "FALSE"
    else:
        ret ="TRUE"
    print _id+"\t", tag+"\t", ret+"\t"
