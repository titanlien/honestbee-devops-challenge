#!/urs/bin/env python

import docker

client = docker.from_env()
containers = client.containers.list(filters={'status':'running'})


print "CONTAINER ID\t", "TAG\t\t", "UP TO DATE?\t"
for cont in containers:
    _id  = cont.attrs['Id'][:12]
    name, tag = cont.attrs['Config']['Image'].split(':')
    ## if we could not get tag, just assume it's latest
    if tag is None:
        ret = "FALSE\t"
        tag = "latest"
    elif tag == 'latest':
        ret = "FALSE\t"
    else:
        ret ="TRUE\t"
    print _id+"\t", tag+"\t\t", ret
