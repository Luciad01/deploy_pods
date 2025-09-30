# Script de despliegue automático de nodos Quditto en Kubernetes

Este script de **Python** automatiza el despliegue de los nodos de **Quditto** en un clúster de **Kubernetes (MicroK8s)** mediante **Helm Charts**.  
Su función principal es **leer el archivo `inventory.yaml` de Quditto**, desplegar los Pods correspondientes y actualizar dicho archivo con las direcciones IP y puertos necesarios para que Quditto pueda ejecutarse sin intervención manual.

---

## 📋 Requisitos
- Python 3.10 o superior  
- Un clúster Kubernetes (en este caso, **MicroK8s**) 
- La librería **PyYAML**:  

  El script necesita leer y escribir archivos YAML, y eso se implementa con la librería `yaml` en Python.  
  Esta librería no viene instalada por defecto, corresponde al paquete **PyYAML** que se instala con:

  ```bash
  pip install pyyaml
  ```

---

## ⚙️ Uso

### 1. Preparar el archivo `inventory.yaml` de Quditto
- Define los nodos que quieras desplegar, indicando al menos el campo `nodek8s` con el nombre del nodo de Kubernetes.  
- También puedes especificar el resto de parámetros necesarios que aparecen en los ejemplos del README general de Quditto y en las plantillas de la carpeta **Tutorial**.
- Si un nodo ya tiene definidos `ansible_host` y `ansible_port` (y no tiene `nodek8s`), el script lo considerará como **ya desplegado** y no lo tocará.

Ejemplo:
```yaml
nodo_qd2:
  ansible_connection: ssh
  ansible_user: ubuntu
  ansible_ssh_pass: 1234
  py_env: /usr/bin/python3
  nodek8s: nodo_k8s
```

---

### 2. Crear un Helm Chart base
El script necesita un chart para desplegar los Pods. Para crearlo con MicroK8s:

```bash
# Crear el chart en el directorio actual
microk8s helm3 create <nombre>

# Crear el chart en una ruta relativa (la ruta se crea si no existe)
microk8s helm3 create ./ruta/<nombre>

# Crear el chart en una ruta absoluta
microk8s helm3 create /opt/charts/<nombre>
```

Este comando genera la estructura básica del chart (`Chart.yaml`, `values.yaml` y el directorio `templates/`, entre otros). Una vez creado, el **script adecuará automáticamente** los ficheros necesarios antes de proceder al despliegue.

---

### 3. Ejecutar el script
El comando requiere dos parámetros:  
- La ruta al archivo `inventory.yaml`  
- La ruta al directorio del Helm Chart

```bash
python3 deploy_quditto.py inventory.yaml ./helm_chart
```
---

## 🧪 Relación con Quditto
Una vez actualizado el `inventory.yaml` por el script, simplemente sigue los **requerimientos habituales de Quditto** para lanzarlo.

Para comprobar que los pods creados que actúan como nodos qd2 están ejecutándose correctamente, se debe ejecutar el comando:

```bash
# Para un namespace concreto*
microk8s kubectl get pods -n <nodo_k8s> 

# Para un namespace concreto*
microk8s kubectl get pods -A
```

El pod estará corriendo correctamente si su status es **RUNNING**.

* `El namespace al que pertenezca un nodo qd2 será el nombre del nodode kubernetes al que pertenezca añadiendole -ns (ej.: para ejemploNodo será ejemploNodo-ns)`

---