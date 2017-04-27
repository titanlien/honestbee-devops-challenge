#!/usr/bin/env python

import docker
import sys, requests, json

def pretty_print(d):
    print(json.dumps(d, indent=2))

def download_manifest_for_repo(repo, tag):
    """
    repo: string, repository (e.g. 'library/fedora')
    tag:  string, tag of the repository (e.g. 'latest')
    """
    login_template = "https://auth.docker.io/token?service=registry.docker.io&scope=repository:{repository}:pull"
    get_manifest_template = "https://registry.hub.docker.com/v2/{repository}/manifests/{tag}"

    response = requests.get(login_template.format(repository=repo), json=True)
    response_json = response.json()
    token = response_json["token"]
    response = requests.get(
        get_manifest_template.format(repository=repo, tag=tag),
        headers={"Authorization": "Bearer {}".format(token)},
        json=True
    )
    manifest = response.json()
    if not response.status_code == requests.codes.ok:
        pretty_print(dict(response.headers))
    #pretty_print(dict(response.headers))
    #pretty_print(dict(manifest))
    return manifest

def get_manifest(repos):
    if not repos:
        print("Usage: {} <[namespace/]repository[:tag]> [<[namespace/]repository[:tag]>...]".format(sys.argv[0]) +
              "\nExample: {} fedora:23".format(sys.argv[0]))
        raise 1
    for repo_tag in repos:
        if ":" in repo_tag:
            repo, tag = repo_tag.split(":")
        else:
            repo, tag = repo_tag, "latest"
        if "/" not in repo:
            repo = "library/" + "busybox"
        return download_manifest_for_repo(repo, tag)

def main():
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
      name = cont.attrs['Config']['Image']
    finally:
      image_id = cont.attrs['Image']
      manifest = get_manifest(name)
      pretty_print(manifest)

      #if image_id == header_id:
      #    ret = "FALSE"
      #else:
      #    ret ="TRUE"
      #print _id+"\t", tag+"\t", ret+"\t"

if __name__ == "__main__":
  sys.exit(main())
