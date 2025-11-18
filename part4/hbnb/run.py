#!/usr/bin/python3
"""Entry point for running the HBnB API"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    print("--- [PERSISTANCE MÉMOIRE ACTIVÉE] Rechargement automatique désactivé ---")
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
