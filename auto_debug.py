# auto_debug.py
import sys
from pathlib import Path
from typing import List, Dict, Any

from executor import run_script
from ai_client import AIDebuggerClient
from patcher import apply_patches


def auto_debug(python_path: str, script_path: str, max_iterations: int = 30) -> tuple[list[str], list[dict]]:
    """
    Tente de corriger automatiquement un script Python en plusieurs itérations :
    - exécute le script
    - envoie l'erreur + le code à l'IA
    - applique les patchs
    - recommence, jusqu'à ce que le script s'exécute sans erreur ou que max_iterations soit atteint.

    Retourne :
    - logs : liste de chaînes de caractères à afficher (stdout, stderr, messages)
    - ia_history : liste de dicts contenant les explications / patchs de l'IA par itération
    """
    logs: List[str] = []
    ia_history: List[Dict[str, Any]] = []

    script = Path(script_path)
    if not script.exists():
        logs.append(f"[ERREUR] Script introuvable : {script}")
        return logs, ia_history

    try:
        client = AIDebuggerClient()
    except Exception as e:
        logs.append(f"[ERREUR] Impossible de créer le client IA : {e}")
        return logs, ia_history

    for iteration in range(1, max_iterations + 1):
        logs.append(f"\n===== ITÉRATION {iteration}/{max_iterations} =====")

        # Exécution du script
        try:
            rc, stdout, stderr = run_script(python_path, script_path)
        except Exception as e:
            logs.append(f"[ERREUR] Impossible d'exécuter le script : {e}")
            return logs, ia_history

        logs.append(f"[INFO] Code retour : {rc}")

        if stdout:
            logs.append("\n--- STDOUT ---")
            logs.append(stdout)

        # Si pas d'erreur sur stderr
        if not stderr or stderr.strip() == "":
            logs.append("\n✅ Aucune erreur détectée (stderr vide).")
            if rc == 0:
                logs.append("✅ Le script semble s'exécuter correctement. Arrêt de l'auto-debug.")
            else:
                logs.append("⚠️ Pas d'erreur sur stderr mais code retour non nul. Arrêt.")
            return logs, ia_history

        logs.append("\n--- STDERR (erreur) ---")
        logs.append(stderr)

        # Appel à l'IA pour obtenir un patch
        try:
            code = script.read_text(encoding="utf-8")
            data = client.get_correction(code, stderr)
        except Exception as e:
            logs.append(f"[ERREUR] Échec de l'appel à l'IA : {e}")
            return logs, ia_history

        patch = data.get("patch", [])
        if not patch:
            logs.append("\n⚠️ L'IA n'a proposé aucun patch ('patch' est vide).")
            logs.append("Arrêt de l'auto-debug.")
            return logs, ia_history

        # On enregistre ce que l'IA a compris / proposé
        ia_history.append(
            {
                "iteration": iteration,
                "stderr": stderr,
                "error_short": data.get("error", "(erreur non précisée)"),
                "explanations": data.get("explanations", ""),
                "patch": patch,
            }
        )

        logs.append("\n✅ Patch proposé par l'IA :")
        logs.append(str(patch))

        # Application des patchs
        try:
            apply_patches(script_path, patch)
            logs.append("\n✅ Patch appliqué avec succès. Nouvelle exécution à la prochaine itération.")
        except Exception as e:
            logs.append(f"[ERREUR] Impossible d'appliquer le patch : {e}")
            return logs, ia_history

    logs.append("\n⛔ Nombre maximal d'itérations atteint sans exécution correcte du script.")
    return logs, ia_history


if __name__ == "__main__":
    """
    Usage en ligne de commande :

    python auto_debug.py chemin_vers_python chemin_vers_script.py

    Exemple :
    python auto_debug.py venv\\Scripts\\python.exe test_bug_complexe.py
    """
    if len(sys.argv) != 3:
        print("Usage : python auto_debug.py <chemin_python> <chemin_script>")
        print("Exemple : python auto_debug.py venv\\Scripts\\python.exe test_bug_complexe.py")
        sys.exit(1)

    python_path_arg = sys.argv[1]
    script_path_arg = sys.argv[2]

    logs_cli, ia_history_cli = auto_debug(python_path_arg, script_path_arg, max_iterations=30)

    # Affichage des logs en mode console
    print("\n".join(logs_cli))

    if ia_history_cli:
        print("\n===== RÉCAPITULATIF DES CORRECTIONS IA =====")
        for h in ia_history_cli:
            print(f"\n--- ITÉRATION {h['iteration']} - {h['error_short']} ---")
            print("Traceback :")
            print(h["stderr"])
            print("Explications IA :")
            print(h["explanations"])
            print("Patch :")
            print(h["patch"])
