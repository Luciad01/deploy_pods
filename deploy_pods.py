
import sys
from modify_yaml import update_values_yaml, update_inventory_file, remove_nodek8s_field, update_templates_files
from initial_config import prepare_deployment_data, check_nodek8s, check_helm_releases, create_namespaces
from k8s_utils import install_helm, get_pods_node_ips



# ---------------------- Main Deployment --------------------------

def deploy_pods(helm_chart_path, inventory_path):
    node_names, node_nodek8s, node_ports = prepare_deployment_data(inventory_path)
    
    check_nodek8s(node_nodek8s)
    check_helm_releases(node_nodek8s)
    
    node_namespaces = {node: nodek8s + "-ns" for node, nodek8s in node_nodek8s.items()}
    create_namespaces(node_namespaces)
    pods_ips = {}

    
    for node in node_names:
        nodek8s = node_nodek8s.get(node)
        port = node_ports[node]
        namespace = node_namespaces[node]

        update_values_yaml(helm_chart_path, port, node, nodek8s)


        print(f"\n\033[94m[INFO] Desplegando pod '{node}' en puerto {port}...\033[0m")

        install_helm(node, helm_chart_path, namespace)

        pods_ips.update(get_pods_node_ips(node, namespace))


    return pods_ips, node_ports




# ---------------------- Entry Point ------------------------------

if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("\033[1mUso: \033[3mpython3 deploy_pods.py <ruta_al_inventory.yaml> <ruta_al_directorio_helm_chart>\033[0m")
        sys.exit(1)
    

    inventory_path, helm_chart_path = sys.argv[1], sys.argv[2]
    update_templates_files(helm_chart_path)
    
    try:
        pod_ips, node_ports = deploy_pods(helm_chart_path, inventory_path)

        print(f"\n\033[94m[INFO] IPs de los pods desplegados: {pod_ips}\033[0m")

        update_inventory_file(inventory_path, pod_ips, node_ports)  
        remove_nodek8s_field(inventory_path)                            
        
    except ValueError as e:
        print(f"\033[91m! {e}\033[0m")
        sys.exit(1)


