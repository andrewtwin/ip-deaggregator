import ipaddress
import argparse
import sys
import locale


def main() -> None:
    locale.setlocale(locale.LC_ALL, "")

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

    # Runs faster when the largest subnets come first
    sorted_subnets = sorted(subnets, key=get_prefixlen)

    newline = "\n"
    if args.notquiet:
        print(
            f"Finding the largest subnets of {format_address(supernet, args.mask_type)} "
            + f"which don't include the subnet(s):{newline}"
            + f"{newline.join(format_address(i, args.mask_type) for i in sorted_subnets)}"
            + {newline}
            + "=" * 18,
            file=sys.stderr,
        )

    exclude_subnets.count = 0
    exclude_subnets.max_gap_prefixlen = 0
    new_subnets = exclude_subnets(supernet, sorted_subnets)

    delimiter = args.output_delimiter
    print(f"{delimiter.join(format_address(i, args.mask_type) for i in new_subnets)}")

    if args.notquiet:
        print(
            "=" * 18 + newline + f"{len(new_subnets)} subnets total",
            file=sys.stderr,
        )

    if args.verbose:
        print(
            "Total subnets considered: "
            + "{0:n}".format(exclude_subnets.count)
            + newline
            + "Max subnet prefix length: "
            + "{0:n}".format(exclude_subnets.max_gap_prefixlen),
            file=sys.stderr,
        )


def exclude_subnets(supernet, gap_subnets, output=[]) -> list:
    """returns a list of networks from the supernet with subnets removed

    Split the supernet in half and check for subnets in each half.
    Repeat until all subnets exclude the contents of gap_subnets.
    """
    if exclude_subnets.max_gap_prefixlen == 0:
        for gap in gap_subnets:
            if exclude_subnets.max_gap_prefixlen < gap.prefixlen:
                exclude_subnets.max_gap_prefixlen = gap.prefixlen

    for subnet in supernet.subnets(1):
        exclude_subnets.count += 1
        unsuitable_subnet = False
        for gap in gap_subnets:
            if gap.subnet_of(subnet) or subnet.subnet_of(gap):
                unsuitable_subnet = True
                break

        if not unsuitable_subnet:
            output.append(subnet)
        elif subnet.prefixlen < exclude_subnets.max_gap_prefixlen:
            exclude_subnets(subnet, gap_subnets, output)
    return output


def format_address(address, mask="prefix") -> str:
    """return the formatted network"""
    if mask == "net":
        return address.with_netmask
    elif mask == "wildcard":
        return address.with_hostmask
    else:
        return address.with_prefixlen


def get_prefixlen(ip_net) -> int:
    """return the prefix length of each network

    Used for sorting by subnet length
    """
    return ip_net.prefixlen


if __name__ == "__main__":
    main()
