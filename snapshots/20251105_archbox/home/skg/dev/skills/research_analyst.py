#!/usr/bin/env python3
"""Skill: research_analyst – summarize and correlate local recon or research data."""
import os, json, time, re, xml.etree.ElementTree as ET
from pathlib import Path
from skg.governance import append_event
from skg.learn_vault import append as vault_append

def _parse_text(file_path):
    """Simple parser for text-based recon outputs."""
    findings = []
    with open(file_path, errors="ignore") as f:
        for line in f:
            # Example: capture IPs, domains, CVE patterns
            ips = re.findall(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", line)
            domains = re.findall(r"\b[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b", line)
            cves = re.findall(r"CVE-\d{4}-\d+", line)
            for val in ips + domains + cves:
                findings.append(val)
    return findings

def _parse_nmap_xml(file_path):
    """Parse Nmap XML for open ports and services."""
    results = []
    try:
        tree = ET.parse(file_path)
        for host in tree.findall("host"):
            addr = host.find("address").attrib.get("addr")
            for port in host.findall(".//port"):
                num = port.attrib.get("portid")
                state = port.find("state").attrib.get("state")
                svc = port.find("service")
                svcname = svc.attrib.get("name") if svc is not None else "unknown"
                results.append(f"{addr}:{num}/{state}/{svcname}")
    except Exception as e:
        results.append(f"[parse error: {e}]")
    return results

def run(**params):
    """Main entrypoint: run via API or CLI."""
    directory = params.get("path", "/home/skg/recon")
    summary = {"ts": time.time(), "directory": directory, "files": 0, "findings": []}
    for root, _, files in os.walk(directory):
        for f in files:
            path = Path(root) / f
            if f.endswith(".xml"):
                data = _parse_nmap_xml(path)
            else:
                data = _parse_text(path)
            summary["files"] += 1
            summary["findings"].extend(data)
    summary["unique_findings"] = sorted(set(summary["findings"]))
    append_event({"actor": "research_analyst", "type": "analysis",
                  "count": len(summary["unique_findings"]),
                  "directory": directory})
    vault_append({"actor": "research_analyst", "summary": summary})
    return {"ok": True, "files": summary["files"],
            "unique_findings": len(summary["unique_findings"])}

