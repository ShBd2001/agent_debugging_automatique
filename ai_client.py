# ai_client.py
import os
import json
from dataclasses import dataclass
from typing import Any, Dict, List

from dotenv import load_dotenv
from groq import Groq   # on utilise Groq

load_dotenv()


@dataclass
class PatchInstruction:
    action: str    # "replace_line" | "delete_line" | "insert_before"
    line: int
    content: str | None = None


class AIDebuggerClient:
    """
    Client pour envoyer le code + erreur à Groq
    et récupérer un JSON de corrections.
    """

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY manquante dans .env")

        self.client = Groq(api_key=api_key)
        # Modèle Groq (tu peux changer si besoin)
        self.model = "llama-3.3-70b-versatile"

    def build_messages(self, code: str, error: str) -> List[Dict[str, Any]]:
        system_prompt = (
            "Tu es un expert en debugging Python.\n"
            "Tu DOIS répondre STRICTEMENT en JSON valide, sans texte autour.\n\n"
            "Format attendu :\n\n"
            "{\n"
            '  \"error\": \"description courte de l\'erreur\",\n'
            '  \"explanations\": \"explication détaillée en français\",\n'
            '  \"patch\": [\n'
            "     {\n"
            '       \"action\": \"replace_line | delete_line | insert_before\",\n'
            "       \"line\": <numéro de ligne (int, 1-based)>,\n"
            '       \"content\": \"nouveau code de la ligne (ou chaine vide si delete_line)\"\n'
            "     }\n"
            "  ]\n"
            "}\n\n"
            "Règles :\n"
            "- Ne modifie que les lignes strictement nécessaires.\n"
            "- Si aucune modification n'est nécessaire, retourne un JSON avec \"patch\": [].\n"
            "- Ne rajoute pas de commentaires inutiles dans le code.\n"
        )

        user_prompt = (
            "Voici le code du script Python :\n\n"
            f"{code}\n\n"
            "=== FIN DU CODE ===\n\n"
            "Voici l'erreur d'exécution (stderr) :\n\n"
            f"{error}\n\n"
            "Propose un correctif en respectant STRICTEMENT le format JSON demandé.\n"
        )

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

    def get_correction(self, code: str, error: str) -> Dict[str, Any]:
        """
        Appelle le modèle Groq et retourne le JSON de correction.
        """
        messages = self.build_messages(code, error)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.1,
        )

        raw_content = response.choices[0].message.content

        try:
            data = json.loads(raw_content)
        except json.JSONDecodeError:
            cleaned = raw_content.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.strip("`")
                cleaned = cleaned.replace("json", "", 1).strip()
            data = json.loads(cleaned)

        self._validate_json(data)
        return data

    def _validate_json(self, data: Dict[str, Any]) -> None:
        """
        Validation simple du JSON de correction.
        On vérifie juste que la structure de base est là, sans bloquer
        sur les noms d'actions (les actions inconnues seront ignorées plus tard).
        """
        if "error" not in data or "explanations" not in data or "patch" not in data:
            raise ValueError("JSON incomplet : 'error', 'explanations' ou 'patch' manquant")

        if not isinstance(data["patch"], list):
            raise ValueError("'patch' doit être une liste")

        for instr in data["patch"]:
            if "action" not in instr or "line" not in instr:
                raise ValueError("Chaque patch doit contenir 'action' et 'line'")
            if not isinstance(instr["line"], int):
                raise ValueError("'line' doit être un entier")
            # On ne vérifie PAS ici la valeur exacte de 'action'
