import requests
import json
import re
import os
from subprocess import call

#your github user credentials.
u='yourusername'
p='yourpassword'

# where to store your repositories locally (absolute path plz!). Create the directory if needed.
myrepos='~/myrepos'
if (os.path.isdir(myrepos) == False):
    call("mkdir -p " + myrepos, shell=True)

# a list of your organisations.
orgs = ['listof', 'your', 'organisations']

# headers sent to the github api.
headers = {'Content-type': 'application/x-www-form-urlencoded', 'Accept': 'application/json', }

# a list to store repositories in.
repos = []

# a regular expression used to follow the link to more repositores if an organisation has more than 25 repositories.
preg = re.compile('<(https://.+)>;\s*rel="(next)"')

# helper function that is recursive for performing the actual fetching of github api data.
def fetch (url, repos):
    r = requests.get(url, auth=(u, p), headers=headers)
    repos = repos + r.json
    if r.headers['link'] is not None:
        m = preg.match(r.headers['link'])
        if m is not None and m.group(2) == 'next':
            repos = fetch (m.group(1), repos)

    return repos


# perform request to github api and save the repositories to an array.
for org in orgs:
    url = 'https://api.github.com/orgs/%s/repos' % (org)
    repos = fetch (url, repos)

# loop through the array of repos and either clone them locally, 
# or if they exist run git pull on each and every one of them.
for repo in repos:
    if (os.path.isdir( repo['full_name'] + '/.git')):
        # go into each directory and run git pull.
        call("cd " + myrepos + "/" + repo['full_name'] + " && git pull", shell=True)
    else: 
        # run git clone if the repository doesn't exist.
        fetchurl = 'git clone ' + repo['ssh_url'] + ' ' + repo['full_name']
        call("cd " + myrepos + " && " + fetchurl, shell=True)
