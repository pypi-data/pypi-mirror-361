import requests


def faasr_put_file(local_file, remote_file, server_name="", local_folder=".", remote_folder="."):
    print("put file wrapper!")
    request_json = {
        "ProcedureID": "faasr_put_file",
        "Arguments": {"local_file": local_file, 
                    "remote_file": remote_file,
                    "server_name": server_name,
                    "local_folder": local_folder,
                    "remote_folder": remote_folder},
    }
    r = requests.post("http://127.0.0.1:8000/faasr-action", json=request_json)
    

def faasr_get_file(local_file, remote_file, server_name="", local_folder=".", remote_folder="."):
    request_json = {
        "ProcedureID": "faasr_put_file",
        "Arguments": {"local_file": local_file, 
                    "remote_file": remote_file,
                    "server_name": server_name,
                    "local_folder": local_folder,
                    "remote_folder": remote_folder}
    }
    r = requests.post("http://127.0.0.1:8000/faasr-action", json=request_json)


def faasr_delete_file(remote_file, server_name="", remote_folder=""):
    request_json = {
        "ProcedureID": "faasr_delete_file",
        "Arguments": {"remote_file": remote_file, 
                    "server_name": server_name,
                    "remote_folder": remote_folder}
    }
    r = requests.post("http://127.0.0.1:8000/faasr-action", json=request_json)


def faasr_log(log_message):
    request_json = {
        "ProcedureID": "faasr_log",
        "Arguments": {"log_message": log_message}
    }
    r = requests.post("http://127.0.0.1:8000/faasr-action", json=request_json)


def faasr_get_folder_list(server_name="", faasr_prefix = ""):
    request_json = {
        "ProcedureID": "faasr_get_folder_list",
        "Arguments": {"server_name": server_name,
                     "faasr_prefix": faasr_prefix}
    }
    r = requests.post("http://127.0.0.1:8000/faasr-action", json=request_json)