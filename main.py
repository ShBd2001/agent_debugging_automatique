# main.py
from pathlib import Path

from executor import run_script
from ai_client import AIDebuggerClient
from patcher import apply_patches


def main():
    python_path = r"venv\Scripts\python.exe"
    script_path = input("Chemin du script à analyser : ").strip()

    code = Path(script_path).read_text(encoding="utf-8")
    rc, stdout, stderr = run_script(python_path, script_path)

    print("=== STDERR ===")
    print(stderr)

    client = AIDebuggerClient()
    data = client.get_correction(code, stderr)

    print("\n=== ERREUR DÉTECTÉE ===")
    print(data["error"])
    print("\n=== EXPLICATIONS ===")
    print(data["explanations"])
    print("\n=== PATCH ===")
    print(data["patch"])

    confirm = input("\nAppliquer les patchs ? (o/n) : ").lower()
    if confirm == "o":
        apply_patches(script_path, data["patch"])
        print("Patch appliqué ✅")


if __name__ == "__main__":
    main()
