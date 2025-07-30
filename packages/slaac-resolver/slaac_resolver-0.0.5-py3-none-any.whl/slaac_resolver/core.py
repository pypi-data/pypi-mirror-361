import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

logging.basicConfig(
    level=logging.DEBUG,
    stream=sys.stderr,
    format='%(asctime)s %(levelname)s %(message)s'
)

def _resolve_address(ipv6_addr):
    logging.debug(f"Resolving address: {ipv6_addr}")
    result = subprocess.run(
        ["avahi-resolve-address", ipv6_addr],
        capture_output=True, text=True
    )
    logging.debug(f"Result for {ipv6_addr}: {result.stdout.strip()}")
    return result.stdout.strip()

def _resolve_addresses_parallel(ipv6_addresses):
    results = {}
    with ThreadPoolExecutor() as executor:
        future_to_ip = {executor.submit(_resolve_address, ip): ip for ip in ipv6_addresses}
        for future in as_completed(future_to_ip):
            ip = future_to_ip[future]
            try:
                results[ip] = future.result()
            except Exception as exc:
                results[ip] = f"Error: {exc}"
    return results

def get_ipv6_neighbors(interface, log_level=logging.INFO):
    logging.getLogger().setLevel(log_level)
    try:
        logging.info(f"Getting IPv6 neighbors for interface: {interface}")
        result = subprocess.run(
            ["ip", "-6", "neigh", "show", "dev", interface],
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to get neighbors on {interface}: {e.stderr}")
        print(f"Failed to get neighbors on {interface}: {e.stderr}", file=sys.stderr)
        return []

    # Collect all IPv6 addresses first
    ipv6_addrs = []
    for line in result.stdout.strip().split("\n"):
        if "FAILED" in line or not line.strip():
            continue
        parts = line.split()
        if len(parts) < 1:
            continue
        addr = parts[0]
        if addr.startswith("fe80:") or addr.startswith("::1"):
            logging.debug(f"Skipping link-local address: {addr}")
            continue
        ipv6_addrs.append(addr)

    # Resolve all addresses in parallel
    resolved_dict = _resolve_addresses_parallel(ipv6_addrs)

    neighbors = []
    for addr, resolved in resolved_dict.items():
        resolved_output = resolved.strip().split()
        if len(resolved_output) >= 2:
            name = resolved_output[1]
            neighbors.append({
                "Hostname": name.split(".")[0],
                "Address": addr.split(":")
            })
    return neighbors
