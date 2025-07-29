# mcp_modules_pkg/credentials/__init__.py
import os
import json
from pathlib import Path

def get_credentials_path():
    """크리덴셜 파일들이 있는 디렉토리 경로 반환"""
    return Path(__file__).parent

def get_credential_file(filename: str):
    """특정 크리덴셜 파일의 전체 경로 반환"""
    credentials_dir = get_credentials_path()
    file_path = credentials_dir / filename
    
    if not file_path.exists():
        raise FileNotFoundError(f"Credential file not found: {filename}")
    
    return str(file_path)

def load_json_credentials(filename: str):
    """JSON 크리덴셜 파일 로드 (gspread.json 같은 파일용)"""
    file_path = get_credential_file(filename)
    with open(file_path, 'r') as f:
        return json.load(f)

def list_credential_files():
    """사용 가능한 크리덴셜 파일들 목록 반환"""
    credentials_dir = get_credentials_path()
    return [f.name for f in credentials_dir.iterdir() if f.is_file() and not f.name.startswith('__')]

__all__ = [
    "get_credentials_path",
    "get_credential_file", 
    "load_json_credentials",
    "list_credential_files",
]