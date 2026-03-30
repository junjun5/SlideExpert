# Copyright 2026 Google LLC
import asyncio
import datetime
import importlib
import inspect
import json
import logging
import warnings
from typing import Any

import click
import google.auth
import vertexai
from google.cloud import resourcemanager_v3
from google.iam.v1 import iam_policy_pb2, policy_pb2
from vertexai._genai import _agent_engines_utils
from vertexai._genai.types import AgentEngine, AgentEngineConfig, IdentityType

# Suppress google-cloud-storage version compatibility warning
warnings.filterwarnings(
    "ignore", category=FutureWarning, module="google.cloud.aiplatform"
)

def generate_class_methods_from_agent(agent_instance: Any) -> list[dict[str, Any]]:
    registered_operations = _agent_engines_utils._get_registered_operations(agent=agent_instance)
    class_methods_spec = _agent_engines_utils._generate_class_methods_spec_or_raise(
        agent=agent_instance, operations=registered_operations
    )
    return [_agent_engines_utils._to_dict(method_spec) for method_spec in class_methods_spec]

def parse_key_value_pairs(kv_string: str | None) -> dict[str, str]:
    result = {}
    if kv_string:
        for pair in kv_string.split(","):
            if "=" in pair:
                key, value = pair.split("=", 1)
                result[key.strip()] = value.strip()
    return result

def write_deployment_metadata(remote_agent: Any, metadata_file: str = "deployment_metadata.json") -> None:
    metadata = {
        "remote_agent_engine_id": remote_agent.api_resource.name,
        "deployment_target": "agent_engine",
        "deployment_timestamp": datetime.datetime.now().isoformat(),
    }
    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

def print_deployment_success(remote_agent: Any, location: str, project: str) -> None:
    resource_name_parts = remote_agent.api_resource.name.split("/")
    agent_engine_id = resource_name_parts[-1]
    print("\n✅ Deployment successful!")
    playground_url = f"https://console.cloud.google.com/vertex-ai/agents/agent-engines/locations/{location}/agent-engines/{agent_engine_id}/playground?project={project}"
    print(f"\n📊 Open Console Playground: {playground_url}\n")

@click.command()
@click.option("--project", default="YOUR_PROJECT_ID")
@click.option("--location", default="us-central1")
@click.option("--display-name", default="SlideExpert")
@click.option("--description", default="Googleブランドの美学に基づき、プロフェッショナルな日本ビジネススタイルのGoogle Slides資料を作成します。")
@click.option("--source-packages", multiple=True, default=["./slide_app"])
@click.option("--entrypoint-module", default="slide_app.agent_engine_app")
@click.option("--entrypoint-object", default="agent_engine")
@click.option("--requirements-file", default="slide_app/app_utils/.requirements.txt")
@click.option("--set-env-vars", default=None)
def deploy_agent_engine_app(project, location, display_name, description, source_packages, entrypoint_module, entrypoint_object, requirements_file, set_env_vars):
    logging.basicConfig(level=logging.INFO)
    env_vars = parse_key_value_pairs(set_env_vars)
    env_vars["MY_PROJECT_ID"] = project
    env_vars["GOOGLE_CLOUD_LOCATION"] = "global"

    vertexai.init(project=project, location=location)
    client = vertexai.Client(project=project, location=location)

    module = importlib.import_module(entrypoint_module)
    agent_instance = getattr(module, entrypoint_object)
    if inspect.iscoroutine(agent_instance):
        agent_instance = asyncio.run(agent_instance)
    
    class_methods_list = generate_class_methods_from_agent(agent_instance)

    config = AgentEngineConfig(
        display_name=display_name,
        description=description,
        source_packages=list(source_packages),
        entrypoint_module=entrypoint_module,
        entrypoint_object=entrypoint_object,
        class_methods=class_methods_list,
        env_vars=env_vars,
        requirements_file=requirements_file,
        # service_account="YOUR_SERVICE_ACCOUNT@YOUR_PROJECT_ID.iam.gserviceaccount.com",
        agent_framework="google-adk",
    )

    existing_agents = list(client.agent_engines.list())
    matching_agents = [a for a in existing_agents if a.api_resource.display_name == display_name]

    if matching_agents:
        print(f"\n🚀 Updating agent: {display_name}...")
        remote_agent = client.agent_engines.update(name=matching_agents[0].api_resource.name, config=config)
    else:
        print(f"\n🚀 Creating agent: {display_name}...")
        remote_agent = client.agent_engines.create(config=config)

    write_deployment_metadata(remote_agent)
    print_deployment_success(remote_agent, location, project)

if __name__ == "__main__":
    deploy_agent_engine_app()
