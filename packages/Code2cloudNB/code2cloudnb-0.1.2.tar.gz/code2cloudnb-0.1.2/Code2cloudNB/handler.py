import requests
import time
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential


def import_code_to_databricks(host, token, domain_name, target_path, filename, encoded_string):
    """
    Helper function to import jupyter notebook json content into Azure Databricks as a Notebook.
    Args:
        host: Databricks host URL.
        token: Databricks PAT (Personal Access Token).
        domain_name: your Databricks workspace name.
        target_path: Path in the workspace where the Notebook will be created.
        filename: Name of the Notebook you want.
        encoded_string: base64 encoded Jupyter notebook JSON content.
    """
    # First checking if the folder path exists, if so then skip, if not then create it.
    resp_1 = requests.post(
        f"{host}/api/2.0/workspace/mkdirs",
        headers={"Authorization": f"Bearer {token}"},
        json={"path": f"/Users/{domain_name}/{target_path}"}
    )

    if resp_1.status_code == 200:
        payload = {
            "path": f"/Users/{domain_name}/{target_path}/{filename}_notebook",
            "format": "JUPYTER",
            "language": "PYTHON",
            "content": encoded_string,
            "overwrite": True
        }

        resp_2 = requests.post(
            f"{host}/api/2.0/workspace/import",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json=payload
        )
        try:
            resp_2.raise_for_status()
            return {
                "status": resp_2.status_code,
                "message": resp_2.text,
                "location": f"/Users/{domain_name}/{target_path}/{filename}_notebook"
            }
        except requests.HTTPError as e:
            return {
                "error": e.errno,
                "message": f"Error in importing the notebook: {str(e)}-{resp_2.text}"
            }
    else:
        return{
            "error": resp_1.status_code,
            "message": resp_1.text
        }
    
def import_code_to_synapse(wName, target_path, filename, pool_name, notebook_json, api_version):
    """
    Helper function to import jupyter notebook json content as a Notebook into Azure Synapse Workspaces.
    Args:
        wName: Synapse Workspace name.
        target_path: Path in the workspace where the Notebook will be created.
        filename: Name of the Notebook you want.
        pool_name: Your Big Data pool name (Apache Spark Pool).
        notebook_json: Jupyter notebook JSON content.
        api_version: Synapse REST API Version.
    """
    creds = DefaultAzureCredential()
    token = creds.get_token("https://dev.azuresynapse.net/.default")

    notebook_name = f"{filename}_notebook"
    endpoint = f"https://{wName}.dev.azuresynapse.net"
    url = f"{endpoint}/notebooks/{notebook_name}?api-version={api_version}"

    props = {
        "nbformat": notebook_json["nbformat"],
        "nbformat_minor": notebook_json["nbformat_minor"],
        "cells": notebook_json["cells"],
        "metadata": notebook_json["metadata"],
        "bigDataPool": {
            "referenceName": pool_name,
            "type": "BigDataPoolReference"
        }
    }

    if target_path:
        props["folder"] = {"name": target_path}

    body = {
        "name": notebook_name,
        "properties": props
    }

    headers = {
        "Authorization": f"Bearer {token.token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    resp = requests.put(url, headers=headers, json=body)
    
    try:
        resp.raise_for_status()
        return {
            "status": resp.status_code,
            "message": f"Imported notebook {notebook_name} successfully !",
            "location": f"/{target_path}/{notebook_name}" if target_path else f"/{notebook_name}",
            "id": resp.json()["recordId"]
        }
    except requests.HTTPError as e:
        return {
            "error": f"{resp.status_code}: {str(e)}",
            "message": f"Error in importing the notebook : {resp.text}"
        }
    
def import_code_to_fabric(wID, target_path, filename, api_version, encoded_string):
    """
    Helper function to import jupyter notebook json content into Microsoft Fabric as a Notebook.
    Args:
        wID: Fabric Workspace ID.
        target_path: Path in the workspace where the Notebook will be created.
        filename: Name of the Notebook you want.
        api_version: Fabric REST API version.
        encoded_string: base64 encoded Jupyter notebook JSON content.
    """
    # ─── CONFIG ─────────────────────────────────────────────────────────────────────
    global folder_id
    MAX_RETRIES = 6
    WAIT_SECONDS = 10

    # ─── AUTHENTICATION ─────────────────────────────────────────────────────────────
    cred = ManagedIdentityCredential()
    token = cred.get_token("https://api.fabric.microsoft.com/.default").token
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # ─── CREATE FOLDER ──────────────────────────────────────────────────────────────
    folder_payload = {
        "displayName": target_path,
        "type": "Folder"
    }
    url = f"https://api.fabric.microsoft.com/{api_version}/workspaces/{wID}/folders"

    try:
        resp = requests.post(url, headers=headers, json=folder_payload)

        if resp.status_code in (200, 201):
            folder_id = resp.json().get('id')
        elif resp.status_code == 409 and "FolderDisplayNameAlreadyInUse" in resp.text:
            pass
    except requests.HTTPError as e:
        return {
            "error": resp.status_code,
            "message": resp.text
        }

    # ─── ENCODE NOTEBOOK FILE ───────────────────────────────────────────────────────
    notebook_payload = {
        "displayName": f"{filename}_notebook",
        "type": "Notebook",
        "folderId": folder_id,
        "definition": {
            "format": "ipynb",
            "parts": [{
                "path": "notebook-content.ipynb",
                "payload": encoded_string,
                "payloadType": "InlineBase64"
            }]
        }
    }

    nb_url = f"https://api.fabric.microsoft.com/{api_version}/workspaces/{wID}/notebooks"

    # ─── UPLOAD NOTEBOOK WITH RETRIES ───────────────────────────────────────────────
    try:
        for attempt in range(1, MAX_RETRIES + 1):
            resp = requests.post(nb_url, headers=headers, json=notebook_payload)
            resp.raise_for_status()

            if resp.status_code in (200, 201):
                break
            elif resp.status_code == 202:
                break
            elif resp.status_code == 400 and "ItemDisplayNameNotAvailableYet" in resp.text:
                time.sleep(WAIT_SECONDS)
            elif resp.status_code == 400 and "ItemDisplayNameAlreadyInUse" in resp.text:
                raise ValueError(f"Attempt {attempt}: Error {resp.status_code} - displayNmae already in use, please use a different Name !")
        else:
            print("⏱️ Max retries reached. Try again later.")
        
        if resp.status_code in (200, 201):
            return {
                "status": resp.status_code,
                "output": {
                    "result": resp.text,
                    "message": "Notebook deployed successfully."
                }
            }
        elif resp.status_code == 202:
            return {
                "status": resp.status_code,
                "output": {
                    "result": "Notebook not yet indexed, but it's deployed successfully.",
                    "message": "Notebook deployed successfully."
                }
            }
        elif resp.status_code == 400 and "ItemDisplayNameNotAvailableYet" in resp.text:
            raise RuntimeError(f"Error {resp.status_code}: May be the Notebook is deleted, so it's waiting to get available again.")
    
    except requests.HTTPError as e:
        return {
            "error": e.errno,
            "message": f"Error in importing the notebook : {resp.text}"
        }