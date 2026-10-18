from pathlib import Path
import shutil

documents_path = Path.home() / "Downloads"
folders = {
    "Images": ["jpg", "jpeg", "png", "gif", "bmp", "tiff", "ico", "avif" , "jfif"],
    "Videos": ["mp4", "mov", "avi", "mkv", "flv", "wmv" , "webm"],
    "Audio": ["mp3", "wav", "flac", "aac", "ogg" , "m4a"],
    "Documentos": ["txt", "pdf", "doc", "docx", "odt" , "rtf", "tex", "wpd", "md", "markdown"],
    "Cálculos": ["xls", "xlsx", "ods", "csv"],
    "Presentaciones": ["ppt", "pptx", "odp", "pptm"],
    "Comprimidos": ["zip", "rar", "7z", "tar", "gz"],
    "Código": ["py", "js", "html", "css", "java", "c", "cpp", "cs", "php", "rb", "go", "rs", "ts"],
    "Ejecutables": ["exe", "msi", "bat", "sh", "appimage", "apk", "deb", "rpm"],
}

for name in folders:
    (documents_path / name).mkdir(exist_ok=True)
    
for file in list(documents_path.iterdir()):
    ext = file.suffix[1:].lower()
    for name, exts in folders.items():
       if file.is_file() and ext in exts:
            target = documents_path / name / file.name
            if not target.exists():
                shutil.move(file,target)