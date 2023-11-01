#!/usr/bin/env python3
import json
import re
import subprocess
import sys
from math import inf
from random import randint, shuffle
from statistics import mean

import requests


SERVER_LIST = "https://iperf3serverlist.net/serverlist.json"
PINGTIME = re.compile("time=([.\d]+) (m?s)")
PORTRANGE = re.compile("-p (\d+)(-(\d+))?")
SPEED = re.compile("^\[SUM\].* (\d+) Kbits/sec.*receiver", re.MULTILINE)


def popen(cmd):
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def ping(addr):
    return popen(["ping", "-c", "5", "-w", "10", addr]).communicate()


def refresh(checkall=False):
    cache = {}
    try:
        with open("cache.json") as f:
            cache = json.loads(f.read())
    except FileNotFoundError:
        pass

    if not "best" in cache:
        cache["best"] = 0
    if not "servers" in cache:
        cache["servers"] = {}

    r = requests.get(SERVER_LIST)
    j = json.loads(r.text)

    servers = list(j["results"])
    shuffle(servers)

    for server in servers:
        server_string = server["IP"].removeprefix("iperf3 -c ").split(maxsplit=1)
        addr = server_string[0]

        if not addr in cache["servers"]:
            cache["servers"][addr] = {}

        # skip if last attempt to contact server failed
        if not checkall and not cache["servers"][addr].get("success", True):
            continue

        # skip if previous result was more than 2x higher than best
        if not checkall and cache["servers"][addr].get("ping", 0) > 2 * cache["best"]:
            continue

        # skip if server does not support reverse mode
        if not any(opt["value"] == "-R" for opt in server["OPTIONS"]):
            continue

        out, err = ping(addr)
        out = out.decode("utf-8")
        if not ", 0% packet loss" in out:
            print(">>", addr, "failed")
            cache["servers"][addr]["success"] = False
            continue

        avg_time = mean(
            float(x[0]) * 10 ** (3 * int(x[1] == "s")) for x in PINGTIME.findall(out)
        )
        print(">>", addr, avg_time)
        cache["servers"][addr]["ping"] = avg_time
        cache["servers"][addr]["success"] = True

        if len(server_string) == 2:
            match = PORTRANGE.match(server_string[1])
            if match:
                grps = match.groups()
                cache["servers"][addr]["min_port"] = int(grps[0])
                if grps[2]:
                    cache["servers"][addr]["max_port"] = int(grps[2])

    best_server = ""
    best_time = inf
    for server, result in cache["servers"].items():
        if not result.get("success", False):
            continue
        if result["ping"] <= best_time:
            best_server = server
            best_time = result["ping"]
    print("Best result:", best_server, best_time)
    cache["best"] = best_time

    with open("cache.json", "w") as f:
        f.write(json.dumps(cache))


def server_sort(v):
    if not v[1].get("success"):
        return inf
    return v[1]["ping"]


def run_test(server, s_data, reverse_mode=True):
    cmd = ["iperf3", "-c", server, "-fk", "-O2", "-t12", "-P2", "--connect-timeout", "5000"]
    if reverse_mode:
        cmd.append("-R")
    if "min_port" in s_data:
        port = s_data["min_port"]
        if "max_port" in s_data:
            port = randint(s_data["min_port"], s_data["max_port"])
        cmd.append(f"-p {port}")
    print(f"Testing {'download from' if reverse_mode else 'upload to'} {server}...")
    proc = popen(cmd)
    out, err = proc.communicate()
    if err:
        err = err.decode("utf-8")
        print("ERROR:", err)
        if "the server is busy running a test" in err:
            return 0
        return None
    out = out.decode("utf-8")
    kbps = int(SPEED.search(out).groups()[0])
    if kbps >= 10000:
        print(f"Result: {round(kbps / 1000, 1)} Mbps")
    else:
        print(f"Result: {kbps} Kbps")
    return kbps


def bench(tests):
    with open("cache.json") as f:
        cache = json.loads(f.read())

    best_speed = 0
    best_server = ""
    for server, data in sorted(cache["servers"].items(), key=server_sort)[:tests]:
        result = run_test(server, data)
        if result is None:
            cache["servers"][server]["success"] = False
        elif result > best_speed:
            best_speed = result
            best_server = server
    cache["preferred"] = best_server

    with open("cache.json", "w") as f:
        f.write(json.dumps(cache))


def run():
    with open("cache.json") as f:
        cache = json.loads(f.read())

    preferred_server = cache.get("preferred")
    if not preferred_server:
        print("No preferred server. Benchmark them first.")
        return
    run_test(preferred_server, cache["servers"][preferred_server])
    run_test(preferred_server, cache["servers"][preferred_server], reverse_mode=False)


if __name__ == "__main__":
    if 2 <= len(sys.argv) <= 3 and sys.argv[1] == "refresh":
        if len(sys.argv) == 3 and sys.argv[2] == "all":
            refresh(True)
        else:
            refresh()
    elif len(sys.argv) == 2 and sys.argv[1] == "run":
        run()
    elif len(sys.argv) == 3 and sys.argv[1] == "bench" and sys.argv[2].isdigit():
        bench(int(sys.argv[2]))
    else:
        print(
            f"Usage: {sys.argv[0]} [command]\n"
            "    refresh [all]: refresh server list from web source\n"
            "    run: run download + upload test\n"
            "    bench [n]: benchmark closest n servers for best download speed"
        )
