import subprocess
import importlib.metadata
from packaging import version
import os
import sys
import re
import argparse
import requests

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:
    import tomli as tomllib  # para Python 3.10 e anteriores com tomli instalado

def load_config(filename="pyproject.toml"):
    with open(filename, "rb") as f:
        data = tomllib.load(f)
    # Extrair a seção [project]
    return data.get("project", {})

def get_versao_instalada(pacote):
    try:
        return importlib.metadata.version(pacote)
    except importlib.metadata.PackageNotFoundError:
        return None

def precisa_atualizar(instalada, requerida, operador):
    try:
        v_inst = version.parse(instalada)
        v_req = version.parse(requerida)
        match operador:
            case "==":
                return v_inst != v_req
            case "!=":
                return v_inst == v_req
            case ">=":
                return v_inst < v_req
            case "<=":
                return v_inst > v_req
            case ">":
                return v_inst <= v_req
            case "<":
                return v_inst >= v_req 
            case "~=":
                if v_inst < v_req:
                    return True
                if v_inst.major != v_req.major:
                    return True
                if v_inst.minor < getattr(v_req, 'minor', 0):
                    return True
                return False
            case _:
                return True
    except Exception as e:
        print(f"[!] Erro ao comparar versões: {e}")
        return True

def parse_linha(linha):
    linha = linha.strip()
    if not linha or linha.startswith("#"):
        return None, None, None

    pattern = r'^([a-zA-Z0-9_\-\.\[\]]+)\s*([<>=!~]{1,2})?\s*([\w\.\*]+)?'
    match_re = re.match(pattern, linha)
    if not match_re:
        return linha, None, None

    nome = match_re.group(1)
    operador = match_re.group(2)
    versao = match_re.group(3)

    if operador and not versao:
        return nome, operador, None

    return nome, operador, versao

def instalar_ou_verificar(linha, dry_run=False):
    nome, operador, versao_requerida = parse_linha(linha)
    if nome is None:
        return

    nome_base = nome.split('[')[0]
    instalada = get_versao_instalada(nome_base)

    if instalada is None:
        print(f"[!] {nome} não está instalado.")
        if not dry_run:
            print(f"    Instalando...")
            subprocess.run([sys.executable, "-m", "pip", "install", linha])
    else:
        if operador and versao_requerida:
            if precisa_atualizar(instalada, versao_requerida, operador):
                print(f"[↑] {nome:<30} - versão {instalada}, requer {operador} {versao_requerida}.")
                if not dry_run:
                    print("    Atualizando...")
                    subprocess.run([sys.executable, "-m", "pip", "install", linha])
            else:
                print(f"[✓] {nome:<30} - versão {instalada} satisfaz a versão requerida.")
        else:
            print(f"[✓] {nome:<30} - instalado na versão {instalada}.")

def processar_requirements(caminho="requirements.txt", dry_run=False):
    if not os.path.exists(caminho):
        print(f"[✗] Arquivo '{caminho}' não encontrado.")
        return

    with open(caminho, "r") as file:
        for linha in file:
            linha = linha.strip()
            if linha and not linha.startswith("#"):
                instalar_ou_verificar(linha, dry_run)

def checar_atualizacao(nome_pacote: str, versao_atual: str):
    try:
        url = f"https://pypi.org/pypi/{nome_pacote}/json"
        resposta = requests.get(url, timeout=5)
        if resposta.status_code == 200:
            dados = resposta.json()
            ultima_versao = dados["info"]["version"]
            if ultima_versao != versao_atual:
                print(f"[↑] Versão mais recente disponível: {ultima_versao} (você está com {versao_atual})")
                print(f"    Atualize com: pip install --upgrade {nome_pacote}")
            else:
                print(f"[✓] Você já está usando a versão mais recente: {versao_atual}")
        else:
            print("[!] Não foi possível acessar o PyPI para verificar atualizações.")
    except Exception as e:
        print(f"[!] Erro ao verificar atualizações: {e}")

def main():
    config = load_config()  # lê pyproject.toml e pega a seção [project]

    desc = config.get("description")
    # No pyproject.toml description é string, ou pode ser lista? No seu exemplo é string, então já pode usar direto
    if isinstance(desc, list):
        desc = " ".join([linha.strip() for linha in desc if linha.strip()])
    else:
        desc = desc or "Instalador inteligente de dependências."

    parser = argparse.ArgumentParser(description=desc, add_help=False)
    parser.add_argument("--help", "-h", action="help", help="Show this help message / Mostrar esta mensagem de ajuda")
    parser.add_argument("--file", "-f", default="requirements.txt", help="Requirements file (default: requirements.txt) / Arquivo de requisitos (padrão: requirements.txt)")
    parser.add_argument("--dry-run", "-d", action="store_true", help="Dry run (do not install anything) / Executar em modo simulado (sem instalar nada)")
    parser.add_argument("--version", "-v", action="store_true", help="Show version / Mostrar versão")
    parser.add_argument("--changelog", "-c", action="store_true", help="Show changelog / Mostrar changelog")
    parser.add_argument("--description", action="store_true", help="Show project description / Mostrar descrição do projeto")
    parser.add_argument("--check-update", "-u", action="store_true", help="Verificar se há nova versão no PyPI / Check for update on PyPI")
    args = parser.parse_args()

    if args.version:
        print(f"{config['name']} versão {config['version']}")
        return

    if args.changelog:
        changelog = config.get("dynamic", {}).get("changelog") or config.get("changelog")
        if changelog and isinstance(changelog, list):
            print("Changelog:")
            for item in changelog:
                print(f"- {item}")
        else:
            print("[!] Nenhuma entrada de changelog encontrada.")
        return

    if args.description:
        desc = config.get("description")
        print("Descrição:")
        if isinstance(desc, list):
            for linha in desc:
                print(f"- {linha}")
        else:
            print(f"- {desc}")
        return

    if args.check_update:
        checar_atualizacao(config["name"], config["version"])
        return

    # Se não for versão nem changelog, processa os requirements
    processar_requirements(caminho=args.file, dry_run=args.dry_run)

def cli():
    main()
