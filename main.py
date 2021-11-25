import ipaddress

def main():
   supernet = ipaddress.ip_network('10.0.0.0/16')
   skip_network = ipaddress.ip_network('10.0.0.0/24')

   print(f"Finding subnets of {supernet} which don't include {skip_network}")
   get_subnets(supernet, skip_network)

def get_subnets(supernet, skip_network):
    for network in supernet.subnets(1):
        if not skip_network.subnet_of(network): 
            if skip_network.prefixlen >= network.prefixlen:
                print(f"{network}")
        else:
            get_subnets(network, skip_network)

if __name__ == "__main__":
    main()
