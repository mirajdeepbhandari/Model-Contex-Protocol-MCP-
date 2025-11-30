import time
import json
import os
import re

LOG_FILE = r"C:\Users\I1000929\AppData\Roaming\Claude\logs\mcp.log"

CLEAN_PATTERN = re.compile(
    r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z\s+\[info\]\s+\[.*?\]\s*",
    re.IGNORECASE
)
ANSI_PATTERN = re.compile(r'\x1b\[[0-9;]*m')

IGNORE_LINES = [
    "Shutting down server...",
    "Client transport closed",
    "Server transport closed",
    "Server transport closed (intentional shutdown)"
]

IGNORE_STARTUP_LINES = [
    "Initializing server...",
    "args: [",
    "'run',",
    "'--directory',",
    "'fastmcp',",
    "'run',",
    "'server.py',",
    "[length]: 6",
    "'],",
    "paths: [",
    "'',",
    "[length]: 26",
    "]",
    "}",
    "Server started and connected successfully",
    "Using MCP server command:"
]

def clean_line(line):
    line = CLEAN_PATTERN.sub("", line)
    line = ANSI_PATTERN.sub("", line)
    line = line.strip()
    
    if line.startswith("Message from client:"):
        line = line.replace("Message from client:", "").strip()
    elif line.startswith("Message from server:"):
        line = line.replace("Message from server:", "").strip()
    
    return line

def try_json(line):
    try:
        return json.loads(line), True
    except:
        return line, False

def is_jsonrpc(obj):
    return isinstance(obj, dict) and "jsonrpc" in obj

def print_json_clean(obj, indent=2):
    """Print JSON without extra quotes or newlines"""
    print(json.dumps(obj, indent=indent))

def print_jsonrpc(obj):
    print("_" * 60)
    if "method" in obj and "id" in obj:
        print("🔵 CLIENT → SERVER")
        print_json_clean(obj)
        print("_" * 60)
        return
    if "result" in obj or "error" in obj:
        print("🟢 SERVER → CLIENT")
        print_json_clean(obj)
        print("_" * 60)
        return
    print("📨 JSON-RPC MESSAGE")
    print_json_clean(obj)
    print("_" * 60)

def print_line_old(line):
    """Print old logs (do NOT skip startup lines)"""
    line = clean_line(line)
    if not line:
        return

    obj, is_json = try_json(line)
    if is_json and is_jsonrpc(obj):
        print_jsonrpc(obj)
    else:
        if "C:\\" not in line and "PATH" not in line:
            print(line)

def print_line_tail(line):
    """Print live logs (skip startup and shutdown lines)"""
    original_line = line
    line = clean_line(line)
    if not line:
        return

    # Check for ignore patterns in the ORIGINAL line (before cleaning)
    if any(ignore in original_line for ignore in IGNORE_STARTUP_LINES):
        return
    if any(ignore in original_line for ignore in IGNORE_LINES):
        return

    obj, is_json = try_json(line)
    if is_json and is_jsonrpc(obj):
        print_jsonrpc(obj)
    else:
        if "C:\\" not in line and "PATH" not in line and line:
            print(line)

def tail():
    # Wait until file exists
    while not os.path.exists(LOG_FILE):
        time.sleep(1)

    # STEP 1 — Print all previous logs (full)
    with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            print_line_old(line.strip())

if __name__ == "__main__":
    tail()