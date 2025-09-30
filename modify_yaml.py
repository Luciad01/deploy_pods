
import re
import os
import sys
from config import *
from yaml_utils import load_yaml, save_yaml, readlines_yaml, write_yaml


# ---------------------- File Update Functions --------------------

def update_values_yaml(helm_chart_path, ssh_node_port, node_name, nodek8s):
    values_path = f"{helm_chart_path}/values.yaml"

    values = load_yaml(values_path)

    values.update({
        "sshNodePort": ssh_node_port,
        "appSelector": node_name,
        "podName": node_name,
        "namespace": f"{nodek8s}-ns",
        "nodeSelector": {
            "kubernetes.io/hostname": nodek8s
        },
    })

    save_yaml(values_path, values)
    print(f"\n\033[92m[OK] values.yaml actualizado para {node_name}\033[0m")



def update_inventory_file(inventory_path, pod_ips, node_ports):
    inventory = load_yaml(inventory_path)
    hosts = inventory.get("all", {}).get("hosts", {})

    for node, data in hosts.items():

        if node in pod_ips:
            data["ansible_host"] = pod_ips[node]
            data["ansible_port"] = node_ports[node]

    save_yaml(inventory_path, inventory)
    print(f"\n\033[92m[OK] Inventory actualizado: {inventory_path}\033[0m")



def remove_nodek8s_field(inventory_path):
    inventory = load_yaml(inventory_path)
    hosts = inventory.get('all', {}).get('hosts', {})

    for node in hosts.values():
        node.pop("nodek8s", None)

    save_yaml(inventory_path, inventory)
    print(f"\n\033[92m[OK] Campo 'nodek8s' eliminado de: {inventory_path}\033[0m")


# ---------------------- File Update Functions ON INITIALIZATION --------------------

def update_templates_files(file_path):   
    service_path = file_path + "/templates/service.yaml"
    deployment_path = file_path + "/templates/deployment.yaml"
    values_path = file_path + "/values.yaml"

    chart_name = os.path.basename(os.path.normpath(file_path)) 


    new_service = f"""apiVersion: v1
kind: Service
metadata:
  name: {{{{ include "{chart_name}.fullname" . }}}}
  labels:
    {{{{- include "{chart_name}.labels" . | nindent 4 }}}}
spec:
  type: {{{{ .Values.service.type }}}}
  selector:
    app.kubernetes.io/instance: {{{{ $.Values.podName }}}}
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/name: {chart_name}
    app.kubernetes.io/version: 1.16.0
    helm.sh/chart: {chart_name}-0.1.0

  ports:
    - port: {{{{ .Values.service.port }}}}
      targetPort: 22
      protocol: TCP
      name: ssh
      {{{{- if .Values.sshNodePort }}}}
      nodePort: {{{{ .Values.sshNodePort }}}}
      {{{{- end }}}}
  selector:
    {{{{- include "{chart_name}.selectorLabels" . | nindent 4 }}}}"""



    new_deployment = f"""{{{{- range .Values.nodes }}}}

apiVersion: apps/v1
kind: Deployment
metadata:
    name: {{{{ $.Release.Name }}}}
    namespace: {{{{ $.Values.namespace }}}}
spec:
    replicas: {{{{ $.Values.replicaCount }}}}
    selector:
        matchLabels:
            app.kubernetes.io/instance: {{{{ $.Values.podName }}}}
            app.kubernetes.io/managed-by: Helm
            app.kubernetes.io/name: {chart_name}
            app.kubernetes.io/version: 1.16.0
            helm.sh/chart: {chart_name}-0.1.0
    template:
        metadata:
            labels:
                app.kubernetes.io/instance: {{{{ $.Values.podName }}}}
                app.kubernetes.io/managed-by: Helm
                app.kubernetes.io/name: {chart_name}
                app.kubernetes.io/version: 1.16.0
                helm.sh/chart: {chart_name}-0.1.0
        spec:
            containers:
                - name: {{{{ .name }}}}
                  image: "{{{{ $.Values.image.repository }}}}:{{{{ $.Values.image.tag }}}}"
                  imagePullPolicy: {{{{ $.Values.image.pullPolicy }}}}
                  command: ["sh", "-c", "mkdir -p /run/sshd && /usr/sbin/sshd -D"]
                  workingDir: /usr/src/app
                  securityContext:
                    capabilities:
                        add: ["NET_ADMIN", "SYS_TIME"]
                    runAsUser: 0
                  ports:
                    - containerPort: {{{{ $.Values.service.port }}}}
            nodeSelector:
{{{{ toYaml $.Values.nodeSelector | nindent 14 }}}}
{{{{- end }}}}
"""



    values = load_yaml(values_path)

    values.update({
        "service": {
            "type": "NodePort",
            "port": 22
        },
        "nodes": [
            {"name": "node"}
        ],
        "image": {
            "pullPolicy": "Always",
            "repository": "buchillo/orch_ehu",
            "tag": "latest",
        },
    })


    write_yaml(service_path, new_service) 

    print("\n\033[92m[OK] Fichero service.yaml preparado\033[0m.")

    write_yaml(deployment_path, new_deployment)

    print("\033[92m[OK] Fichero deployment.yaml preparado\033[0m.")

    save_yaml(values_path, values)

    print("\033[92m[OK] Fichero values.yaml preparado\033[0m.")





