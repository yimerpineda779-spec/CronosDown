import shutil
import tkinter as tk
import os
import sys
import sqlite3
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

FOLDERS = {
    "Images": ["jpg", "jpeg", "png", "gif", "bmp", "tiff", "ico", "avif", "jfif"],
    "Videos": ["mp4", "mov", "avi", "mkv", "flv", "wmv", "webm"],
    "Audio": ["mp3", "wav", "flac", "aac", "ogg", "m4a"],
    "Documentos": ["txt", "pdf", "doc", "docx", "odt", "rtf", "tex", "wpd", "md", "markdown"],
    "Cálculos": ["xls", "xlsx", "ods", "csv"],
    "Presentaciones": ["ppt", "pptx", "odp", "pptm"],
    "Comprimidos": ["zip", "rar", "7z", "tar", "gz"],
    "Código": ["py", "js", "html", "css", "java", "c", "cpp", "cs", "php", "rb", "go", "rs", "ts"],
    "Ejecutables": ["exe", "msi", "bat", "sh", "appimage", "apk", "deb", "rpm"],
}
#----------- base de datos en SQLite----------------------------------
# Obtiene la ruta donde está corriendo el ejecutable o el script
if getattr(sys, 'frozen', False):
    # Si es un ejecutable compilado
    base_path = os.path.dirname(sys.executable)
else:
    # Si estás corriendo el script normal en desarrollo
    base_path = os.path.dirname(os.path.abspath(__file__))

# Ruta completa para la base de datos al lado de tu .exe
db_path = os.path.join(base_path, "cronosdown_registro.db")

# Conectarte (esto creará el archivo automáticamente si no existe)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
#---------------------------------------------------------------------
# Colores
BG = "#1e1e2e"
CARD = "#2a2a3d"
TEXT = "#e6e6f0"
MUTED = "#9a9ab0"
ACCENT = "#7c5cff"
ACCENT_HOVER = "#957bff"
OK = "#5ee3a1"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ordenador de Archivos")
        self.geometry("620x540")
        self.minsize(560, 480)
        self.configure(bg=BG)

        self.ruta = tk.StringVar(value=str(Path.home() / "Downloads"))
        self._estilos()
        self._interfaz()

    # ---------- Estilos ----------
    def _estilos(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("TFrame", background=BG)
        s.configure("Card.TFrame", background=CARD)
        s.configure("Titulo.TLabel", background=BG, foreground=TEXT, font=("Segoe UI", 20, "bold"))
        s.configure("Sub.TLabel", background=BG, foreground=MUTED, font=("Segoe UI", 10))
        s.configure("Card.TLabel", background=CARD, foreground=MUTED, font=("Segoe UI", 9))
        s.configure("Resumen.TLabel", background=BG, foreground=OK, font=("Segoe UI", 10, "bold"))
        s.configure(
            "TEntry", fieldbackground=BG, foreground=TEXT, bordercolor=CARD,
            lightcolor=CARD, darkcolor=CARD, padding=6,
        )
        s.configure(
            "Sec.TButton", background=CARD, foreground=TEXT, borderwidth=0,
            padding=(14, 7), font=("Segoe UI", 10),
        )
        s.map("Sec.TButton", background=[("active", "#3a3a52")])
        s.configure(
            "Main.TButton", background=ACCENT, foreground="white", borderwidth=0,
            padding=(20, 11), font=("Segoe UI", 12, "bold"),
        )
        s.map("Main.TButton", background=[("active", ACCENT_HOVER)])

    # ---------- Interfaz ----------
    def _interfaz(self):
        main = ttk.Frame(self, padding=24)
        main.pack(fill="both", expand=True)

        ttk.Label(main, text="Ordenador de Archivos", style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(
            main, text="Elige una carpeta y organiza tus archivos por tipo.",
            style="Sub.TLabel",
        ).pack(anchor="w", pady=(2, 18))

        # Tarjeta de selección de carpeta
        card = ttk.Frame(main, style="Card.TFrame", padding=14)
        card.pack(fill="x")
        ttk.Label(card, text="CARPETA A ORDENAR", style="Card.TLabel").pack(anchor="w", pady=(0, 6))
        fila = ttk.Frame(card, style="Card.TFrame")
        fila.pack(fill="x")
        ttk.Entry(fila, textvariable=self.ruta).pack(side="left", fill="x", expand=True)
        ttk.Button(fila, text="Examinar", style="Sec.TButton", command=self.examinar).pack(
            side="left", padx=(8, 0)
        )

        # Botón principal
        ttk.Button(main, text="Ordenar", style="Main.TButton", command=self.ordenar).pack(
            fill="x", pady=18
        )

        # Registro
        ttk.Label(main, text="REGISTRO", style="Sub.TLabel").pack(anchor="w", pady=(0, 4))
        caja = ttk.Frame(main, style="Card.TFrame", padding=2)
        caja.pack(fill="both", expand=True)
        self.log = tk.Text(
            caja, bg=CARD, fg=TEXT, relief="flat", font=("Consolas", 9),
            padx=10, pady=8, state="disabled", wrap="none",
        )
        scroll = ttk.Scrollbar(caja, command=self.log.yview)
        self.log.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.log.pack(side="left", fill="both", expand=True)

        # Resumen
        self.resumen = ttk.Label(main, text="", style="Resumen.TLabel")
        self.resumen.pack(anchor="w", pady=(12, 0))

    # ---------- Lógica ----------
    def examinar(self):
        carpeta = filedialog.askdirectory(initialdir=self.ruta.get(), title="Elige una carpeta")
        if carpeta:
            self.ruta.set(carpeta)

    def escribir(self, texto):
        self.log.configure(state="normal")
        self.log.insert("end", texto + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")
        self.update_idletasks()

    def ordenar(self):
        base = Path(self.ruta.get())
        if not base.is_dir():
            messagebox.showerror("Error", "La carpeta seleccionada no existe.")
            return

        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")
        self.resumen.configure(text="")

        conteo = {}
        omitidos = 0
        errores = 0

        for archivo in list(base.iterdir()):
            if not archivo.is_file():
                continue
            ext = archivo.suffix[1:].lower()
            for nombre, exts in FOLDERS.items():
                if ext in exts:
                    destino_dir = base / nombre
                    destino = destino_dir / archivo.name
                    if destino.exists():
                        omitidos += 1
                        self.escribir(f"Omitido (ya existe): {archivo.name}")
                    else:
                        try:
                            destino_dir.mkdir(exist_ok=True)
                            shutil.move(str(archivo), str(destino))
                            conteo[nombre] = conteo.get(nombre, 0) + 1
                            self.escribir(f"{archivo.name}  ->  {nombre}")
                        except Exception as e:
                            errores += 1
                            self.escribir(f"Error con {archivo.name}: {e}")
                    break

        total = sum(conteo.values())
        if total == 0 and omitidos == 0 and errores == 0:
            self.resumen.configure(text="No había archivos para ordenar.")
            return

        detalle = ", ".join(f"{n}: {c}" for n, c in conteo.items())
        texto = f"Listo: {total} archivo(s) movido(s)"
        if detalle:
            texto += f" ({detalle})"
        if omitidos:
            texto += f". Omitidos: {omitidos}"
        if errores:
            texto += f". Errores: {errores}"
        self.resumen.configure(text=texto, wraplength=560, justify="left")


if __name__ == "__main__":
    App().mainloop()