
import subprocess
import time
import json
from config import *


# ---------------------- Helm/K8s Deployment ----------------------

def install_helm(node_name, helm_chart_path, namespace):
    try:
        subprocess.run([
            "microk8s", "helm3", "install", node_name, helm_chart_path,
            "-n", namespace, "-f", f"{helm_chart_path}/values.yaml"
        ], check=True)

        time.sleep(7)

    except subprocess.CalledProcessError as e:
        print(f"\n\033[91m[ERROR] {ERROR_MSG_INSTALL_HELM} '{node_name}'\033[0m\n{e}\n")


def uninstall_helms(node_names, namespace):
    try:
        print("\033[91mDesinstalando pods previamente instalados...\033[0m")

        for node_name in node_names:
            subprocess.run([
                "microk8s", "helm3", "uninstall", node_name, "-n", namespace
            ], check=True)

    except subprocess.CalledProcessError as e:
        print(f"\n\033[91m[ERROR] {ERROR_MSG_UNINSTALL_HELM} \033[0m\n{e}\n")
    



# ---------------------- IP Gathering -----------------------------

def get_node_internal_ips():
    result = subprocess.run(
        ["microk8s", "kubectl", "get", "nodes", "-o", "json"],  
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE, 
        text=True, check=True
    )

    data = json.loads(result.stdout)

    node_ip_map = {
        node["metadata"]["name"]: next(
            (
                addr["address"] 
                for addr in node["status"]["addresses"] 
                if addr["type"] == "InternalIP"
            ), None
        ) for node in data["items"]
    }

    return node_ip_map



def get_pods_node_ips(node, namespace):
    node_ips = get_node_internal_ips()

    result = subprocess.run(
        ["microk8s", "kubectl", "get", "pods", "-n", namespace, "-o", "wide"],
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE, 
        text=True, check=True
    )

    lines = result.stdout.strip().split("\n")[1:]
    pod_ip = {}

    for line in lines:
        parts = line.split()

        if len(parts) >= 7:
            pod_name, node_pod = parts[0], parts[6]
            
            if pod_name.startswith(node):
                pod_ip[node] = node_ips.get(node_pod)
                break

    return pod_ip
