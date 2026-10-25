"""
Una aplicación de escritorio ligera y autónoma diseñada para organizar automáticamente la carpeta de descargas del usuario de forma ordenada y eficiente.
"""

import asyncio
import os
import shutil
import sqlite3
import sys
from datetime import datetime
from importlib.metadata import version as _version
from pathlib import Path

import toga
from toga.platform import current_platform
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

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

# Plataforma
ES_ANDROID = current_platform == "android"
ES_IOS = current_platform == "iOS"
ES_MOVIL = ES_ANDROID or ES_IOS

# Toga 0.5 renombró "padding" a "margin" en Pack. Se detecta la versión
# para que el mismo código funcione en ambas.
try:
    _TOGA_VER = tuple(int(x) for x in _version("toga-core").split(".")[:2])
except Exception:
    _TOGA_VER = (0, 5)
ESPACIO = "margin" if _TOGA_VER >= (0, 5) else "padding"


def esp(*valores):
    """Devuelve el espaciado con el nombre de propiedad correcto según la versión."""
    return {ESPACIO: valores[0] if len(valores) == 1 else tuple(valores)}


# ======================================================================
# BASE DE DATOS (SQLite)
# ======================================================================
if getattr(sys, "frozen", False):
    base_path = os.path.dirname(sys.executable)  # Ejecutable compilado (.exe)
else:
    base_path = os.path.dirname(os.path.abspath(__file__))  # Script normal

db_path = os.path.join(base_path, "cronosdown_registro.db")


def configurar_ruta_db(carpeta_datos):
    """En móvil la carpeta de la app es de solo lectura, así que la base de
    datos se guarda en la carpeta de datos privada que asigna el sistema."""
    global db_path
    carpeta = Path(carpeta_datos)
    carpeta.mkdir(parents=True, exist_ok=True)
    db_path = str(carpeta / "cronosdown_registro.db")


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
# INTERFAZ (Toga)
# ==================================================================
class CronosDownMobile(toga.App):
    def startup(self):
        """Construye y muestra la ventana principal."""
        # Base de datos: en móvil va en la carpeta de datos privada de la app
        if ES_MOVIL:
            configurar_ruta_db(self.paths.data)
        inicializar_base_datos()

        self.main_window = toga.MainWindow(
            title="Ordenador de Archivos", size=(620, 580)
        )
        self.vista_principal = self._interfaz()
        self.vista_historial = self._interfaz_historial()
        self.main_window.content = self.vista_principal
        self.main_window.show()

    # ---------- Carpeta por defecto según la plataforma ----------
    def _carpeta_por_defecto(self):
        if ES_ANDROID:
            return Path("/storage/emulated/0/Download")
        if ES_IOS:
            # iOS solo permite trabajar dentro de la carpeta de la propia app
            carpeta = Path(self.paths.data) / "Descargas"
            carpeta.mkdir(parents=True, exist_ok=True)
            return carpeta
        return Path.home() / "Downloads"

    # ---------- Utilidades de diálogos (compatibles con Toga 0.4 y 0.5) ----------
    async def _info(self, titulo, mensaje):
        if hasattr(toga, "InfoDialog"):
            await self.main_window.dialog(toga.InfoDialog(titulo, mensaje))
        else:
            await self.main_window.info_dialog(titulo, mensaje)

    async def _error(self, titulo, mensaje):
        if hasattr(toga, "ErrorDialog"):
            await self.main_window.dialog(toga.ErrorDialog(titulo, mensaje))
        else:
            await self.main_window.error_dialog(titulo, mensaje)

    async def _elegir_carpeta(self, inicial):
        if hasattr(toga, "SelectFolderDialog"):
            return await self.main_window.dialog(
                toga.SelectFolderDialog(
                    title="Elige una carpeta", initial_directory=inicial
                )
            )
        return await self.main_window.select_folder_dialog(
            "Elige una carpeta", initial_directory=inicial
        )

    # ---------- Vista principal ----------
    def _interfaz(self):
        main = toga.Box(
            style=Pack(direction=COLUMN, flex=1, background_color=BG, **esp(24))
        )

        main.add(
            toga.Label(
                "Ordenador de Archivos",
                style=Pack(
                    color=TEXT, background_color=BG, font_size=20, font_weight="bold"
                ),
            )
        )
        main.add(
            toga.Label(
                "Elige una carpeta y organiza tus archivos por tipo.",
                style=Pack(
                    color=MUTED, background_color=BG, font_size=10, **esp(2, 0, 18, 0)
                ),
            )
        )

        # Selección de carpeta
        card = toga.Box(
            style=Pack(direction=COLUMN, background_color=CARD, **esp(14))
        )
        card.add(
            toga.Label(
                "CARPETA A ORDENAR",
                style=Pack(
                    color=MUTED, background_color=CARD, font_size=9, **esp(0, 0, 6, 0)
                ),
            )
        )
        fila = toga.Box(style=Pack(direction=ROW, background_color=CARD))
        self.ruta_input = toga.TextInput(
            value=str(self._carpeta_por_defecto()),
            style=Pack(flex=1, color=TEXT, background_color=BG),
        )
        fila.add(self.ruta_input)
        # En móvil no existe el selector de carpetas: la ruta se escribe a mano
        if not ES_MOVIL:
            fila.add(
                toga.Button(
                    "Examinar",
                    on_press=self.examinar,
                    style=Pack(color=TEXT, background_color=BG, **esp(0, 0, 0, 8)),
                )
            )
        card.add(fila)
        main.add(card)

        # Botones principales
        main.add(
            toga.Button(
                "Ordenar",
                on_press=self.ordenar,
                style=Pack(
                    color="white",
                    background_color=ACCENT,
                    font_size=12,
                    font_weight="bold",
                    **esp(18, 0, 8, 0),
                ),
            )
        )
        main.add(
            toga.Button(
                "Ver historial de cambios",
                on_press=self.abrir_historial,
                style=Pack(color=TEXT, background_color=CARD, **esp(0, 0, 14, 0)),
            )
        )

        # Registro
        main.add(
            toga.Label(
                "REGISTRO",
                style=Pack(
                    color=MUTED, background_color=BG, font_size=10, **esp(0, 0, 4, 0)
                ),
            )
        )
        self.log = toga.MultilineTextInput(
            readonly=True,
            style=Pack(
                flex=1,
                color=TEXT,
                background_color=CARD,
                font_family="monospace",
                font_size=9,
            ),
        )
        main.add(self.log)

        # Resumen
        self.resumen = toga.Label(
            "",
            style=Pack(
                color=OK, background_color=BG, font_size=10, font_weight="bold",
                **esp(12, 0, 0, 0),
            ),
        )
        main.add(self.resumen)

        # Fila inferior (Acerca de)
        fila_inferior = toga.Box(
            style=Pack(direction=ROW, background_color=BG, **esp(8, 0, 0, 0))
        )
        fila_inferior.add(toga.Box(style=Pack(flex=1, background_color=BG)))
        fila_inferior.add(
            toga.Button(
                "Acerca de",
                on_press=self.mostrar_acerca_de,
                style=Pack(color=MUTED, background_color=BG, font_size=8),
            )
        )
        main.add(fila_inferior)

        return main

    # ---------- Vista de historial ----------
    # Se muestra dentro de la misma ventana (en móvil no hay ventanas múltiples)
    def _interfaz_historial(self):
        cont = toga.Box(
            style=Pack(direction=COLUMN, flex=1, background_color=BG, **esp(20))
        )
        cont.add(
            toga.Label(
                "Historial de movimientos",
                style=Pack(
                    color=TEXT, background_color=BG, font_size=20, font_weight="bold"
                ),
            )
        )
        cont.add(
            toga.Label(
                "Archivos ordenados anteriormente.",
                style=Pack(
                    color=MUTED, background_color=BG, font_size=10, **esp(2, 0, 12, 0)
                ),
            )
        )

        self.tabla = toga.Table(
            headings=["Fecha", "Hora", "Archivo", "Carpeta destino"],
            data=[],
            style=Pack(flex=1, color=TEXT, background_color=CARD),
        )
        cont.add(self.tabla)

        botones = toga.Box(
            style=Pack(direction=ROW, background_color=BG, **esp(12, 0, 0, 0))
        )
        botones.add(
            toga.Button(
                "Volver",
                on_press=self.volver,
                style=Pack(color=TEXT, background_color=CARD),
            )
        )
        botones.add(toga.Box(style=Pack(flex=1, background_color=BG)))
        botones.add(
            toga.Button(
                "Actualizar",
                on_press=self.cargar_historial,
                style=Pack(color=TEXT, background_color=CARD),
            )
        )
        cont.add(botones)
        return cont

    async def cargar_historial(self, widget=None):
        try:
            self.tabla.data = [tuple(f) for f in leer_historial()]
        except Exception as e:
            await self._error("Error", f"No se pudo leer el historial:\n{e}")

    async def abrir_historial(self, widget):
        self.main_window.content = self.vista_historial
        await self.cargar_historial()

    def volver(self, widget):
        self.main_window.content = self.vista_principal

    # ---------- Lógica ----------
    async def examinar(self, widget):
        try:
            carpeta = await self._elegir_carpeta(self.ruta_input.value)
        except Exception:
            carpeta = None
        if carpeta:
            self.ruta_input.value = str(carpeta)

    def escribir(self, texto):
        self.log.value = (self.log.value or "") + texto + "\n"
        try:
            self.log.scroll_to_bottom()
        except Exception:
            pass

    async def ordenar(self, widget):
        base = Path(self.ruta_input.value)
        if not base.is_dir():
            mensaje = "La carpeta seleccionada no existe."
            if ES_ANDROID:
                mensaje += (
                    "\n\nEn Android, si la carpeta existe, revisa que la app "
                    "tenga permiso de acceso a todos los archivos."
                )
            await self._error("Error", mensaje)
            return

        self.log.value = ""
        self.resumen.text = ""

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
                    # Cede el control a la interfaz para que el registro se
                    # actualice en pantalla (equivale a update_idletasks)
                    await asyncio.sleep(0)
                    break

        total = sum(conteo.values())
        if total == 0 and omitidos == 0 and errores == 0:
            self.resumen.text = "No había archivos para ordenar."
            return

        detalle = ", ".join(f"{n}: {c}" for n, c in conteo.items())
        texto = f"Listo: {total} archivo(s) movido(s)"
        if detalle:
            texto += f" ({detalle})"
        if omitidos:
            texto += f". Omitidos: {omitidos}"
        if errores:
            texto += f". Errores: {errores}"
        self.resumen.text = texto

    async def mostrar_acerca_de(self, widget):
        await self._info(
            "Acerca de CronosDown",
            "CronosDown v3.1.0\n\n"
            "Desarrollado por: Yimer Pineda\n"
            "Todos los derechos reservados © 2026\n\n"
            "Herramienta inteligente de ordenamiento de archivos.",
        )


# ======================================================================
# INICIO
# ======================================================================
def main():
    return CronosDownMobile(
        formal_name="Ordenador de Archivos", app_id="com.yimerpineda.cronosdown"
    )


if __name__ == "__main__":
    main().main_loop()