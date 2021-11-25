import ipaddress
import argparse

def main():
    parser = argparse.ArgumentParser(description="Subnet a network.")
    parser.add_argument(
        "network", type=str, help="Network to subnet.",
    )
    parser.add_argument(
        "-m", "--max-prefix", type=int, default=25, help="Maximum prefix length.",
    )
    parser.add_argument(
        "-c", "--indent-char", default=" ", help="Characters to use for indentation.",
    )

    args = parser.parse_args()
    try:
        parent_network = ipaddress.ip_network(args.network)
    except ValueError:
        exit(f"Supplied argument {args.network} is not a valid IPv4 or IPv6 network.")

    if args.max_prefix <= parent_network.prefixlen:
        exit(
            f"Network prefix {args.max_prefix} already at or beyond max prefix length {parent_network.prefixlen}."
        )
  
    supernet = ipaddress.ip_network('10.0.0.0/16')
    gap_subnets = [
       ipaddress.ip_network('10.0.0.0/24'),
       ipaddress.ip_network('10.0.3.0/25'),
       ipaddress.ip_network('10.0.90.0/26')
       ]

    print(f"Finding subnets of {supernet} which don't include {', '.join(str(i) for i in gap_subnets)}")
    check_subnets(supernet, gap_subnets)

def check_subnets(supernet, gap_subnets):
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
           check_subnets(subnet, gap_subnets)

if __name__ == "__main__":
    main()
