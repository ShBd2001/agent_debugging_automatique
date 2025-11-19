
## 3️⃣ `patcher.py` — Appliquer les corrections sur le fichier

# patcher.py
from pathlib import Path
from typing import List, Dict, Any
import shutil


def apply_patches(file_path: str, patch_instructions: List[Dict[str, Any]]) -> None:
    """
    Applique les patchs sur file_path.
    Crée une sauvegarde file_path.bak avant modification.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Fichier source introuvable : {path}")

    # Sauvegarde
    backup_path = path.with_suffix(path.suffix + ".bak")
    shutil.copy2(path, backup_path)

    # Lecture
    with path.open("r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    # On applique les patchs dans l'ordre des lignes croissantes
    # pour limiter les décalages
    sorted_patches = sorted(patch_instructions, key=lambda x: x["line"])

    for instr in sorted_patches:
        action = instr["action"]
        line_number = instr["line"]  # 1-based
        content = instr.get("content", "")

        index = line_number - 1  # pour la liste 0-based

        if action == "delete_line":
            if 0 <= index < len(lines):
                del lines[index]

        elif action == "replace_line":
            if 0 <= index < len(lines):
                lines[index] = content

        elif action == "insert_before":
            if 0 <= index <= len(lines):
                lines.insert(index, content)

        else:
            # déjà filtré normalement
            continue

    # Réécriture du fichier
    with path.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))
