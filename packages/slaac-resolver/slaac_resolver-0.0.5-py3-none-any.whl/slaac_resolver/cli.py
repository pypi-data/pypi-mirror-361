import argparse
import json
from slaac_resolver.core import get_ipv6_neighbors

def main():
    parser = argparse.ArgumentParser(description="Discover IPv6 neighbors via SLAAC on a given interface")
    parser.add_argument("interface", help="The network interface to scan (e.g. br0)")
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level (default: INFO)"
    )    
    args = parser.parse_args()

    data = get_ipv6_neighbors(args.interface, args.log_level.upper())
    print(json.dumps(data))
