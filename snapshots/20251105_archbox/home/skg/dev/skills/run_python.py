#!/usr/bin/env python3
import time
from skg.governance import append_event
SAFE_BUILTINS = {"len":len,"range":range,"min":min,"max":max,"sum":sum,"sorted":sorted,"abs":abs,"print":print}
def run(**params):
    code=params.get("code","")
    if not code: return {"ok":False,"error":"code required"}
    loc={}
    try:
        exec(compile(code,"<skg_py>","exec"), {"__builtins__":SAFE_BUILTINS}, loc)
        append_event({"actor":"runner.python","type":"exec","keys":list(loc.keys())})
        return {"ok":True,"locals":{k:str(type(v).__name__) for k,v in list(loc.items())[:50]}}
    except Exception as e:
        append_event({"actor":"runner.python","type":"error","error":str(e)})
        return {"ok":False,"error":str(e)}
