"""Despliega los workflows de Startidea OS en una instancia n8n autorizada."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import requests

from n8n_config import ConfigError, N8nConfig, load_n8n_config


DEPENDENCY_FILES = (
    "21_SYS_LLM_Core_V3_Fix.json",
    "15_SUB_Accion_V3.json",
    "16_SUB_Validacion_Task_V3.json",
    "17_SUB_Hoy_Focus.json",
    "18_SUB_Interactive_Task.json",
)
IDEA_FILE = "22_SUB_Idea_V3_Fix.json"
ROUTER_FILE = "12_HUB_Router_V3.json"
REQUEST_TIMEOUT = (5, 30)


def _workflow_path(config: N8nConfig, filename: str) -> Path:
    candidate = (config.workflow_dir / filename).resolve()
    if candidate.parent != config.workflow_dir:
        raise RuntimeError(f"Workflow fuera del directorio permitido: {filename}")
    return candidate


def _load_workflows(config: N8nConfig) -> dict[str, dict[str, Any]]:
    workflows: dict[str, dict[str, Any]] = {}
    for filename in (*DEPENDENCY_FILES, IDEA_FILE, ROUTER_FILE):
        with _workflow_path(config, filename).open(encoding="utf-8") as handle:
            workflow = json.load(handle)
        if not isinstance(workflow, dict) or not isinstance(workflow.get("nodes"), list):
            raise RuntimeError(f"Workflow inválido: {filename}")
        workflows[filename] = workflow
    return workflows


def _create_workflow(
    session: requests.Session,
    config: N8nConfig,
    workflow: dict[str, Any],
) -> str:
    name = str(workflow.get("name") or "sin nombre")
    print(f"Deploying {name}...")
    response = session.post(
        f"{config.api_url}/workflows",
        json=workflow,
        timeout=REQUEST_TIMEOUT,
    )
    if not response.ok:
        raise RuntimeError(f"Error desplegando {name}: HTTP {response.status_code}")
    workflow_id = response.json().get("id")
    if not workflow_id:
        raise RuntimeError(f"n8n no devolvió id para {name}")
    print(f"Success! ID: {workflow_id}")
    return str(workflow_id)


def _inject_telegram_credentials(
    workflow: dict[str, Any],
    credential_id: str,
    *,
    trigger_only: bool = False,
) -> None:
    workflow.setdefault("settings", {})
    for node in workflow["nodes"]:
        node_type = str(node.get("type", ""))
        matches = (
            node_type == "n8n-nodes-base.telegramTrigger"
            if trigger_only
            else node_type.startswith("n8n-nodes-base.telegram")
        )
        if matches:
            node["credentials"] = {
                "telegramApi": {"id": credential_id, "name": "Telegram_Bot"},
            }


def deploy_all(config: N8nConfig) -> None:
    # Validar todos los ficheros antes de realizar la primera escritura remota.
    workflows = _load_workflows(config)
    workflow_ids: dict[str, str] = {}

    with requests.Session() as session:
        session.headers.update(
            {
                "X-N8N-API-KEY": config.api_key,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )

        for filename in DEPENDENCY_FILES:
            workflow = workflows[filename]
            _inject_telegram_credentials(workflow, config.telegram_credential_id)
            workflow_ids[str(workflow.get("name"))] = _create_workflow(
                session,
                config,
                workflow,
            )

        idea_workflow = workflows[IDEA_FILE]
        _inject_telegram_credentials(idea_workflow, config.telegram_credential_id)
        for node in idea_workflow["nodes"]:
            if node.get("name") == "Llamar_LLM_Core":
                node["parameters"]["workflowId"] = workflow_ids.get(
                    "SYS_LLM_Core_V3_Fix",
                    "",
                )
        workflow_ids["SUB_Idea_V3_Fix"] = _create_workflow(
            session,
            config,
            idea_workflow,
        )

        router_workflow = workflows[ROUTER_FILE]
        _inject_telegram_credentials(
            router_workflow,
            config.telegram_credential_id,
            trigger_only=True,
        )
        dependency_names = {
            "Ejecutar_Idea": "SUB_Idea_V3_Fix",
            "Ejecutar_Validacion": "SUB_Validacion_Task_V3",
            "Ejecutar_Accion": "SUB_Accion_V3",
            "Ejecutar_Hoy": "SUB_Hoy_Focus",
            "Ejecutar_Focus": "SUB_Hoy_Focus",
            "Ejecutar_Interactive_Done": "SUB_Interactive_Task",
            "Ejecutar_Interactive_Postpone": "SUB_Interactive_Task",
        }
        for node in router_workflow["nodes"]:
            dependency = dependency_names.get(str(node.get("name")))
            if dependency:
                node["parameters"]["workflowId"] = workflow_ids.get(dependency, "")

        router_id = _create_workflow(session, config, router_workflow)
        print(f"Activating HUB_Main_Router (ID: {router_id})...")
        response = session.post(
            f"{config.api_url}/workflows/{router_id}/activate",
            timeout=REQUEST_TIMEOUT,
        )
        if not response.ok:
            raise RuntimeError(f"Error activando router: HTTP {response.status_code}")
        print(f"Activate status: {response.status_code}")


def main() -> int:
    try:
        deploy_all(load_n8n_config())
    except (ConfigError, OSError, json.JSONDecodeError, requests.RequestException, RuntimeError) as error:
        print(f"Despliegue abortado: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
