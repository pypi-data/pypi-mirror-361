import os
import shutil
import subprocess
from pathlib import Path

from cognite.client import CogniteClient
from cognite.client.data_classes.data_modeling import View
from jinja2 import Environment, FileSystemLoader

from .config import Config
from .helpers import to_snake
from .models import ViewDefinition


def generate(config_path: Path | None = None) -> None:
    config = Config.from_config(config_path)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    env = Environment(loader=FileSystemLoader(current_dir + "/templates"))

    instance_space_configs_as_dict = {
        instance_space_config.view_or_space_external_id: instance_space_config
        for instance_space_config in config.instance_space_configs
    }
    view_definitions: list[ViewDefinition] = []

    views = _get_views(config)
    for view in sorted(views, key=lambda v: v.external_id):
        instance_space_config = instance_space_configs_as_dict.get(
            view.external_id
        ) or instance_space_configs_as_dict.get(view.space)

        view_definitions.append(
            ViewDefinition.from_view(
                view,
                instance_space_config,
            )
        )

    output_path = config.output_path or to_snake(config.client_name)

    os.makedirs(output_path, exist_ok=True)
    shutil.rmtree(output_path)

    os.makedirs(output_path, exist_ok=True)
    os.makedirs(output_path + "/models", exist_ok=True)
    with open(f"{output_path}/models/__init__.py", "w") as f:
        f.write("")

    os.makedirs(output_path + "/requests", exist_ok=True)
    with open(f"{output_path}/requests/__init__.py", "w") as f:
        f.write("")

    paths = {
        "__init__.j2": f"{output_path}/__init__.py",
        "clients_facade.j2": f"{output_path}/clients_facade.py",
        "requests_aggregation.j2": f"{output_path}/requests/aggregation.py",
        "requests_base.j2": f"{output_path}/requests/base.py",
        "requests_query.j2": f"{output_path}/requests/query.py",
        "requests_search.j2": f"{output_path}/requests/search.py",
        "models_aggregation.j2": f"{output_path}/models/aggregation.py",
        "models_entity.j2": f"{output_path}/models/entity.py",
        "models_entity_complete.j2": f"{output_path}/models/entity_complete.py",
        "models_search.j2": f"{output_path}/models/search.py",
    }

    if config.client_mode in ["both", "sync"]:
        paths["clients_sync.j2"] = f"{output_path}/clients_sync.py"

    if config.client_mode in ["both", "async"]:
        paths["clients_async.j2"] = f"{output_path}/clients_async.py"

    for template_name, path in paths.items():
        template = env.get_template(template_name)
        entities_content = template.render(
            {
                "view_definitions": view_definitions,
                "client_name": config.client_name,
                "client_mode": config.client_mode,
            }
        )

        with open(path, "w") as f:
            f.write(entities_content)

    subprocess.run(["ruff", "format", output_path])
    subprocess.run(["ruff", "check", "--fix", output_path])
    subprocess.run(["mypy", output_path])


def _get_views(config: Config) -> list[View]:
    cognite_client = CogniteClient.load(config.cognite.model_dump())
    data_model_id = config.data_model

    return (
        cognite_client.data_modeling.data_models.retrieve(
            ids=data_model_id.as_tuple(), inline_views=True
        )
        .latest_version()
        .views
    )
