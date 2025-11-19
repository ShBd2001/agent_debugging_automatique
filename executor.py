# executor.py
import subprocess
from pathlib import Path


def run_script(python_path: str, script_path: str):
    """
    Exécute un script Python avec l'interpréteur donné.
    Retourne (returncode, stdout, stderr).
    """
    python = Path(python_path)
    script = Path(script_path)

    if not python.exists():
        raise FileNotFoundError(f"Interpréteur Python introuvable : {python}")
    if not script.exists():
        raise FileNotFoundError(f"Script cible introuvable : {script}")

    result = subprocess.run(
        [str(python), str(script)],
        capture_output=True,
        text=True
    )

    return result.returncode, result.stdout, result.stderr
