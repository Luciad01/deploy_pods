
import random
import subprocess
from config import *


# ---------------------- Port Management --------------------------

def get_used_nodeports():
    try:
        result = subprocess.run(
            ["microk8s", "kubectl", "get", "services", "--all-namespaces", "-o",
             "jsonpath={.items[*].spec.ports[*].nodePort}"],
            capture_output=True, text=True, check=True
        )

        return set(map(int, result.stdout.strip().split()))

    except subprocess.CalledProcessError as e:
        print(f"\n\033[91m[ERROR] {ERROR_MSG_NODEPORT_RETRIEVAL}\033[0m\n{e}\n")
        return set()



def get_unique_random_port(used_ports):
    for _ in range(1000):
        port = random.randint(NODEPORT_MIN, NODEPORT_MAX)

        if port not in used_ports:
            used_ports.add(port)

            return port

    raise RuntimeError("No se encontró un puerto libre tras muchos intentos.")
