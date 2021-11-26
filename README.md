# ip-gap-finder

Subnet a network to exclude address space.

Useful for populating route tables, filters, etc.

Examples:

Single subnet:
```
main.py -n 192.168.0.0/24 192.168.0.0/27
Finding the largest subnets of 192.168.0.0/24 which don't include the subnets: 192.168.0.0/27
192.168.0.32/27
192.168.0.64/26
192.168.0.128/25
```

Multiple subnets:
```
main.py -n 192.168.0.0/16 192.168.1.0/24 192.168.2.0/25 192.168.20.128/27
Finding the largest subnets of 192.168.0.0/16 which don't include the subnets: 192.168.1.0/24, 192.168.2.0/25, 192.168.20.128/27
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
```