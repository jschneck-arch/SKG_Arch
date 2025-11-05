import sys, json, time
from skg.governance import append_event
PHASE="/var/lib/skg/memory/phase.current"
def set_phase(name):
    open(PHASE,"w").write(name+"\n")
    append_event({"actor":"cli","type":"phase","value":name,"ts":time.time()})
    return {"ok":True,"phase":name}
if __name__=="__main__":
    print(json.dumps(set_phase(sys.argv[1]) if len(sys.argv)>1 else {"usage":"phase <name>"}))
