#!/usr/bin/env python3
import json, datetime

FILE = "conversations.json"
DATE = datetime.datetime.now().strftime("%Y-%m-%d")
OUT = f"chat_full_restore_{DATE}.txt"

data = json.load(open(FILE))

sep = "\n" + "-"*80 + "\n"
output = []

def get_text(content):
    if not content:
        return ""
    # parts style
    if isinstance(content, dict) and "parts" in content:
        parts = content.get("parts", [])
        return "\n".join(p for p in parts if isinstance(p,str)).strip()
    # block style
    if isinstance(content, list):
        out = []
        for block in content:
            if block.get("type") == "text":
                out.append(block.get("text",""))
            if block.get("type") == "code":
                out.append(f"```{block.get('language','')}\n{block.get('text','')}\n```")
        return "\n".join(out).strip()
    return ""

def walk_mapping(mapping):
    # find root node
    roots = [k for k,v in mapping.items() if v.get("parent") is None]
    if not roots:
        roots = list(mapping.keys())[:1]
    msgs = []
    stack = roots[:]

    visited = set()
    while stack:
        node_id = stack.pop(0)
        if node_id in visited:
            continue
        visited.add(node_id)

        node = mapping.get(node_id,{})
        msg = node.get("message")
        if msg:
            role = (msg.get("author") or {}).get("role","unknown").upper()
            content = get_text(msg.get("content"))
            if content:
                msgs.append(f"{role}:\n{content}{sep}")

        for child in node.get("children",[]):
            stack.append(child)

    return msgs

for conv in data:
    title = conv.get("title","Untitled")
    mapping = conv.get("mapping",{})
    output.append(f"### {title} ###\n{sep}")
    msgs = walk_mapping(mapping)
    output.extend(msgs)

with open(OUT,"w",encoding="utf-8") as f:
    f.write("\n".join(output))

print(f"✅ Restored conversations: {len(data)}")
print(f"📄 Output file: {OUT}")
