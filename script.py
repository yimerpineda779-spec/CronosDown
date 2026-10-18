import os
import shutil
import sqlite3
import sys
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

# ======================================================================
# CONFIGURACIÓN
# ======================================================================
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

# Colores
BG = "#1e1e2e"
CARD = "#2a2a3d"
TEXT = "#e6e6f0"
MUTED = "#9a9ab0"
ACCENT = "#7c5cff"
ACCENT_HOVER = "#957bff"
OK = "#5ee3a1"

# ======================================================================
# BASE DE DATOS (SQLite)
# ======================================================================
if getattr(sys, "frozen", False):
    base_path = os.path.dirname(sys.executable)  # Ejecutable compilado (.exe)
else:
    base_path = os.path.dirname(os.path.abspath(__file__))  # Script normal

db_path = os.path.join(base_path, "cronosdown_registro.db")


def inicializar_base_datos():
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS historial (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            hora TEXT,
            archivo TEXT,
            carpeta TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def registrar_movimiento(nombre_archivo, carpeta_destino):
    ahora = datetime.now()
    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT INTO historial (fecha, hora, archivo, carpeta) VALUES (?, ?, ?, ?)",
        (ahora.strftime("%Y-%m-%d"), ahora.strftime("%H:%M:%S"), nombre_archivo, carpeta_destino),
    )
    conn.commit()
    conn.close()


def leer_historial():
    conn = sqlite3.connect(db_path)
    filas = conn.execute(
        "SELECT fecha, hora, archivo, carpeta FROM historial ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return filas


# ==================================================================
# INTERFAZ
# ==================================================================
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ordenador de Archivos")
        self.geometry("620x580")
        self.minsize(560, 520)
        self.configure(bg=BG)
        try:    #icono de la ventana
            root.iconbitmap("icono.ico") 
        except Exception as e:
            print("No se pudo cargar el ícono en la ventana:", e)

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
        # Tabla del historial
        s.configure(
            "Treeview", background=CARD, fieldbackground=CARD, foreground=TEXT,
            borderwidth=0, rowheight=26, font=("Segoe UI", 9),
        )
        s.configure(
            "Treeview.Heading", background=BG, foreground=MUTED,
            font=("Segoe UI", 9, "bold"), borderwidth=0, padding=6,
        )
        s.map("Treeview", background=[("selected", ACCENT)])

    # ---------- Interfaz principal ----------
    def _interfaz(self):
        main = ttk.Frame(self, padding=24)
        main.pack(fill="both", expand=True)

        ttk.Label(main, text="Ordenador de Archivos", style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(
            main, text="Elige una carpeta y organiza tus archivos por tipo.",
            style="Sub.TLabel",
        ).pack(anchor="w", pady=(2, 18))

        # Selección de carpeta
        card = ttk.Frame(main, style="Card.TFrame", padding=14)
        card.pack(fill="x")
        ttk.Label(card, text="CARPETA A ORDENAR", style="Card.TLabel").pack(anchor="w", pady=(0, 6))
        fila = ttk.Frame(card, style="Card.TFrame")
        fila.pack(fill="x")
        ttk.Entry(fila, textvariable=self.ruta).pack(side="left", fill="x", expand=True)
        ttk.Button(fila, text="Examinar", style="Sec.TButton", command=self.examinar).pack(
            side="left", padx=(8, 0)
        )

        # Botones principales
        ttk.Button(main, text="Ordenar", style="Main.TButton", command=self.ordenar).pack(
            fill="x", pady=(18, 8)
        )
        ttk.Button(
            main, text="Ver historial de cambios", style="Sec.TButton",
            command=self.abrir_historial,
        ).pack(fill="x", pady=(0, 14))

        # Registro
        ttk.Label(main, text="REGISTRO", style="Sub.TLabel").pack(anchor="w", pady=(0, 4))
        caja = ttk.Frame(main, style="Card.TFrame", padding=2)
        caja.pack(fill="both", expand=True)
        self.log = tk.Text(
            caja, bg=CARD, fg=TEXT, relief="flat", font=("Consolas", 9),
            padx=10, pady=8, state="disabled", wrap="none",
        )
        scroll_y = ttk.Scrollbar(caja, orient="vertical", command=self.log.yview)
        scroll_x = ttk.Scrollbar(caja, orient="horizontal", command=self.log.xview)
        self.log.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")
        self.log.pack(side="left", fill="both", expand=True)

        # Resumen
        self.resumen = ttk.Label(main, text="", style="Resumen.TLabel")
        self.resumen.pack(anchor="w", pady=(12, 0))

    # ---------- Ventana de historial ----------
    def abrir_historial(self):
        win = tk.Toplevel(self)
        win.title("Historial de movimientos")
        win.geometry("680x420")
        win.configure(bg=BG)

        cont = ttk.Frame(win, padding=20)
        cont.pack(fill="both", expand=True)

        ttk.Label(cont, text="Historial de movimientos", style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(cont, text="Archivos ordenados anteriormente.", style="Sub.TLabel").pack(
            anchor="w", pady=(2, 12)
        )

        columnas = ("Fecha", "Hora", "Archivo", "Carpeta destino")
        marco = ttk.Frame(cont, style="Card.TFrame", padding=2)
        marco.pack(fill="both", expand=True)
        tree = ttk.Treeview(marco, columns=columnas, show="headings")
        anchos = {"Fecha": 90, "Hora": 80, "Archivo": 300, "Carpeta destino": 130}
        for col in columnas:
            tree.heading(col, text=col)
            tree.column(col, width=anchos[col], anchor="w")
        sb = ttk.Scrollbar(marco, command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)

        def cargar():
            tree.delete(*tree.get_children())
            try:
                for fila in leer_historial():
                    tree.insert("", "end", values=fila)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo leer el historial:\n{e}", parent=win)

        ttk.Button(cont, text="Actualizar", style="Sec.TButton", command=cargar).pack(
            anchor="e", pady=(12, 0)
        )
        cargar()

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
                            registrar_movimiento(archivo.name, nombre)
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


# ======================================================================
# INICIO
# ======================================================================
if __name__ == "__main__":
    inicializar_base_datos()
    App().mainloop()