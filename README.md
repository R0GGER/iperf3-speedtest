# iPERF3 SpeedTest

A simple Python tool and web app to measure your internet speed using public iperf3 servers.

## Features
- **Command-line tool** (`speedtest.py`) for quick speed tests
- **Modern web interface** (Flask app) for easy use in your browser
- **Benchmarks multiple servers and finds the fastest**
- **Shows both download and upload speeds**

## Quick Install
1. **Install Python 3.6+**
2. **Install iperf3**
   - Windows: [Download here](https://iperf.fr/iperf-download.php) and add to PATH
   - macOS: `brew install iperf3`
   - Linux: `sudo apt install iperf3`
3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Command Line
- **Refresh server list:**
  ```bash
  python speedtest.py refresh
  ```
- **Benchmark fastest servers:**
  ```bash
  python speedtest.py bench 3
  ```
- **Run speed test (download + upload):**
  ```bash
  python speedtest.py run
  ```

### Web Interface
- **Start the web app:**
  ```bash
  python app.py
  ```
- Open your browser at [http://localhost:5000](http://localhost:5000)
- Use the buttons:
  - **Refresh:** Get latest server list and ping times
  - **Bench:** Test download speed of fastest servers (number is adjustable)
  - **Speedtest:** Run full download + upload test on the best server

## File Structure
```
speedtest/
├── speedtest.py      # Command-line tool
├── app.py            # Flask web app
├── requirements.txt  # Python dependencies
├── static/           # CSS, images
├── templates/        # HTML templates
└── cache.json        # Server cache (auto-generated)
```

## Tips
- Always start with **Refresh** and **Bench** before running a full speed test
- The web UI shows results in a clear dashboard and lets you view detailed output
- All results are cached for faster repeated tests

---
Speedtest.py script forked from: https://github.com/afontenot/speedtest
