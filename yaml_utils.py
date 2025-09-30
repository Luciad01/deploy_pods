
import yaml


# ---------------------- YAML Utilities ---------------------------

def load_yaml(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)



def save_yaml(file_path, data):
    with open(file_path, 'w') as file:
        yaml.dump(data, file, default_flow_style=False)



def readlines_yaml(file_path):
    with open(file_path, 'r') as file:
        return file.readlines()



def write_yaml(file_path, data):
    with open(file_path, 'w') as file:
        file.write(data)

