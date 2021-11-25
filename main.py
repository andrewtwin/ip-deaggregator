import ipaddress

def main():
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
