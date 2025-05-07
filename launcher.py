#!/usr/bin/env python3
import sys
import subprocess
import sqlite3

def launch_game(module, arg=None):
    cmd = [sys.executable, "-m", module]
    if arg:
        cmd.append(str(arg))
    subprocess.Popen(cmd)


def view_results():
    db_path = "server/resultados.db"
    try:
        conn = sqlite3.connect(db_path)
    except sqlite3.Error as e:
        print(f"⚠️ No se pudo abrir la BD: {e}")
        return
    cursor = conn.cursor()

    print("\n¿Qué resultados quieres ver?")
    print("1) N-Reinas")
    print("2) Knight’s Tour")
    print("3) Torres de Hanói")
    print("4) Todos")
    sel = input("Selecciona [1-4]: ").strip()

    if sel == "1":
        tables = ["reinas_results"]
    elif sel == "2":
        tables = ["caballo_results"]
    elif sel == "3":
        tables = ["hanoi_results"]
    elif sel == "4":
        tables = ["reinas_results", "caballo_results", "hanoi_results"]
    else:
        print("Opción no válida.")
        conn.close()
        return

    for t in tables:
        print(f"\n--- {t} ---")
        try:
            cursor.execute(f"SELECT * FROM {t}")
            cols = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
        except sqlite3.Error as e:
            print(f"⚠️ Error consultando {t}: {e}")
            continue

        print(" | ".join(cols))
        for row in rows:
            print(" | ".join(str(x) for x in row))

    conn.close()

def main():
    while True:
        print("\n=== Máquina Arcade Distribuida ===")
        print("1) N-Reinas")
        print("2) Knight’s Tour")
        print("3) Torres de Hanói")
        print("4) Ver resultados")
        print("5) Chat IA")
        print("6) Salir")
        choice = input("Selecciona [1-6]: ").strip()

        if choice == "1":
            n = input("  Introduce N (por defecto 8): ").strip() or "8"
            launch_game("clients.nreinas.ui", n)

        elif choice == "2":
            print("  - Selecciona la casilla inicial en la ventana")
            launch_game("clients.caballo.ui")

        elif choice == "3":
            d = input("  ¿Cuántos discos? (por defecto 3): ").strip() or "3"
            launch_game("clients.hanoi.ui", d)

        elif choice == "4":
            view_results()

        elif choice == "5":
            launch_game("clients.common.chat_ui")

        elif choice == "6":
            print("¡Hasta luego!")
            sys.exit(0)

        else:
            print("Opción no válida, elige 1-6.")

if __name__ == "__main__":
    main()
