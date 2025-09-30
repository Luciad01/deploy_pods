
import subprocess
import json
import sys
from config import *
from yaml_utils import load_yaml
from k8s_utils import get_node_internal_ips
from ports_utils import get_used_nodeports, get_unique_random_port


# ---------------------- Preparation ------------------------------

def prepare_deployment_data(inventory_path):
    inventory = load_yaml(inventory_path)
    hosts = inventory.get("all", {}).get("hosts", {})

    node_names, node_nodek8s, node_ports = get_data(hosts)

    print_initial_summary(node_nodek8s, node_names)

    return node_names, node_nodek8s, node_ports



def get_data(hosts):
    node_names = []
    node_nodek8s = {}
    node_ports = {}

    used_ports = get_used_nodeports()

    for node, data in hosts.items():
        host_defined = data.get("ansible_host")
        port_defined = data.get("ansible_port")
        check_configuration(node, host_defined, port_defined)

        if not host_defined and not port_defined:
            node_names.append(node)
            node_nodek8s[node] = data.get("nodek8s")
            node_ports[node] = get_unique_random_port(used_ports)
    
    return node_names, node_nodek8s, node_ports



def check_configuration(node, host, port):
    if not host and port:
        print(f"\n\t\033[91m[ERROR] El nodo '{node}' tiene 'ansible_port' definido ({port}) pero no 'ansible_host' en inventory.yaml.\033[0m\n")
        raise ValueError(ERROR_MSG_INCOMPLETE_ANSIBLE_CONFIG)


    if host and not port:
        print(f"\n\t\033[91m[ERROR] El nodo '{node}' tiene 'ansible_host' definido ({host}) pero no 'ansible_port' en inventory.yaml.\033[0m\n")
        raise ValueError(ERROR_MSG_INCOMPLETE_ANSIBLE_CONFIG)
    


def print_initial_summary(node_nodek8s, node_names):
    print("\n\033[94m[INFO] Distribución de nodos QKD por nodo de Kubernetes (solo pendientes de desplegar):\033[0m")
    for node, nodek8s in node_nodek8s.items():
        if nodek8s:
            print(f"  - {node} → {nodek8s}")

    print(f"\n\033[94m[INFO] {len(node_names)} nodo(s) QKD definido(s) a desplegar: {', '.join(node_names)}\033[0m")



def check_nodek8s(node_nodek8s):
    for node, nodek8s in node_nodek8s.items():

        if not nodek8s:
            print(f"\n\t\033[91m[ERROR] El nodo '{node}' no tiene un nodo de Kubernetes asignado en inventory.yaml.\033[0m\n")
            raise ValueError(ERROR_MSG_MISSING_NODEK8S)
    

    existing_nodes = get_node_internal_ips().keys()
    missing_nodek8s = set(node_nodek8s.values()) - set(existing_nodes)

    if missing_nodek8s:
        print(f"\n\t\033[91m[ERROR] Los siguientes nodosk8s asignados no existen:\033[0m {', '.join(missing_nodek8s)}\n")
        raise ValueError(ERROR_MSG_INVALID_NODEK8S)



def check_helm_releases(node_names):
    node_names = {rel: f"{ns}-ns" for rel, ns in node_names.items()}
    namespaces = sorted(set(node_names.values()))
    deployed = set()

    for ns in namespaces:
        result = subprocess.run(
            ["microk8s", "helm3", "list", "-n", ns, "-o", "json"], 
            capture_output=True, 
            text=True
        )
    
        if result.returncode != 0:
            continue

        releases = json.loads(result.stdout or "[]")

        for r in releases:
            if str(r.get("status")) == "deployed":
                name = r.get("name")

                if name:
                    deployed.add((name, ns))  

    matches = {
        rel: ns for rel, ns in node_names.items()
        if (rel, ns) in deployed
    }

    if matches:
        print("\n\033[91m[ERROR] Estos Helm ya están desplegados con el namespace indicado:")

        for rel, ns in matches.items():
            print(f"\t- {rel} → {ns}\033[0")

        print(f"\n\033[93m[AVISO] {WARNING_HELM_CONFLICT} \033[0m")

        raise SystemExit(0)  



def create_namespaces(namespaces):
    unique_namespaces = set(namespaces.values())

    for ns in unique_namespaces:
        try:
            result = subprocess.run(
                ["microk8s", "kubectl", "get", "namespace", ns],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                print(f"\n\033[94m[INFO] El namespace '{ns}' ya esixte, se omite.\033[0m")
                continue
        except subprocess.CalledProcessError:
            pass


        try:
            subprocess.run(
                ["microk8s", "kubectl", "create", "namespace", ns],
                check=True
            )
            print(f"\n\033[92m[OK] El namespace '{ns}' se ha creado correctamente.\033[0m")
        
        except subprocess.CalledProcessError:
            print(f"\n\033[91m[ERROR] {ERROR_MSG_CREATE_NAMESPACE} '{ns}'.\033[0m")
            return set()
