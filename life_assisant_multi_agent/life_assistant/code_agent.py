import os
import subprocess
from utils.file_utils import read_json, write_json
from utils.llm_utils import run_llm

CODE_WORKSPACE = "workspace/"


def generate_code(payload: dict) -> str:
    spec = payload["data"]["spec"]
    filename = payload["data"]["filename"]
    code = run_llm(spec, model_name="codestral-mamba")
    file_path = os.path.join(CODE_WORKSPACE, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)
    return file_path

def modify_code(payload: dict) -> None:
    file_path = os.path.join(CODE_WORKSPACE, payload["data"]["filename"])
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    old = payload["data"].get("old", "")
    new = payload["data"].get("new", "")
    content = content.replace(old, new)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

def delete_code(payload: dict) -> None:
    file_path = os.path.join(CODE_WORKSPACE, payload["data"]["filename"])
    if os.path.exists(file_path):
        os.remove(file_path)

def run_code(payload: dict) -> str:
    file_path = os.path.join(CODE_WORKSPACE, payload["data"]["filename"])
    result = subprocess.run(["python", file_path], capture_output=True, text=True)
    return result.stdout

def handle(payload):
    action = payload.get("action")
    if action == "generate_code":
        generate_code(payload)
    elif action == "modify_code":
        modify_code(payload)
    elif action == "delete_code":
        delete_code(payload)
    elif action == "run_code":
        run_code(payload)
