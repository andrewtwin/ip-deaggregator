import ipaddress

def main():
   supernet = ipaddress.ip_network('10.0.0.0/16')
   skip_networks = [
       ipaddress.ip_network('10.0.0.0/24'),
       ipaddress.ip_network('10.0.3.0/24')
       ]

   print(f"Finding subnets of {supernet} which don't include {skip_networks}")
   check_subnets(supernet, skip_networks)

def check_subnets(supernet, skip_networks):
    for network in supernet.subnets(1):
       #print(f"Considering {network}")
       skip = False
       max_gap = supernet.prefixlen
       for gap in skip_networks:
           #print(f"Checking {gap}")
           if gap.prefixlen > max_gap:
               max_gap = gap.prefixlen
               #print(f"New max_gap size {max_gap}")
           if gap.subnet_of(network) or network.subnet_of(gap):
               skip = True
        
       if not skip:
            print(f"{network}")
       elif network.prefixlen < max_gap:
           check_subnets(network, skip_networks)

if __name__ == "__main__":
    main()
