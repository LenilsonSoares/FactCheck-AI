import os
import subprocess
import sys


def check_model_files():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    ml_dir = os.path.join(repo_root, "backend", "app", "ml_models")
    candidates = [
        os.path.join(ml_dir, "modelo.pkl"),
        os.path.join(ml_dir, "model.pkl"),
    ]

    found = None
    for p in candidates:
        if os.path.exists(p) and os.path.getsize(p) > 0:
            found = p
            break

    return found, candidates


def retrain():
    print("Iniciando treino do modelo via scripts/train_model.py...")
    cmd = [sys.executable, os.path.join(os.path.dirname(__file__), "train_model.py")]
    res = subprocess.run(cmd, check=False)
    return res.returncode == 0


def main():
    found, candidates = check_model_files()
    if found:
        print(f"Modelo detectado: {found} (tamanho OK)")
        return 0

    print(f"Nenhum modelo válido encontrado. Tentei: {candidates}")
    ok = retrain()
    if ok:
        print("Treino concluído com sucesso. Verifique backend/app/ml_models/")
        return 0
    else:
        print("Falha ao treinar o modelo. Verifique a saída do script de treino.")
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
