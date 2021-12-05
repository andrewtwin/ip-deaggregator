import ipaddress
import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Subnet a network to exclude address space.",
        epilog="ip-deaggregator v1.5.0",
    )

    parser.add_argument(
        "-n",
        "--network",
        type=str,
        help="Supernet to exclude subnet(s) from.",
        dest="supernet",
        required=True,
    )

    parser.add_argument(
        "subnet", type=str, help="Subnet(s) to exclude from the Supernet.", nargs="+"
    )

    parser.add_argument(
        "-q",
        "--quiet",
        help="Only produce output, no other information.",
        action="store_false",
        dest="notquiet",
    )

    parser.add_argument(
        "-d",
        "--output-delimiter",
        type=str,
        help="Sets the output delimeter, default is new line.",
        default="\n",
    )

    parser.add_argument(
        "-m",
        "--mask-type",
        help="Use prefix length (default), net mask, or wildcard mask.",
        type=str,
        choices=["prefix", "net", "wildcard"],
        default="prefix",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        help="Be more verbose, add timing and performance info.",
        action="store_true",
        dest="verbose",
    )

    args = parser.parse_args()
    try:
        supernet = ipaddress.ip_network(args.supernet)
    except ValueError:
        exit(f"Supplied argument {args.supernet} is not a valid IPv4 or IPv6 network.")

    subnets = []
    for subnet in args.subnet:
        try:
            subnets.append(ipaddress.ip_network(subnet))
        except ValueError:
            exit(f"Supplied argument {subnet} is not a valid IPv4 or IPv6 network.")

    sorted_subnets = sorted(subnets, key=get_prefixlen)

    if args.notquiet:
        print(
            f"Finding the largest subnets of {format_address(supernet, args.mask_type)} "
            f"which don't include the subnet(s): {', '.join(format_address(i, args.mask_type) for i in sorted_subnets)}",
            file=sys.stderr,
        )
        # print("=" * 18)

    exclude_subnets.count = 0
    exclude_subnets.max_gap_prefixlen = 0
    new_subnets = exclude_subnets(supernet, sorted_subnets)

    delimiter = args.output_delimiter
    print(f"{delimiter.join(format_address(i, args.mask_type) for i in new_subnets)}")

    if args.notquiet:
        # print("=" * 18)
        print(
            f"{len(new_subnets)} subnets total",
            file=sys.stderr,
        )

    if args.verbose:
        print(
            f"Total subnets considered: {exclude_subnets.count}",
            file=sys.stderr,
        )
        print(
            f"Max subnet prefix length: {exclude_subnets.max_gap_prefixlen}",
            file=sys.stderr,
        )


def exclude_subnets(supernet, gap_subnets, output=[]):
    if exclude_subnets.max_gap_prefixlen == 0:
        for gap in gap_subnets:
            if exclude_subnets.max_gap_prefixlen < gap.prefixlen:
                exclude_subnets.max_gap_prefixlen = gap.prefixlen

    for subnet in supernet.subnets(1):
        exclude_subnets.count += 1
        unsuitable_subnet = False
        for gap in gap_subnets:
            if gap.subnet_of(subnet) or gap.prefixlen > subnet.prefixlen:
                unsuitable_subnet = True
                break

        if not unsuitable_subnet:
            output.append(subnet)
        elif subnet.prefixlen < exclude_subnets.max_gap_prefixlen:
            exclude_subnets(subnet, gap_subnets, output)
    return output


def format_address(address, mask="prefix"):
    if mask == "net":
        return address.with_netmask
    elif mask == "wildcard":
        return address.with_hostmask
    else:
        return address.with_prefixlen


def get_prefixlen(ip_net):
    return ip_net.prefixlen


if __name__ == "__main__":
    main()
