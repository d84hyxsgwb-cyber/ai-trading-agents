#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
run.py
------
Piccolo "launcher" con menu testuale per gestire:

1) Analisi giornaliera (ensemble_manager)
2) Backtest avanzato (backtest)
3) Advisor IA (advisor_agent)

Da eseguire con:
    source env/bin/activate
    python3 run.py
"""

import subprocess
import sys
import os


def run_command(cmd: list[str]) -> int:
    """
    Esegue un comando di sistema e mostra l'output in tempo reale.
    Ritorna il codice di uscita.
    """
    print(f"\n>>> Eseguo: {' '.join(cmd)}\n")
    result = subprocess.run(cmd)
    print("\n>>> Comando terminato.\n")
    return result.returncode


def menu_loop():
    """
    Mostra il menu e gestisce la scelta dell'utente.
    """
    while True:
        print("=======================================")
        print("      AI TRADING AGENTS - MAIN MENU    ")
        print("=======================================")
        print("1) Analisi completa dei mercati (ensemble_manager)")
        print("2) Backtest avanzato (backtest)")
        print("3) Advisor IA (advisor_agent)")
        print("4) Esci")
        print("=======================================")

        choice = input("Seleziona un'opzione (1-4): ").strip()

        if choice == "1":
            # Analisi completa
            run_command([sys.executable, "ensemble_manager.py"])

        elif choice == "2":
            # Backtest
            run_command([sys.executable, "backtest.py"])

        elif choice == "3":
            # Advisor IA
            # Controlliamo che ci sia la OPENAI_API_KEY
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("\n[ERRORE] OPENAI_API_KEY non trovata. "
                      "Aggiungila al file .env nella root del progetto.\n")
            else:
                run_command([sys.executable, "advisor_agent.py"])

        elif choice == "4":
            print("\nEsco dal programma. Bye Master 👋\n")
            break
        else:
            print("\nScelta non valida. Inserisci un numero tra 1 e 4.\n")


if __name__ == "__main__":
    menu_loop()
