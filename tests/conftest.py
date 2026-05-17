"""
Configuracion compartida de pytest.

Define:
- Un fixture `driver` que crea/cierra el WebDriver por cada test (tests independientes).
- Un fixture `credenciales` con los datos de prueba.
- Un hook que captura screenshot automaticamente cuando un test falla.
"""

import sys
from pathlib import Path

import pytest

# Aseguramos que el root del proyecto este en sys.path para poder importar `utils`.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.helpers import cargar_credenciales, crear_driver, guardar_screenshot, log


@pytest.fixture()
def credenciales() -> dict:
    """Carga las credenciales/URL desde datos/credenciales.json."""
    return cargar_credenciales()


@pytest.fixture()
def driver():
    """
    Crea un WebDriver fresco para cada test y lo cierra al finalizar.

    Esta estrategia garantiza tests independientes: ninguna sesion
    arrastra estado (cookies, localStorage, ruta) entre pruebas.
    """
    drv = crear_driver(headless=True)
    yield drv
    try:
        drv.quit()
        log.info("WebDriver cerrado")
    except Exception as exc:  # noqa: BLE001
        log.error("Error al cerrar el WebDriver: %s", exc)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook que se ejecuta tras cada fase del test (setup, call, teardown).

    Si la fase `call` falla y el test usa el fixture `driver`, guardamos
    un screenshot en reports/screenshots/ con el nombre del test.
    """
    outcome = yield
    reporte = outcome.get_result()

    if reporte.when == "call" and reporte.failed:
        drv = item.funcargs.get("driver")
        if drv is not None:
            guardar_screenshot(drv, item.name)
