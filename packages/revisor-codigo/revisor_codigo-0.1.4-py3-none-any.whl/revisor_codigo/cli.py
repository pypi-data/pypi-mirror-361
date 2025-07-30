#!/usr/bin/env python3
import sys
import json
import os

from git import Repo, SymbolicReference

# SDKs de LLM
from openai import OpenAI
import anthropic
from google import genai
from google.genai import types

from dotenv import load_dotenv

load_dotenv()
# --- COLETA DE DIFFS ---------------------------------------

def detect_remote_default_branch(repo):
    try:
        origin = repo.remotes.origin
    except Exception:
        return None
    for ref in origin.refs:
        if isinstance(ref, SymbolicReference) and ref.name.endswith('/HEAD'):
            return ref.reference.remote_head
    return None

def sanitize(s: str) -> str:
    return ''.join(ch if not (0xD800 <= ord(ch) <= 0xDFFF) else '?' for ch in s)

def collect_diffs(repo_path, target_branch_arg):
    repo = Repo(repo_path)
    if repo.bare:
        raise RuntimeError("Repositório vazio ou não encontrado em " + repo_path)

    # branch de origem = branch atual
    try:
        source = repo.active_branch.name
    except TypeError:
        raise RuntimeError("HEAD destacado; não há branch atual.")

    # branch de destino
    if target_branch_arg:
        target = target_branch_arg
    else:
        default = detect_remote_default_branch(repo) or 'main'
        target = default if default.startswith('origin/') else f'origin/{default}'

    rev_range = f"{target}..{source}"
    commits = list(repo.iter_commits(rev_range))
    if not commits:
        return []

    files = {}
    for commit in reversed(commits):
        parent = commit.parents[0] if commit.parents else None
        diffs = commit.diff(parent, create_patch=True)
        for diff in diffs:
            path = diff.a_path or diff.b_path
            raw_patch = diff.diff.decode('utf-8', errors='replace')
            patch = sanitize(raw_patch)
            mods = [l for l in patch.splitlines() if l.startswith('+') or l.startswith('-')]

            if path not in files:
                try:
                    raw_content = repo.git.show(f"{source}:{path}")
                    content = sanitize(raw_content)
                except Exception:
                    content = ""
                files[path] = {
                    "arquivo": path,
                    "conteudoArquivo": content,
                    "modificações": []
                }

            files[path]["modificações"].extend(mods)

    return list(files.values())

# --- CHAMADAS AOS PROVIDERS -------------------------------

def call_openai(model, system_prompt, diffs_json):
    print(diffs_json)
    # instância do cliente já com API key
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    print(system_prompt)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": json.dumps(diffs_json, ensure_ascii=False)}
        ],
    )
    return response.choices[0].message.content.strip()

def call_anthropic(model, system_prompt, diffs_json):
    client = anthropic.Client(api_key=os.getenv("ANTHROPIC_API_KEY"))
    prompt = [{
        "role": "user",
        "content": json.dumps(diffs_json, ensure_ascii=False)
    }]


    resp = client.messages.create(
        system=system_prompt,
        messages=prompt,
        temperature=0.2,
        model=model,
        max_tokens=8192
    )
    return resp.content[0].text


def call_gemini(model: str, system_prompt: str, diffs_json):
    client = genai.Client()
    response = client.models.generate_content(
        model=model,
        contents=json.dumps(diffs_json, ensure_ascii=False, indent=2),
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.3,
        ),
    )

    return response.text

# --- FLUXO PRINCIPAL ---------------------------------------

def main():
    repo_path = sys.argv[1] if len(sys.argv) > 1 else '.'
    cfg_path  = sys.argv[2] if len(sys.argv) > 2 else 'revisor.json'

    # carrega configuração
    with open(cfg_path, encoding='utf-8') as f:
        cfg = json.load(f)

    diffs = collect_diffs(repo_path, cfg.get("branchTarget"))
    if not diffs:
        print("Nenhuma modificação nova encontrada.")
        return

    provider = cfg.get("provider", "openai").lower()
    model    = cfg["model"]
    assistant_prompt = cfg.get("assistant", "")

    if provider == "openai":
        out = call_openai(model, assistant_prompt, diffs)
    elif provider == "anthropic":
        out = call_anthropic(model, assistant_prompt, diffs)
    elif provider in ("gemini", "google"):
        out = call_gemini(model, assistant_prompt, diffs)
    else:
        raise RuntimeError(f"Provider desconhecido: {provider}")

    print("\n=== AVALIAÇÃO DO LLM ===\n")
    print(out)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Erro:", e, file=sys.stderr)
        sys.exit(1)