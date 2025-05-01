#!/usr/bin/env python3
import os
import sys
import threading
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

# Ajuste de path para importar desde la raíz del proyecto
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(THIS_DIR, os.pardir, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from clients.common.ia_client import consultar_chatbot

class ChatUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Asistente IA – Chat")
        self.root.geometry("500x400")

        # Historial de chat (solo lectura)
        self.history = ScrolledText(self.root, state='disabled', wrap='word')
        self.history.pack(fill='both', expand=True, padx=5, pady=5)

        # Frame inferior con entrada y botón
        bottom = tk.Frame(self.root)
        bottom.pack(fill='x', padx=5, pady=5)

        self.entry = tk.Entry(bottom)
        self.entry.pack(side='left', fill='x', expand=True, padx=(0,5))
        # Aseguramos que reciba el foco
        self.entry.focus_set()
        # En algunos sistemas puede ayudar forzar el foco tras arrancar
        self.root.after(100, lambda: self.entry.focus_force())

        self.entry.bind("<Return>", self.on_send)

        send_btn = tk.Button(bottom, text="Enviar", command=self.on_send)
        send_btn.pack(side='right')

    def on_send(self, event=None):
        user_msg = self.entry.get().strip()
        if not user_msg:
            return
        self._append(f"Tú: {user_msg}\n")
        self.entry.delete(0, tk.END)
        threading.Thread(target=self._fetch_response, args=(user_msg,), daemon=True).start()

    def _fetch_response(self, prompt):
        self._append("\nIA: …\n")
        try:
            resp = consultar_chatbot(prompt)
        except Exception as e:
            resp = f"Error IA: {e}"
        # Reemplazamos la línea provisional
        self._replace_last_line(f"IA: {resp}\n")

    def _append(self, text):
        self.history.configure(state='normal')
        self.history.insert(tk.END, text)
        self.history.configure(state='disabled')
        self.history.yview(tk.END)

    def _replace_last_line(self, text):
        self.history.configure(state='normal')
        # Borra la última línea (la provisional)
        last_index = self.history.index('end-2l linestart')
        self.history.delete(last_index, tk.END)
        self.history.insert(tk.END, text)
        self.history.configure(state='disabled')
        self.history.yview(tk.END)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    ChatUI().run()
