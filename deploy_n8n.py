import requests
import json

API_URL = "http://n8n.72.61.195.108.sslip.io/api/v1"
HEADERS = {
    "X-N8N-API-KEY": "n8n_api_d7748877f03f212f266ca7f6a22ed6a0f8d77b2db972a8d847f35223cacec12fb1cffe21b2e6b441",
    "Content-Type": "application/json",
    "Accept": "application/json"
}
DIR = "/Users/STARTIDEA/.gemini/antigravity/scratch/startidea_os"

cred_id = "MU4yoPrZzzfRHbHb"
workflow_ids = {}

def deploy_workflow(filename):
    with open(f"{DIR}/{filename}", "r") as f:
        wf = json.load(f)
    print(f"Deploying {wf['name']}...")
    
    # Inject settings if missing
    if "settings" not in wf:
        wf["settings"] = {}
        
    for node in wf['nodes']:
        if node['type'].startswith("n8n-nodes-base.telegram"):
            node['credentials'] = {"telegramApi": {"id": cred_id, "name": "Telegram_Bot"}}
            
    r = requests.post(f"{API_URL}/workflows", headers=HEADERS, json=wf)
    if r.ok:
        wid = r.json().get("id")
        workflow_ids[wf['name']] = wid
        print(f"Success! ID: {wid}")
        return wid
    else:
        print(f"Error deploying {wf['name']}:", r.text)
        return None

deploy_workflow("21_SYS_LLM_Core_V3_Fix.json")
deploy_workflow("15_SUB_Accion_V3.json")
deploy_workflow("16_SUB_Validacion_Task_V3.json")
deploy_workflow("17_SUB_Hoy_Focus.json")
deploy_workflow("18_SUB_Interactive_Task.json")

with open(f"{DIR}/22_SUB_Idea_V3_Fix.json", "r") as f:
    idea_wf = json.load(f)
if "settings" not in idea_wf: idea_wf["settings"] = {}
for node in idea_wf['nodes']:
    if node['name'] == 'Llamar_LLM_Core':
        node['parameters']['workflowId'] = workflow_ids.get("SYS_LLM_Core_V3_Fix", "")
    if node['type'].startswith("n8n-nodes-base.telegram"):
        node['credentials'] = {"telegramApi": {"id": cred_id, "name": "Telegram_Bot"}}
        
r = requests.post(f"{API_URL}/workflows", headers=HEADERS, json=idea_wf)
if r.ok:
    workflow_ids["SUB_Idea_V3_Fix"] = r.json().get("id")
else:
    print("Error SUB_Idea:", r.text)

with open(f"{DIR}/12_HUB_Router_V3.json", "r") as f:
    router_wf = json.load(f)
if "settings" not in router_wf: router_wf["settings"] = {}
for node in router_wf['nodes']:
    if node['name'] == 'Ejecutar_Idea': node['parameters']['workflowId'] = workflow_ids.get("SUB_Idea_V3_Fix", "")
    if node['name'] == 'Ejecutar_Validacion': node['parameters']['workflowId'] = workflow_ids.get("SUB_Validacion_Task_V3", "")
    if node['name'] == 'Ejecutar_Accion': node['parameters']['workflowId'] = workflow_ids.get("SUB_Accion_V3", "")
    if node['name'] == 'Ejecutar_Hoy': node['parameters']['workflowId'] = workflow_ids.get("SUB_Hoy_Focus", "")
    if node['name'] == 'Ejecutar_Focus': node['parameters']['workflowId'] = workflow_ids.get("SUB_Hoy_Focus", "")
    if node['name'] == 'Ejecutar_Interactive_Done': node['parameters']['workflowId'] = workflow_ids.get("SUB_Interactive_Task", "")
    if node['name'] == 'Ejecutar_Interactive_Postpone': node['parameters']['workflowId'] = workflow_ids.get("SUB_Interactive_Task", "")
    if node['type'] == "n8n-nodes-base.telegramTrigger":
        node['credentials'] = {"telegramApi": {"id": cred_id, "name": "Telegram_Bot"}}

r = requests.post(f"{API_URL}/workflows", headers=HEADERS, json=router_wf)
if r.ok:
    router_id = r.json().get("id")
    print(f"Activating HUB_Main_Router (ID: {router_id})...")
    r2 = requests.post(f"{API_URL}/workflows/{router_id}/activate", headers=HEADERS)
    print("Activate status:", r2.status_code)
else:
    print("Error router:", r.text)

