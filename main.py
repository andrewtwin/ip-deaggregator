import ipaddress

def main():
   supernet = ipaddress.ip_network('10.0.0.0/16')
   skip_networks = [
       ipaddress.ip_network('10.0.0.0/24'),
       ipaddress.ip_network('10.0.1.0/24')
       ]

   print(f"Finding subnets of {supernet} which don't include {skip_networks}")
   check_subnets(supernet, skip_networks)

def check_subnets(supernet, skip_networks):
    for network in supernet.subnets(1):
        skip_network = False
        skip_subnet = False
        for gap in skip_networks:
            if gap.subnet_of(network): 
                skip_network = True
            if gap.prefixlen > network.prefixlen:
                skip_subnet = True
        
        if not (skip_network or skip_subnet):
                print(f"{network}")
        else:
            check_subnets(network, skip_networks)

if __name__ == "__main__":
    main()
