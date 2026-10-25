# Guía Definitiva: De CronosDown Escritorio a APK Android con BeeWare

Esta guía detalla el paso a paso completo, comandos y consideraciones técnicas utilizados para bifurcar el proyecto **CronosDown** a una versión móvil utilizando el framework **BeeWare** (Briefcase y Toga) y generar un archivo `.apk` funcional para Android.

---

## Fase 1: Control de Versiones y Creación de la Rama Móvil

Para mantener la versión de escritorio (`main`) intacta y segura, se trabaja sobre una rama dedicada al desarrollo móvil.

1. **Verificar el estado del repositorio local:**
   ```bash
   git status
   ```
2. **Crear y cambiar a una nueva rama específica para móviles:**
   ```bash
   git checkout -b mobile-beeware
   ```
   *(O alternativamente: `git switch -c mobile-beeware`)*
3. **Sincronizar y respaldar la nueva rama en GitHub:**
   ```bash
   git push -u origin mobile-beeware
   ```

---

## Fase 2: Configuración del Entorno BeeWare y Briefcase

BeeWare utiliza **Briefcase** para empaquetar aplicaciones de Python en ejecutables nativos móviles y de escritorio.

1. **Instalar Briefcase en el entorno de desarrollo:**
   ```bash
   pip install briefcase
   ```
2. **Inicializar la estructura de la aplicación multiplataforma:**
   ```bash
   briefcase new
   ```
3. **Configurar los parámetros del asistente interactivo:**
   * **App Name:** `CronosDownApp`
   * **Formal Name:** `CronosDown Mobile`
   * **Bundle Identifier:** `com.yimerpineda.cronosdown`
   * **Project Name:** `CronosDown`
   * **Author:** `Yimer Pineda`
   * **GUI Framework:** `Toga`

4. **Ajustar metadatos (Opcional pero recomendado):**
   * Editar el archivo `pyproject.toml` en la raíz del proyecto para acortar la descripción general (menos de 80 caracteres para evitar advertencias de compilación).

---

## Fase 3: Desarrollo y Pruebas Locales (Modo Escritorio / Dev)

Antes de compilar para Android, se valida que la estructura base de Toga corra correctamente en el sistema operativo local.

1. **Ejecutar el entorno de desarrollo de Briefcase:**
   ```bash
   briefcase dev
   ```
   *Nota técnica:* En Toga, los componentes gráficos tienen nombres específicos. Por ejemplo, el campo de texto multilínea se define estrictamente como `toga.MultilineTextInput` (evitando errores como `MultilineInput`).

---

## Fase 4: Creación y Compilación del Entorno Android

Una vez validada la app, se configuran las herramientas de compilación para dispositivos móviles (JDK y Android SDK).

1. **Crear la plantilla de Android:**
   ```bash
   briefcase create android
   ```
   * *Nota:* Durante este proceso, Briefcase descargará automáticamente el JDK 17 y las herramientas de línea de comandos del SDK de Android si no están presentes. Se deben aceptar las licencias escribiendo `y` en la terminal cuando se solicite.
2. **Construir el APK definitivo:**
   ```bash
   briefcase build android
   ```
   * *Nota:* Este comando descargará Gradle y empaquetará todo el código fuente y las dependencias (como SQLite) en un paquete compilado.

---

## Fase 5: Ubicación del Instalable y Distribución

Una vez finalizada la compilación exitosa, el archivo de instalación para Android (`.apk`) se genera en la siguiente ruta relativa dentro del proyecto:

```text
build\CronosDownApp\android\gradle\app\build\outputs\apk\debug\app-debug.apk
```

Para probarlo, basta con transferir este archivo al dispositivo móvil mediante cable USB, Google Drive o mensajería, habilitar la instalación de fuentes desconocidas e instalarlo.