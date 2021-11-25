import ipaddress

def main():
   supernet = ipaddress.ip_network('10.0.0.0/16')
   skip_networks = [
       ipaddress.ip_network('10.0.0.0/24'),
       ipaddress.ip_network('10.0.128.0/24')
       ]

   print(f"Finding subnets of {supernet} which don't include {skip_networks}")
   get_subnets(supernet, skip_networks)

def get_subnets(supernet, skip_networks):
    for network in supernet.subnets(1):
        contains_gap = False
        for gap in skip_networks:
            if gap.subnet_of(network):
                contains_gap = True
            else:    
                if gap.prefixlen > network.prefixlen:
                    break
        if not contains_gap :
                print(f"{network}")
        else:
            get_subnets(network, skip_networks)

if __name__ == "__main__":
    main()
