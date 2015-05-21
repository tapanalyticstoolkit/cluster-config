from atk_config import cdh
import hashlib, re, time, argparse, os, time, sys, getpass
from pprint import pprint

parser = argparse.ArgumentParser(description="Process cl arguments to avoid prompts in automation")
parser.add_argument("--host", type=str, help="Cloudera Manager Host", default="127.0.0.1")
parser.add_argument("--port", type=int, help="Cloudera Manager Port", default=7180)
parser.add_argument("--username", type=str, help="Cloudera Manager User Name", default="admin")
parser.add_argument("--password", type=str, help="Cloudera Manager Password", default="admin")
parser.add_argument("--cluster", type=str, help="Cloudera Manager Cluster Name if more than one cluster is managed by "
                                                "Cloudera Manager.", default="cluster")
args = parser.parse_args()

cluster = cdh.Cluster(args.host, args.port, args.username, args.password, args.cluster)

def pick(parentService, childService, parentServiceName, serviceList):
    print("Available {0} types on {1}: '{2}'".format(childService, parentService,parentServiceName))
    print("Pick a {0}".format(childService))
    count = 0
    list = []
    for service in serviceList:
        print("Id {0} {1}: {2}".format(count+1, childService, service))
        list.append(service)
        count += 1
    service_index = input("Enter {0} Id : ".format(childService))
    if service_index <= 0 or service_index > len(cluster.services):
        raise Exception("Not a valid {0} Id".format(childService))
    service_index -= 1
    return list[service_index]


"""
print("Available service types on cluster: '{0}'".format(cluster.cluster.name))
print("Pick a service")
count = 0
for service in cluster.services:
    print("Id {0} service: {1}".format(count+1, service))
    count += 1
service_index = input("Enter service Id : ")
if service_index <= 0 or service_index > len(cluster.services):
    raise Exception("Not a valid service Id")

service_index -= 1
"""

service_index = pick("cluster", "service", cluster.clusterName, cluster.services)
print service_index

pprint(cluster.services[service_index].roles)
role_index = pick("service", "role", service_index, cluster.services[service_index].roles)
print role_index

configGroup_index = pick("role", "config group", role_index, cluster.services[service_index].roles[role_index].configGroups)
print configGroup_index

config_index = pick("config group", "config", configGroup_index, cluster.services[service_index].roles[role_index].configGroups[configGroup_index].configs)
print config_index