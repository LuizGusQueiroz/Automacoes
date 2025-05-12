import os
import re
import shutil
from PyPDF2 import PdfReader
import tkinter as tk
from tkinter import scrolledtext, messagebox

CNPJ_PATTERN = r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}'
CNPJ_IGNORADO = "16.707.848/0001-95"

def limpar_cnpj(cnpj):
    return re.sub(r'\D', '', cnpj)

class CNPJOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Organizador de PDFs por CNPJ")
        self.root.geometry("900x600")
        self.create_widgets()

    def create_widgets(self):
        frame = tk.Frame(self.root)
        frame.pack(pady=10)

        tk.Button(frame, text="Organizar PDFs", command=self.organize_pdfs).pack(side=tk.LEFT, padx=5)

        self.text_area = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, width=100, height=30,
            font=("Courier New", 10)
        )
        self.text_area.pack(padx=15, pady=10, fill=tk.BOTH, expand=True)

    def organize_pdfs(self):
        self.text_area.delete(1.0, tk.END)

        origem = os.path.join("CONDOMINIAIS", "NOTA FISCAL")
        destino_base = os.path.join("arquivos_organizados", "nfs_organizados")

        if not os.path.exists(origem):
            messagebox.showerror("Erro", f"Pasta não encontrada: {origem}")
            return

        os.makedirs(destino_base, exist_ok=True)

        files = [f for f in os.listdir(origem) if f.lower().endswith('.pdf')]
        if not files:
            self.text_area.insert(tk.END, "Nenhum arquivo PDF encontrado.\n")
            return

        for file_name in files:
            full_path = os.path.join(origem, file_name)
            try:
                with open(full_path, 'rb') as f:
                    reader = PdfReader(f)
                    text = ""
                    for page in reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text

                    cnpjs = re.findall(CNPJ_PATTERN, text)
                    cnpjs = [c for c in cnpjs if c != CNPJ_IGNORADO]

                    self.text_area.insert(tk.END, f"\nArquivo: {file_name}\n")

                    if cnpjs:
                        cnpj_limpo = limpar_cnpj(cnpjs[0])
                        destino_final = os.path.join(destino_base, cnpj_limpo)
                        os.makedirs(destino_final, exist_ok=True)
                        shutil.move(full_path, os.path.join(destino_final, file_name))
                        self.text_area.insert(tk.END, f"  Movido para: {destino_final}\n")
                    else:
                        destino_final = os.path.join(destino_base, "nfs sem cnpj")
                        os.makedirs(destino_final, exist_ok=True)
                        shutil.move(full_path, os.path.join(destino_final, file_name))
                        self.text_area.insert(tk.END, f"  Nenhum CNPJ válido encontrado. Movido para: {destino_final}\n")

            except Exception as e:
                self.text_area.insert(tk.END, f"  Erro ao processar {file_name}: {e}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = CNPJOrganizerApp(root)
    root.mainloop()