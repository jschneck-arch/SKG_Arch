#!/usr/bin/env python3
import sys,json,os
STATE="/var/lib/skg/state.json"
def load_state():
    try: return json.load(open(STATE))
    except: return {}
def save_state(st): json.dump(st,open(STATE,"w"),indent=2)
def main():
    if len(sys.argv)!=4:
        print("usage: skg lfo <amp0..1> <freqHz> <phiRadians>"); sys.exit(2)
    amp,freq,phi=map(float,sys.argv[1:4])
    st=load_state(); st.setdefault("lfo",{})["reflect"]={"amp":amp,"freq":freq,"phi":phi}
    save_state(st)
    print(json.dumps({"ok":True,"lfo":st["lfo"]["reflect"]}))
if __name__=="__main__": main()
