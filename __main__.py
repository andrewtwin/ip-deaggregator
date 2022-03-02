SYNOPSYS = """Subnet a network to exclude address space. Useful for populating route tables, filters, etc."""

LICENCE = """
Copyright (C) 2022 Andrew Twin

https://github.com/andrewtwin/ip-deaggregator

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

VERSION = "v1.6.0"

import ipaddress
import argparse
import sys
import locale

"""Formatting Constants"""
NEWLINE = "\n"
RULE = "-" * 18

"""IP Network Constants"""
IP4_CLASS_A = [ipaddress.ip_network("10.0.0.0/8")]
IP4_CLASS_B = [ipaddress.ip_network("172.16.0.0/12")]
IP4_CLASS_C = [ipaddress.ip_network("192.168.0.0/16")]
IP4_CLASS_D = [ipaddress.ip_network("224.0.0.0/4")]
IP4_CLASS_E = [ipaddress.ip_network("240.0.0.0/4")]
IP4_CGNAT = [ipaddress.ip_network("100.64.0.0/10")]
IP4_LOCAL = [ipaddress.ip_network("127.0.0.0/8")]
IP4_LINK_LOCAL = [ipaddress.ip_network("169.254.0.0/16")]

IP4_RFC1918_ADDRESSES = IP4_CLASS_A + IP4_CLASS_B + IP4_CLASS_C
IP4_NON_ROUTABLE = IP4_LOCAL + IP4_LINK_LOCAL
IP4_NON_GLOBAL = IP4_RFC1918_ADDRESSES + IP4_NON_ROUTABLE

IP4_ALIASES = {
    "A": IP4_CLASS_A,
    "B": IP4_CLASS_B,
    "C": IP4_CLASS_C,
    "D": IP4_CLASS_D,
    "E": IP4_CLASS_E,
    "CGNAT": IP4_CGNAT,
    "LOCAL": IP4_LOCAL,
    "LINK": IP4_LINK_LOCAL,
    "PRIVATE": IP4_RFC1918_ADDRESSES,
    "NOROUTE": IP4_NON_ROUTABLE,
    "NOGLOBAL": IP4_NON_GLOBAL,
}


def main() -> None:
    locale.setlocale(locale.LC_ALL, "")
    newline = "\n"

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

    """If displaying version and licence, print and exit"""
    if args.version:
        print(f"{VERSION}" + LICENCE)
        exit(0)

    """If just listing the classes, print and exit"""
    if args.list_aliases:
        delimiter = ", "
        print(
            "Recognised address aliases."
            + NEWLINE
            + "These can be used alongside regular addresses:"
            + NEWLINE
            + RULE * 2,
        )
        for ipclass, ipvalue in IP4_ALIASES.items():
            print(
                f"{ipclass.rjust(8)}: "
                f"{delimiter.join(format_address(i, args.mask_type) for i in ipvalue)}"
            )
        exit(0)

    subnets = []
    for subnet in args.subnet:
        try:
            subnets.append(ipaddress.ip_network(subnet))
        except ValueError:
            exit(f"Supplied argument {subnet} is not a valid IPv4 or IPv6 network.")

    # Remove any redundant subnets
    collapsed_subnets = list(ipaddress.collapse_addresses(subnets))

    if args.notquiet:
        # Get a list of redundant subnets which were removed
        removed_subents = set(subnets) - set(collapsed_subnets)

        if len(removed_subents) > 0:
            print(
                "Removed redundant subnets: "
                + newline
                + f"{newline.join(format_address(i, args.mask_type) for i in removed_subents)}"
                + newline,
                file=sys.stderr,
            )

    # Runs faster when the largest subnets come first
    sorted_subnets = sorted(collapsed_subnets, key=get_prefixlen)

    if args.notquiet:
        print(
            f"Finding the largest subnets of {format_address(supernet, args.mask_type)} "
            + "which don't include the subnet(s):"
            + newline
            + f"{newline.join(format_address(i, args.mask_type) for i in sorted_subnets)}"
            + newline
            + RULE,
            file=sys.stderr,
        )

    exclude_subnets.count = 0
    exclude_subnets.max_gap_prefixlen = 0
    new_subnets = exclude_subnets(supernet, sorted_subnets)

    delimiter = args.output_delimiter
    print(f"{delimiter.join(format_address(i, args.mask_type) for i in new_subnets)}")

    if args.notquiet:
        print(
            RULE + NEWLINE + f"{len(new_subnets)} subnets total",
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
