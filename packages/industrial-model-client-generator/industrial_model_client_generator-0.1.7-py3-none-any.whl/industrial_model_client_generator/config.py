import os
from pathlib import Path
from string import Template
from typing import Literal

import yaml
from dotenv import load_dotenv
from industrial_model import DataModelId
from pydantic import BaseModel, Field

CONFIG_FILE = "generator-config.yaml"


class ClientCredentials(BaseModel):
    token_url: str
    client_id: str
    client_secret: str
    scopes: list[str]


class Credentials(BaseModel):
    client_credentials: ClientCredentials


class CogniteConfig(BaseModel):
    project: str
    client_name: str
    base_url: str
    credentials: Credentials


class InstanceSpaceConfig(BaseModel):
    view_or_space_external_id: str
    instance_spaces: list[str] | None = None
    instance_spaces_prefix: str | None = None


class Config(BaseModel):
    client_name: str
    output_path: str | None = None
    client_mode: Literal["both", "sync", "async"] = "both"

    cognite: CogniteConfig
    data_model: DataModelId
    instance_space_configs: list[InstanceSpaceConfig] = Field(
        default_factory=list[InstanceSpaceConfig]
    )

    @classmethod
    def from_config(cls, config_path: Path | None = None) -> "Config":
        load_dotenv(override=True)

        file_path = Path(CONFIG_FILE) if config_path is None else config_path

        env_sub_template = Template(file_path.read_text())
        file_env_parsed = env_sub_template.safe_substitute(dict(os.environ))

        value = yaml.safe_load(file_env_parsed)
        return Config.model_validate(value)
