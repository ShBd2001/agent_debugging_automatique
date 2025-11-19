# ui.py
import traceback
import streamlit as st

from config import load_config, save_config
from auto_debug import auto_debug  # on importe la fonction d'auto-debug


def main():
    st.set_page_config(page_title="Agent de Debugging Automatique", layout="wide")
    st.title("🤖 Agent de debugging automatique (AUTO)")

    config = load_config()

    # ================== BARRE LATERALE ==================
    st.sidebar.header("Configuration")
    python_path = st.sidebar.text_input(
        "Chemin de l'interpréteur Python (venv)",
        value=config.get("python_path", "venv\\Scripts\\python.exe"),
    )
    script_path = st.sidebar.text_input(
        "Chemin du script à analyser",
        value=config.get("last_script", ""),
        help="Ex : test_bug.py, test_bug_moyen.py, test_bug_complexe.py",
    )

    max_iter = st.sidebar.number_input(
        "Nombre maximal d'itérations d'auto-debug",
        min_value=1,
        max_value=50,
        value=10,
        step=1,
    )

    if st.sidebar.button("💾 Sauvegarder la config"):
        config["python_path"] = python_path
        config["last_script"] = script_path
        save_config(config)
        st.sidebar.success("Configuration sauvegardée ✅")

    # ================== CONTENU PRINCIPAL ==================
    st.markdown(
        """
        Cette application va :

        1. exécuter le script Python sélectionné,
        2. récupérer l'erreur d'exécution,
        3. envoyer le code + l'erreur à une IA (Groq),
        4. appliquer automatiquement les corrections proposées,
        5. recommencer jusqu'à ce que le script s'exécute sans erreur
           ou que le nombre maximal d'itérations soit atteint.
        """
    )

    if st.button("🤖 Lancer l'AUTO-DEBUG complet"):
        if not script_path:
            st.error("Veuillez renseigner un chemin de script dans la barre latérale.")
        else:
            with st.spinner("Auto-debug en cours..."):
                try:
                    logs, ia_history = auto_debug(
                        python_path=python_path,
                        script_path=script_path,
                        max_iterations=int(max_iter),
                    )
                except Exception as e:
                    st.error(f"Erreur lors de l'exécution de l'auto-debug : {e}")
                    st.code(traceback.format_exc(), language="text")
                else:
                    st.success("Auto-debug terminé ✅")

                    # Affichage des logs bruts (stdout, stderr, infos)
                    st.subheader("📜 Logs d'exécution")
                    if logs:
                        st.code("\n".join(logs), language="text")
                    else:
                        st.write("Aucun log disponible.")

                    # Affichage des explications IA par itération
                    if ia_history:
                        st.subheader("🧠 Historique des corrections IA")
                        for h in ia_history:
                            with st.expander(f"ITÉRATION {h['iteration']} - {h['error_short']}"):
                                st.markdown("**Erreur détectée (traceback original) :**")
                                st.code(h["stderr"], language="text")

                                st.markdown("**Explications de l'IA :**")
                                st.write(h["explanations"])

                                st.markdown("**Patch proposé :**")
                                st.json(h["patch"])
                    else:
                        st.info("Aucune correction IA enregistrée (pas d'erreur ou pas de patch).")


if __name__ == "__main__":
    main()
