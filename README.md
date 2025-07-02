# Speedtest Script using public iperf3-servers

A Python-based network speed testing tool that uses iperf3 servers to measure your internet connection speed.

Forked from: https://github.com/afontenot/speedtest

## Overview

This script provides a command-line interface for testing your internet connection speed by:
1. Fetching a list of available iperf3 servers from the internet
2. Testing ping times to find the fastest servers
3. Running speed tests to measure download and upload speeds
4. Caching results for faster subsequent runs

## Prerequisites

### Required Software
- **Python 3.6+** - The script is written in Python
- **iperf3** - Network performance measurement tool
- **requests** - Python library for HTTP requests

### Installing Dependencies

#### Python Dependencies
```bash
pip install requests
```

#### iperf3 Installation

**Windows:**
- Download from: https://iperf.fr/iperf-download.php
- Extract and add to your PATH environment variable

**macOS:**
```bash
brew install iperf3
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install iperf3
```

**Linux (CentOS/RHEL):**
```bash
sudo yum install iperf3
```

## Usage

The script supports three main commands:

### 1. Refresh Server List
```bash
python speedtest.py refresh
```

**What it does:**
- Downloads the latest list of iperf3 servers from the internet
- Tests ping times to each server
- Caches the results in `cache.json`
- Skips servers that don't support reverse mode (download testing)

**Options:**
- `refresh all` - Tests all servers, including previously failed ones

**Output:**
- Shows ping times for each server tested
- Displays the best server found
- Creates/updates `cache.json` file

### 2. Benchmark Servers
```bash
python speedtest.py bench <number>
```

**Parameters:**
- `<number>` - Number of fastest servers to test (e.g., `3` for top 3)

**What it does:**
- Tests download speeds on the fastest servers (based on ping times)
- Finds the server with the best download performance
- Marks it as the preferred server for future tests

**Example:**
```bash
python speedtest.py bench 5
```

### 3. Run Speed Test
```bash
python speedtest.py run
```

**What it does:**
- Runs both download and upload tests on the preferred server
- Uses the server selected during benchmarking

**Output:**
- Download speed test results
- Upload speed test results
- Results displayed in Mbps (if ≥ 10 Mbps) or Kbps

## File Structure

```
speedtest/
├── speedtest.py    # Speedtest script.
├── cache.json      # Cached server data (created automatically).
└── README.md       # This readme.
```

### cache.json Structure
```json
{
  "best": 0.0035796165466308594,
  "preferred": "ping-ams1.online.net",
  "servers": {
    "server1.com": {
      "ping": 0.015,
      "success": true,
      "min_port": 5201,
      "max_port": 5210
    }
  }
}
```

## Technical Details

### Server Selection Criteria
- Must support reverse mode (`-R` option)
- Ping time < 2x the best ping time (unless using `refresh all`)
- Previously successful connections are prioritized

### Test Parameters
- **Duration:** 12 seconds per test
- **Parallel streams:** 2 connections
- **Timeout:** 5 seconds connection timeout
- **Format:** Results in Kbps/Mbps
