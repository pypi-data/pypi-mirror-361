# Code2cloudNB

A Python package providing helper functions to programmatically import Jupyter notebook content into Azure Databricks, Azure Synapse and Microsoft Fabric workspaces via REST APIs.

## Features

- Create folders and import Jupyter notebooks into Azure Databricks workspace.
- Import Jupyter notebooks into Azure Synapse Analytics workspace with support for Big Data Pools.
- Create folders and import Jupyter notebooks into Microsoft Fabric workspace, linked to Azure Fabric Capacity.
- Handles authentication using Personal Access Tokens (PAT) for Databricks, Azure AD `DefaultAzureCredential` for Synapse and Azure AD `ManagedIdentityCredential` for Fabric.
- Returns detailed responses for success and error scenarios.

## Installation

Install via PyPI once published:

```bash
pip install Code2cloudNB
```

# Usage

## Importing a notebook into Azure Databricks

```python
import base64
from Code2cloudNB import import_code_to_databricks

# Your Databricks workspace info
host = "https://<databricks-instance>"
token = "<your-databricks-pat>"
domain_name = "<your-domain-or-username>"
target_path = "target/folder/path"
filename = "my_notebook"

# Load your notebook JSON file content and encode to base64
with open("notebook.ipynb", "rb") as f:
    notebook_content = f.read()
encoded_string = base64.b64encode(notebook_content).decode()

response = import_code_to_databricks(host, token, domain_name, target_path, filename, encoded_string)

print(response)
```

## Importing a notebook into Azure Synapse Analytics

```python
from Code2cloudNB import import_code_to_synapse
import json

wName = "<your-synapse-workspace-name>"
target_path = "target_folder"
filename = "my_notebook"
pool_name = "<your-big-data-pool-name>"
api_version = "2021-06-01" # example API version

# Load notebook JSON content as Python dict
with open("notebook.ipynb", "r") as f:
    notebook_json = json.load(f)

response = import_code_to_synapse(wName, target_path, filename, pool_name, notebook_json, api_version)

print(response)
```

## Importing a notebook into Microsoft Fabric

```python
import base64
from Code2cloudNB import import_code_to_fabric

wID = "<your-fabric-workspace-id>"
target_path = "<target-folder>"
filename = "my_notebook"
api_version = "v1" # example API version

# Load your notebook JSON file content and encode to base64
with open("notebook.ipynb", "rb") as f:
    notebook_content = f.read()
encoded_string = base64.b64encode(notebook_content).decode('utf-8')

response = import_code_to_fabric(wID, target_path, filename, api_version, encoded_string)

print(response)
```

# Prerequisites

- For Databricks import:
    - A valid **Personal Access Token (PAT)** with workspace permissions.
    - Databricks workspace URL.

- For Synapse import:
    - Azure CLI or environment configured for Azure authentication.
    - Appropriate **Azure AD role assignments** for accessing Synapse workspace.
    - `azure-identity` Python package installed for `DefaultAzureCredential` support.
    - [[Follow this link for step-by-step configuration details](https://learn.microsoft.com/en-us/azure/synapse-analytics/security/how-to-set-up-access-control#step-3-create-and-configure-your-synapse-workspace)]

- For Fabric import:
    - Azure environment or VM's Managed Identity configured for Azure authentication.
    - An `active(running)` Azure **Fabric Capacity**, linked to the Fabric workspace.
    - `azure-identity` Python package installed for `ManagedIdentityCredential` support.
    - Appropriate **Role assignments** for accessing Fabric workspace :
        - create an `Azure Security Group`.
        - add your `VM's object/principal ID (Managed Identity)` as the `member` of the group and keep yourself as the `owner`.
        - under the Fabric's `manage workspaces` tab, click `add people + group`, add your Security Group and grant it the `Contributor` role.
        - give it some time (~10-20mins) to propagate these permissions.
    - [[Resource](https://learn.microsoft.com/en-us/rest/api/fabric/notebook/items/create-notebook?tabs=HTTP)]

```bash
pip install azure-identity requests
```

# Error Handling

Each of the functions return dictionaries including HTTP status codes, results and error messages if any operation fails. Use these to troubleshoot or log issues.

# License

This project is licensed under the MIT License - see the [LICENSE] (LICENSE) file for details.

# Contributing

Feel free to open issues or submit pull requests to improve the package.

# Author

Antick Mazumder — antick.majumder@gmail.com