"""
Funciones auxiliares (helpers) para los tests de Sauce Demo.

Contiene utilidades reusables:
- Configuracion del WebDriver de Chrome.
- Logger basico.
- Espera explicita y wrappers de interaccion.
- Login reutilizable.
- Captura de screenshots ante fallos.

El objetivo es mantener los tests cortos y centrados en lo que validan,
delegando los detalles tecnicos a este modulo.
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils.locators import InventoryLocators, LoginLocators


# Rutas base del proyecto
PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"
SCREENSHOTS_DIR = REPORTS_DIR / "screenshots"
DATOS_DIR = PROJECT_ROOT / "datos"

# Tiempos de espera por defecto (segundos)
DEFAULT_TIMEOUT = 15


# ---------------------------------------------------------------------------
# Logger
# ---------------------------------------------------------------------------
def get_logger(nombre: str = "saucedemo") -> logging.Logger:
    """Devuelve un logger configurado con formato uniforme."""
    logger = logging.getLogger(nombre)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formato = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formato)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


log = get_logger()


# ---------------------------------------------------------------------------
# Configuracion de datos
# ---------------------------------------------------------------------------
def cargar_credenciales() -> dict:
    """Lee datos/credenciales.json y devuelve un dict con base_url, usuario y password."""
    archivo = DATOS_DIR / "credenciales.json"
    with open(archivo, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Configuracion del WebDriver
# ---------------------------------------------------------------------------
def crear_driver(headless: bool = True) -> WebDriver:
    """
    Crea e inicializa un driver de Chrome.

    Por defecto se ejecuta en modo headless para poder correr los tests en
    entornos sin interfaz grafica (CI, contenedores, etc).
    """
    opciones = Options()
    if headless:
        # 'new' es el modo headless moderno de Chrome (recomendado en >= 109).
        opciones.add_argument("--headless=new")
    opciones.add_argument("--no-sandbox")
    opciones.add_argument("--disable-dev-shm-usage")
    opciones.add_argument("--disable-gpu")
    opciones.add_argument("--window-size=1920,1080")
    opciones.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=opciones)
    # Espera implicita pequena como red de seguridad; las validaciones criticas
    # usan esperas explicitas.
    driver.implicitly_wait(2)
    log.info("WebDriver de Chrome iniciado (headless=%s)", headless)
    return driver


# ---------------------------------------------------------------------------
# Esperas explicitas
# ---------------------------------------------------------------------------
def esperar_visible(driver: WebDriver, localizador: tuple, timeout: int = DEFAULT_TIMEOUT):
    """Espera explicita hasta que un elemento sea visible y lo devuelve."""
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located(localizador)
    )


def esperar_clickeable(driver: WebDriver, localizador: tuple, timeout: int = DEFAULT_TIMEOUT):
    """Espera explicita hasta que un elemento sea clickeable y lo devuelve."""
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable(localizador)
    )


def esperar_url_contiene(driver: WebDriver, fragmento: str, timeout: int = DEFAULT_TIMEOUT) -> bool:
    """Espera explicita hasta que la URL contenga el fragmento indicado."""
    return WebDriverWait(driver, timeout).until(EC.url_contains(fragmento))


def click_seguro(driver: WebDriver, elemento) -> None:
    """
    Click robusto: scrollea el elemento al viewport y dispara el click via JS.

    En modo headless algunos botones quedan fuera del viewport y un click
    nativo no llega a registrarse. Esta funcion evita ese problema.
    """
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elemento)
    driver.execute_script("arguments[0].click();", elemento)


# ---------------------------------------------------------------------------
# Flujos reutilizables
# ---------------------------------------------------------------------------
def ir_a_login(driver: WebDriver, base_url: str) -> None:
    """Navega a la pagina principal de Sauce Demo (login)."""
    log.info("Navegando a %s", base_url)
    driver.get(base_url)
    # Aseguramos que la pagina de login este lista antes de continuar
    esperar_visible(driver, LoginLocators.USERNAME_INPUT)


def hacer_login(driver: WebDriver, usuario: str, password: str) -> None:
    """
    Realiza el flujo de login completo en Sauce Demo.

    Asume que el driver ya esta en la pagina de login.
    """
    log.info("Ingresando credenciales para el usuario '%s'", usuario)

    campo_usuario = esperar_visible(driver, LoginLocators.USERNAME_INPUT)
    campo_usuario.clear()
    campo_usuario.send_keys(usuario)

    campo_password = esperar_visible(driver, LoginLocators.PASSWORD_INPUT)
    campo_password.clear()
    campo_password.send_keys(password)

    boton_login = esperar_clickeable(driver, LoginLocators.LOGIN_BUTTON)
    boton_login.click()

    # Esperamos la redireccion a inventario como confirmacion del login.
    esperar_url_contiene(driver, "/inventory.html")
    esperar_visible(driver, InventoryLocators.INVENTORY_CONTAINER)
    log.info("Login exitoso: redirigido a /inventory.html")


# ---------------------------------------------------------------------------
# Evidencias: screenshots
# ---------------------------------------------------------------------------
def guardar_screenshot(driver: WebDriver, nombre_test: str) -> Path:
    """
    Guarda un screenshot en reports/screenshots/ con timestamp.
    Devuelve la ruta del archivo generado.
    """
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"{nombre_test}_{timestamp}.png"
    ruta = SCREENSHOTS_DIR / nombre_archivo
    try:
        driver.save_screenshot(str(ruta))
        log.warning("Screenshot de fallo guardado en %s", ruta)
    except Exception as exc:  # noqa: BLE001
        # No queremos enmascarar el error original del test si esto falla.
        log.error("No se pudo guardar el screenshot: %s", exc)
    return ruta
