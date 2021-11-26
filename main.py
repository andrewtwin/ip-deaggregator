import ipaddress
import argparse

def main():
    parser = argparse.ArgumentParser(description="Subnet a network to exclude address space.")
    parser.add_argument(
        "-n", "--network", type=str, help="Supernet to exclude subnets from.", dest="supernet", 
    )
    parser.add_argument(
        "subnet", type=str, help="Subnet to exclude from the Supernet.", nargs="+"
    )

    args = parser.parse_args()
    try:
        supernet = ipaddress.ip_network(args.supernet)
    except ValueError:
        exit(f"Supplied argument {args.supernet} is not a valid IPv4 or IPv6 network.")

    subnets = list()
    for subnet in args.subnet:
        try:
            subnets.append(ipaddress.ip_network(subnet))
        except ValueError:
            exit(f"Supplied argument {subnet} is not a valid IPv4 or IPv6 network.")

    print(f"Finding the largest subnets of {supernet} which don't include the subnets: {', '.join(str(i) for i in subnets)}")
    exclude_subnets(supernet, subnets)

def exclude_subnets(supernet, gap_subnets):
    for subnet in supernet.subnets(1):
       unsuitable_subnet = False
       max_gap_size = supernet.prefixlen
       for gap in gap_subnets:
           if gap.prefixlen > max_gap_size:
               max_gap_size = gap.prefixlen
           if gap.subnet_of(subnet) or subnet.subnet_of(gap):
               unsuitable_subnet = True
        
       if not unsuitable_subnet:
            print(f"{subnet}")
       elif subnet.prefixlen < max_gap_size:
           exclude_subnets(subnet, gap_subnets)

if __name__ == "__main__":
    main()
