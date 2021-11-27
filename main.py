import ipaddress
import argparse

def main():
    parser = argparse.ArgumentParser(description="Subnet a network to exclude address space.")
    parser.add_argument(
        "-n", "--network", type=str, help="Supernet to exclude subnet(s) from.", dest="supernet", required=True 
    )
    parser.add_argument(
        "subnet", type=str, help="Subnet(s) to exclude from the Supernet.", nargs="+"
    )

    parser.add_argument(
        "-d", "--output-delimiter", type=str, help="Sets the output delimeter, default is new line.", default="\n"
    )

    parser.add_argument(
        "-q", "--quiet", help="Only produce output, no other info.", action="store_false", dest="notquiet",
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

    if args.notquiet:
        print(f"Finding the largest subnets of {supernet} which don't include the subnet(s): {', '.join(str(i) for i in subnets)}")
        print("="*18)
    
    new_subnets = exclude_subnets(supernet, subnets)

    delimiter=args.output_delimiter 
    print(f"{delimiter.join(str(i) for i in new_subnets)}")
    
    if args.notquiet:
        print("="*18)
        print(f"{len(new_subnets)} subnets total")

def exclude_subnets(supernet, gap_subnets, output=list()):
    for subnet in supernet.subnets(1):
       unsuitable_subnet = False
       max_gap_size = supernet.prefixlen
       for gap in gap_subnets:
           if gap.prefixlen > max_gap_size:
               max_gap_size = gap.prefixlen
           if gap.subnet_of(subnet) or subnet.subnet_of(gap):
               unsuitable_subnet = True
        
       if not unsuitable_subnet:
            output.append(subnet)
       elif subnet.prefixlen < max_gap_size:
            output = exclude_subnets(subnet, gap_subnets, output)

    return output

if __name__ == "__main__":
    main()
