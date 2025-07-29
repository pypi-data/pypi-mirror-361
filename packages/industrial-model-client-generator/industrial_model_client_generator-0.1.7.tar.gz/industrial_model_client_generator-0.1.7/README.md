# 🏭 Industrial Model Client Generator

A utility for generating client-specific configurations for industrial data models

## 📦 Overview

The `industrial_model_client_generator` package automates the generation of client configurations based on a set of input definitions.

## 🚀 Installation

```bash
pip install industrial-model-client-generator
```

## ⚙️ Configuration Guide

This project requires a generator-config.yaml file to be placed in the root directory where the script is executed. This file contains environment-specific settings such as Cognite credentials, data model configuration, and instance space mappings.

### Creating `generator-config.yaml`

```yaml
client_name: "TestingClientV2"
output_path: "output" # not required
client_mode: "async" # options: both, async, sync

cognite:
  project: "${CDF_PROJECT}"
  client_name: "${CDF_CLIENT_NAME}"
  base_url: "https://${CDF_CLUSTER}.cognitedata.com"
  credentials:
    client_credentials:
      token_url: "${CDF_TOKEN_URL}"
      client_id: "${CDF_CLIENT_ID}"
      client_secret: "${CDF_CLIENT_SECRET}"
      scopes: ["https://${CDF_CLUSTER}.cognitedata.com/.default"]

data_model:
  external_id: "${CDF_DATA_MODEL_EXTERNAL_ID}"
  space: "${CDF_DATA_MODEL_SPACE}"
  version: "${CDF_DATA_MODEL_VERSION}"

instance_space_configs: # not required
  - view_or_space_external_id: "GENERIC-COR-ALL-DMD"
    instance_spaces:
      - "REF-COR-ALL-DAT"
  - view_or_space_external_id: "Equipment"
    instance_spaces_prefix: "SAP-"
  - view_or_space_external_id: "FunctionalLocation"
    instance_spaces_prefix: "SAP-"
```

### 🔐 Setting the Variables

#### Option: `.env` File (Recommended)

Create a file named `.env` in the root of your project:

```env
CDF_PROJECT=cognite-dev
CDF_CLIENT_NAME=testing
CDF_CLUSTER=az-eastus-1
CDF_TOKEN_URL=https://login.microsoftonline.com/xxxx/oauth2/v2.0/token
CDF_CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
CDF_CLIENT_SECRET=your-client-secret
CDF_DATA_MODEL_EXTERNAL_ID=CogniteCore
CDF_DATA_MODEL_SPACE=cdf_cdm
CDF_DATA_MODEL_VERSION=v1

```

## 🚀 Usage

```python
from industrial_model_client_generator import generate

generate()

```
