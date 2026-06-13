#!/usr/bin/env python3
"""
Upload da pasta scratch/ para o GitHub via API REST.
Uso: python3 upload_scratch.py SEU_TOKEN_AQUI
"""

import sys
import os
import base64
import json
import urllib.request
import urllib.error
import time

OWNER = "junicoders"
REPO  = "junicoders-platform"
BRANCH = "main"
LOCAL_FOLDER = os.path.join(os.path.dirname(__file__), "scratch")

def github_api(method, endpoint, token, data=None):
    url = f"https://api.github.com{endpoint}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read())

def get_sha(path, token):
    """Get existing file SHA (needed to update)."""
    r = github_api("GET", f"/repos/{OWNER}/{REPO}/contents/{path}?ref={BRANCH}", token)
    return r.get("sha")

def upload_file(local_path, repo_path, token):
    with open(local_path, "rb") as f:
        content = base64.b64encode(f.read()).decode()
    sha = get_sha(repo_path, token)
    payload = {
        "message": f"Upload {repo_path}",
        "content": content,
        "branch": BRANCH,
    }
    if sha:
        payload["sha"] = sha
    r = github_api("PUT", f"/repos/{OWNER}/{REPO}/contents/{repo_path}", token, payload)
    return "content" in r

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 upload_scratch.py SEU_TOKEN_AQUI")
        print()
        print("Como criar o token:")
        print("  1. Vai a https://github.com/settings/tokens/new")
        print("  2. Dá um nome (ex: 'junicoders upload')")
        print("  3. Seleciona 'repo' (acesso total ao repositório)")
        print("  4. Clica 'Generate token' e copia o token")
        sys.exit(1)

    token = sys.argv[1]

    # Collect all files
    files = []
    for root, dirs, filenames in os.walk(LOCAL_FOLDER):
        for fname in filenames:
            if fname.endswith(".map"):
                continue  # skip source maps
            local = os.path.join(root, fname)
            rel = os.path.relpath(local, os.path.dirname(LOCAL_FOLDER))
            repo_path = rel.replace("\\", "/")
            files.append((local, repo_path))

    total = len(files)
    print(f"A fazer upload de {total} ficheiros para {OWNER}/{REPO}...")
    print()

    ok = 0
    fail = 0
    for i, (local, repo_path) in enumerate(files, 1):
        size = os.path.getsize(local)
        print(f"[{i}/{total}] {repo_path} ({size//1024}KB)...", end=" ", flush=True)
        try:
            if upload_file(local, repo_path, token):
                print("✓")
                ok += 1
            else:
                print("✗ erro")
                fail += 1
        except Exception as e:
            print(f"✗ {e}")
            fail += 1
        # Small delay to avoid rate limiting
        if i % 10 == 0:
            time.sleep(1)

    print()
    print(f"Concluído: {ok} ficheiros enviados, {fail} erros.")
    if fail == 0:
        print(f"\n✅ Acede a https://{OWNER}.github.io/{REPO}/ daqui a 1-2 minutos!")
