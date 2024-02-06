import json

with open("file-cucm.json") as f:
    data = json.load(f)
for cluster in data['CUCMCluster']:
    for nodes in cluster.values():
        uname = nodes['Username']
        node = nodes['nodes']
        # print(uname)
        for ipadd in node:
            # print(uname)
            # print(ipadd)
            # print("Connecting to:" + (ipadd))
            print((uname) + (ipadd))
