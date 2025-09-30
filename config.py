

# ---------------------- Config -----------------------------------

NODEPORT_MIN = 30000
NODEPORT_MAX = 32767

ERROR_MSG_INCOMPLETE_ANSIBLE_CONFIG = (
    "CONFIGURACIÓN INVÁLIDA: si un nodo está definido en el inventory, "
    "debe tener especificados tanto 'ansible_host' (IP) como 'ansible_port' (puerto)."
)
ERROR_MSG_MISSING_NODEK8S = (
    "CONFIGURACIÓN INVÁLIDA: todos los nodos a desplegar deben tener un 'nodok8s' asignado en el archivo inventory.yaml."
)
ERROR_MSG_INVALID_NODEK8S = (
    "El archivo inventory.yaml contiene nombres de 'nodo' que no existen en el 'nodo' de Kubernetes actual."
)
ERROR_MSG_GET_NODEPORTS_FAILED = (
    "Fallo al obtener NodePorts desde Kubernetes."
)
ERROR_MSG_CREATE_NAMESPACE = (
    "Fallo al crear el namespace:"
)
ERROR_MSG_GET_HELM_NAME = (
    "Fallo relacionado con el nombre del Helm Chart."
)
ERROR_MSG_INSTALL_HELM = (
    "Fallo al instalar el Helm Chart:"
)
ERROR_MSG_UNINSTALL_HELM = (
    "Fallo al desinstalar el Helm Chart."
)
WARNING_HELM_CONFLICT = (
    "Marca este nodo como desplegado rellenando los parámetros "
      "'ansible_host' y 'ansible_port', o bien cámbiale el nombre para evitar coincidencias."
)
