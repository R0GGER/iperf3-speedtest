# A high-performance speedtest using public iperf3 servers

```
$ ./speedtest.py run
Testing download from nyfiosspeed2.west.verizon.net...
Result: 948.5 Mbps
Testing upload to nyfiosspeed2.west.verizon.net...
Result: 24.0 Mbps
```

I can't get performance like this with any public speed test
I've tried, so I wrote my own.

This script fetches and caches a list of public iperf3 servers
provided by the
[public-iperf3-servers](https://github.com/R0GGER/public-iperf3-servers)
project.

## Usage

```
Usage: ./speedtest.py [command]
    refresh: refresh server list from web source
    run: run download + upload test
    bench [n]: benchmark closest n servers for best download speed
```

 * `refresh` downloads the server list and determines which servers
 are accessible (and how close they are) based on ping

 * `bench` attempts a download test on the n closest servers (using
 the cached ping value, see above), and ranks them based on their
 performance.

 * `run` performs both download and upload tests with the best
 server, as determined by previous runs of `bench`.
