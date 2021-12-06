# ip-deaggregator
Subnet a network to exclude address space.
Useful for populating route tables, filters, etc.

Does the opposite of [ip-aggregator](https://github.com/andrewtwin/ip-aggregator)

## Usage
```
usage: ip-deaggregator [-h] -n SUPERNET [-q] [-d OUTPUT_DELIMITER] [-m {prefix,net,wildcard}] [-v] subnet [subnet ...]

Subnet a network to exclude address space.

positional arguments:
  subnet                Subnet(s) to exclude from the Supernet.

optional arguments:
  -h, --help            show this help message and exit
  -n SUPERNET, --network SUPERNET
                        Supernet to exclude subnet(s) from.
  -q, --quiet           Only produce output, no other information.
  -d OUTPUT_DELIMITER, --output-delimiter OUTPUT_DELIMITER
                        Sets the output delimeter, default is new line.
  -m {prefix,net,wildcard}, --mask-type {prefix,net,wildcard}
                        Use prefix length (default), net mask, or wildcard mask.
  -v, --verbose         Be more verbose, add timing and performance info.

ip-deaggregator v1.5.1
```

## Installation
Download the python zipapp from the [releases](https://github.com/andrewtwin/ip-deaggregator/releases) page.

## Examples
Single subnet:
```
python3 main.py -n 192.168.0.0/24 192.168.0.0/27
Finding the largest subnets of 192.168.0.0/24 which don't include the subnet(s): 192.168.0.0/27
==================
192.168.0.32/27
192.168.0.64/26
192.168.0.128/25
==================
3 subnets total
```

With alternate bitmask display:
```
python3 main.py -n 192.168.0.0/24 192.168.0.0/27 -m wildcard
Finding the largest subnets of 192.168.0.0/0.0.0.255 which don't include the subnet(s): 192.168.0.0/0.0.0.31
==================
192.168.0.32/0.0.0.31
192.168.0.64/0.0.0.63
192.168.0.128/0.0.0.127
==================
3 subnets total
```

With a different delimiter:
```
python3 main.py -n 192.168.0.0/24 192.168.0.0/27 -d', '
Finding the largest subnets of 192.168.0.0/24 which don't include the subnet(s): 192.168.0.0/27
==================
192.168.0.32/27, 192.168.0.64/26, 192.168.0.128/25
==================
3 subnets total
```

Just the output:
```
python3 main.py -n 192.168.0.0/24 192.168.0.0/27 -d', ' -q
192.168.0.32/27, 192.168.0.64/26, 192.168.0.128/25
```

Multiple subnets:
```
python3 main.py -n 192.168.0.0/16 192.168.1.0/24 192.168.2.0/25 192.168.20.128/27
Finding the largest subnets of 192.168.0.0/16 which don't include the subnet(s): 192.168.1.0/24, 192.168.2.0/25, 192.168.20.128/27
==================
192.168.0.0/24
192.168.2.128/25
192.168.3.0/24
192.168.4.0/22
192.168.8.0/21
192.168.16.0/22
192.168.20.0/25
192.168.20.160/27
192.168.20.192/26
192.168.21.0/24
192.168.22.0/23
192.168.24.0/21
192.168.32.0/19
192.168.64.0/18
192.168.128.0/17
==================
15 subnets total
```
