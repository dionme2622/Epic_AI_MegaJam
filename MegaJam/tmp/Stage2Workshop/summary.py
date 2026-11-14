import json
a=json.load(open("tmp/Stage2Workshop/audit.json",encoding="utf8"))
print("actors",len(a))
for r in a:
 print("{:39} {:27} {:23} ext {:19} folder {} {}".format(r["label"],r["class"],str([round(x) for x in r["location"]]),str([round(x) for x in r["extent"]]),r["folder"]," | ".join(m["name"]+":"+str(m["mesh"]).split("/")[-1] for m in r["meshes"][:4])))
