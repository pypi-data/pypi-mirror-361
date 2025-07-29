import subprocess
import sys
import time
import pytest
import tempfile
import os
import zipfile
import json
import re
import random
import click
import ast

def run_cli_command(args, input_text=None):
    """
    adxp_cli.model.cli를 subprocess로 실행하고 결과를 반환합니다.
    """
    cmd = [sys.executable, '-m', 'adxp_cli.model.cli'] + args
    result = subprocess.run(cmd, capture_output=True, text=True, input=input_text)
    print(f"\n[STDOUT]\n{result.stdout}\n[STDERR]\n{result.stderr}")  # 항상 출력
    return result

def generate_random_name(prefix):
    return f"{prefix}_{random.randint(100000, 999999)}"

def extract_id_from_output(output):
    # JSON-like dict에서 id 추출
    match = re.search(r"'id': '([\w-]+)'", output)
    if match:
        return match.group(1)
    # JSON 문자열에서 id 추출
    match = re.search(r'"id"\s*:\s*"([\w-]+)"', output)
    if match:
        return match.group(1)
    return None

@pytest.fixture(scope="module")
def provider_id():
    # Provider CRUD 테스트에서 생성한 provider_id를 공유
    name = generate_random_name("sdk_cli_test_provider")
    desc = name
    logo = name
    # create
    result = run_cli_command([
        "model", "provider", "create",
        "--name", name,
        "--description", desc,
        "--logo", logo
    ])
    assert result.returncode == 0
    pid = extract_id_from_output(result.stdout)
    assert pid is not None
    click.secho("✅ Provider created successfully", fg="green")
    yield pid
    # delete (clean up)
    run_cli_command(["model", "provider", "delete", pid])

def test_cli_provider_crud():
    name = generate_random_name("sdk_cli_test_provider")
    desc = name
    logo = name
    # create
    result = run_cli_command([
        "model", "provider", "create",
        "--name", name,
        "--description", desc,
        "--logo", logo
    ])
    assert result.returncode == 0
    pid = extract_id_from_output(result.stdout)
    assert pid is not None
    # get
    result = run_cli_command(["model", "provider", "get", pid])
    assert result.returncode == 0
    assert pid in result.stdout
    # list
    result = run_cli_command(["model", "provider", "list"])
    assert result.returncode == 0
    assert pid in result.stdout
    # update
    new_name = name + "_updated"
    result = run_cli_command([
        "model", "provider", "update", "--name", new_name, "--description", new_name, "--logo", new_name, pid
    ])
    assert result.returncode == 0
    # delete
    result = run_cli_command(["model", "provider", "delete", pid])
    assert result.returncode == 0

def test_cli_serverless_model(provider_id):
    # 타입/태그 조회
    result = run_cli_command(["model", "type-list"])
    assert result.returncode == 0
    result = run_cli_command(["model", "tag-list"])
    assert result.returncode == 0
    # 모델 생성
    model_name = generate_random_name("sdk_cli_serverless_model")
    model_data = {
        "display_name": model_name,
        "name": model_name,
        "type": "language",
        "description": model_name + " description",
        "serving_type": "serverless",
        "provider_id": provider_id,
        "languages": [{"name": "Korean"}],
        "tasks": [{"name": "completion"}],
        "tags": [{"name": "tag"}],
        "policy": [{
            "decision_strategy": "UNANIMOUS",
            "logic": "POSITIVE",
            "policies": [{"logic": "POSITIVE", "names": ["admin"], "type": "user"}],
            "scopes": ["GET", "POST", "PUT", "DELETE"]
        }]
    }
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as f:
        json.dump(model_data, f)
        f.flush()
        model_json_path = f.name
    result = run_cli_command(["model", "create", "--json", model_json_path])
    os.remove(model_json_path)
    assert result.returncode == 0
    model_id = extract_id_from_output(result.stdout)
    assert model_id is not None
    # 모델 수정
    model_data["description"] = model_name + " description updated"
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as f:
        json.dump(model_data, f)
        f.flush()
        model_json_path = f.name
    result = run_cli_command(["model", "update", "--json", model_json_path, model_id])
    # 모델 목록
    result = run_cli_command(["model", "list"])
    assert result.returncode == 0
    assert model_id in result.stdout
    # 모델 단건
    result = run_cli_command(["model", "get", model_id])
    assert result.returncode == 0
    assert model_id in result.stdout
    # 태그 추가/삭제
    result = run_cli_command(["model", "tag-add", model_id, "tag1", "tag2"])
    assert result.returncode == 0
    result = run_cli_command(["model", "tag-remove", model_id, "tag1"])
    assert result.returncode == 0
    # 언어 추가/삭제
    result = run_cli_command(["model", "lang-add", model_id, "English", "Japanese"])
    assert result.returncode == 0
    result = run_cli_command(["model", "lang-remove", model_id, "English"])
    assert result.returncode == 0
    # 태스크 추가/삭제
    result = run_cli_command(["model", "task-add", model_id, "translation", "summarization"])
    assert result.returncode == 0
    result = run_cli_command(["model", "task-remove", model_id, "translation"])
    assert result.returncode == 0
    # 엔드포인트 등록
    endpoint_data = {
        "url": "https://api.example.com/v1/models/" + model_name,
        "identifier": model_name,
        "key": model_name,
        "description": model_name + " endpoint"
    }
    result = run_cli_command([
        "model", "endpoint", "create", model_id,
        "--url", endpoint_data["url"],
        "--identifier", endpoint_data["identifier"],
        "--key", endpoint_data["key"],
        "--description", endpoint_data["description"]
    ])
    assert result.returncode == 0
    endpoint_id = extract_id_from_output(result.stdout)
    assert endpoint_id is not None
    # 엔드포인트 목록
    result = run_cli_command(["model", "endpoint", "list", model_id])
    assert result.returncode == 0
    assert endpoint_id in result.stdout
    # 엔드포인트 단건
    result = run_cli_command(["model", "endpoint", "get", model_id, endpoint_id])
    assert result.returncode == 0
    assert endpoint_id in result.stdout
    # 엔드포인트 삭제
    result = run_cli_command(["model", "endpoint", "delete", model_id, endpoint_id])
    assert result.returncode == 0
    # 모델 삭제/복구/재삭제
    result = run_cli_command(["model", "delete", model_id])
    assert result.returncode == 0
    result = run_cli_command(["model", "recover", model_id])
    assert result.returncode == 0
    result = run_cli_command(["model", "delete", model_id])
    assert result.returncode == 0

def test_cli_selfhosting_custom_model(provider_id):
    # 모델 파일 업로드 (upload 명령어가 cli.py에 있음)
    with tempfile.NamedTemporaryFile(suffix=".zip", dir="/tmp", delete=False) as tmp:
        model_zip_path = tmp.name
    with zipfile.ZipFile(model_zip_path, 'w') as zipf:
        zipf.writestr("dummy.txt", "hello zip content")
    result = run_cli_command(["model", "upload", model_zip_path])
    os.remove(model_zip_path)
    assert result.returncode == 0
    model_path = None
    try:
        # 파이썬 딕셔너리 문자열을 dict로 변환
        output_dict = ast.literal_eval(result.stdout.splitlines()[-1])
        model_path = output_dict.get("temp_file_path")
    except Exception:
        # 기존 정규식도 fallback으로 시도
        match = re.search(r'"temp_file_path"\s*:\s*"([^"]+)"', result.stdout)
        if match:
            model_path = match.group(1)
    time.sleep(5)
    assert model_path is not None
    # 커스텀 코드 파일 업로드 (upload-code 명령어가 custom_runtime_group에 있음)
    with tempfile.NamedTemporaryFile(suffix=".zip", dir="/tmp", delete=False) as tmp:
        code_zip_path = tmp.name
    with zipfile.ZipFile(code_zip_path, 'w') as zipf:
        zipf.writestr("dummy_code.py", "print('hello')")
    result = run_cli_command(["model", "custom-runtime", "upload-code", "--file-path", code_zip_path])
    os.remove(code_zip_path)
    assert result.returncode == 0
    custom_code_path = None
    try:
        output_dict = ast.literal_eval(result.stdout.splitlines()[-1])
        custom_code_path = output_dict.get("temp_file_path")
    except Exception:
        # 기존 정규식도 fallback으로 시도
        match = re.search(r'"temp_file_path"\s*:\s*"([^"]+)"', result.stdout)
        if match:
            custom_code_path = match.group(1)
    time.sleep(5)
    assert custom_code_path is not None
    # 모델 생성
    model_name = generate_random_name("sdk_cli_selfhosting_model")
    model_data = {
        "display_name": model_name,
        "name": model_name,
        "type": "language",
        "description": model_name + " description",
        "serving_type": "self-hosting",
        "is_private": False,
        "provider_id": provider_id,
        "is_custom": True,
        "path": model_path,
        "custom_code_path": custom_code_path,
        "languages": [{"name": "English"}],
        "tasks": [{"name": "completion"}],
        "tags": [{"name": "tag1"}],
        "policy": [{
            "decision_strategy": "UNANIMOUS",
            "logic": "POSITIVE",
            "policies": [{"logic": "POSITIVE", "names": ["admin"], "type": "user"}],
            "scopes": ["GET", "POST", "PUT", "DELETE"]
        }]
    }
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as f:
        json.dump(model_data, f)
        f.flush()
        model_json_path = f.name
    result = run_cli_command(["model", "create", "--json", model_json_path])
    os.remove(model_json_path)
    assert result.returncode == 0
    model_id = extract_id_from_output(result.stdout)
    assert model_id is not None
    # 커스텀 런타임 생성
    result = run_cli_command([
        "model", "custom-runtime", "create",
        "--model-id", model_id,
        "--image-url", "https://hub.docker.com/r/adxp/adxp-runtime-python/tags"
    ])
    assert result.returncode == 0
    # 커스텀 런타임 조회
    result = run_cli_command(["model", "custom-runtime", "get", "--model-id", model_id])
    assert result.returncode == 0
    # 커스텀 런타임 삭제
    result = run_cli_command(["model", "custom-runtime", "delete", "--model-id", model_id])
    assert result.returncode == 0
    # 모델 삭제
    result = run_cli_command(["model", "delete", model_id])
    assert result.returncode == 0 