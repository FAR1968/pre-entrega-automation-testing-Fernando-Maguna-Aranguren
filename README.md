# Pre Entrega – Automation Testing

Curso **QA Automation – Talento TECH (Clases 1 a 8)**
Autor: **Fernando Maguna Aranguren**
Repositorio: <https://github.com/FAR1968/pre-entrega-automation-testing-Fernando-Maguna-Aranguren>

---

## 1. Propósito del proyecto

Automatizar flujos básicos de navegación web sobre el sitio demo
[https://www.saucedemo.com/](https://www.saucedemo.com/) utilizando
**Selenium WebDriver** y **Python**, con estructura de pruebas en **Pytest**.

Se cubren los tres casos de prueba pedidos en la consigna:

| # | Caso | Validaciones principales |
|---|------|--------------------------|
| 1 | **Login automatizado** | Navegar al sitio, ingresar `standard_user` / `secret_sauce`, validar redirección a `/inventory.html` y presencia de los textos **Products** y **Swag Labs**. Espera explícita. |
| 2 | **Navegación y verificación del catálogo** | Título de inventario correcto, al menos 1 producto visible, elementos clave de UI (menú, filtro de orden, carrito), y registro del nombre/precio del primer producto. |
| 3 | **Interacción con productos / carrito** | Agregar el primer producto al carrito, validar que el contador del carrito sube a `1`, navegar a `/cart.html` y validar que el producto aparece con el mismo nombre y precio. |

---

## 2. Tecnologías utilizadas

- **Python 3.12**
- **Selenium WebDriver 4** (Chrome, headless)
- **Pytest 9** + **pytest-html** (reportes HTML)
- **webdriver-manager** (gestión opcional del driver; Selenium 4 trae **Selenium Manager** integrado)
- **Git / GitHub** para control de versiones

---

## 3. Estructura del proyecto

```
pre-entrega-automation-testing-Fernando-Maguna-Aranguren/
├── datos/
│   └── credenciales.json        # URL base, usuario y password de prueba
├── reports/
│   ├── reporte.html             # Reporte HTML generado por pytest-html
│   └── screenshots/             # Capturas automáticas ante fallos
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Fixtures (driver, credenciales) + hook de screenshots
│   └── test_saucedemo.py        # Los 3 casos de prueba
├── utils/
│   ├── __init__.py
│   ├── helpers.py               # Funciones auxiliares: driver, login, esperas, screenshots, logger
│   └── locators.py              # Localizadores centralizados (Login, Inventory, Cart)
├── pytest.ini                   # Configuración de pytest (markers, logs, etc)
├── requirements.txt             # Dependencias del proyecto
├── .gitignore
└── README.md
```

> El código se organiza en **mínimo 2 archivos separados** entre tests y funciones
> auxiliares, como pide la consigna: `tests/test_saucedemo.py` (tests) y
> `utils/helpers.py` + `utils/locators.py` (helpers).

---

## 4. Instalación

### 4.1 Requisitos previos

- Python 3.10 o superior (probado con 3.12).
- Google Chrome instalado en el sistema.
- Conexión a internet (para que Selenium Manager descargue el ChromeDriver compatible).

### 4.2 Crear y activar entorno virtual (recomendado)

```bash
python -m venv .venv
# Linux / macOS:
source .venv/bin/activate
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
```

### 4.3 Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## 5. Ejecución de las pruebas

### 5.1 Comando solicitado por la consigna

```bash
pytest tests/test_saucedemo.py -v --html=reports/reporte.html --self-contained-html
```

Esto:

- Ejecuta los tres casos de prueba.
- Genera el reporte HTML en `reports/reporte.html` (autocontenido en un único archivo, fácil de compartir).
- Si algún test falla, guarda automáticamente una captura en `reports/screenshots/`.

### 5.2 Otros comandos útiles

| Acción | Comando |
|--------|---------|
| Solo verificar que los tests son detectables (collection) | `pytest --collect-only` |
| Ejecutar un único caso | `pytest tests/test_saucedemo.py::test_login_exitoso_con_usuario_estandar -v` |
| Ejecutar por marker (smoke / login / catalog / cart) | `pytest -m smoke` |
| Salida con logs en tiempo real | (ya activado en `pytest.ini` con `log_cli`) |

---

## 6. Resultado de la última ejecución

```
============================== 3 passed in 3.57s ===============================
```

- `test_login_exitoso_con_usuario_estandar` ✓
- `test_catalogo_inventario_muestra_productos_y_elementos_ui` ✓
- `test_agregar_primer_producto_al_carrito` ✓

El reporte HTML correspondiente se encuentra versionado en [`reports/reporte.html`](reports/reporte.html).

---

## 7. Características de calidad incluidas

- **Tests independientes**: cada test usa un WebDriver nuevo (fixture `driver`) y vuelve a iniciar sesión por su cuenta. No comparten estado.
- **Esperas explícitas** (`WebDriverWait` + `expected_conditions`) para sincronizar acciones – no se usan `time.sleep()` en los tests.
- **Localizadores centralizados** en `utils/locators.py` – si cambia la UI, se actualiza un solo archivo.
- **Screenshots automáticas en fallos** vía hook `pytest_runtest_makereport` en `conftest.py`, guardadas en `reports/screenshots/`.
- **Logging** configurado tanto en helpers como en `pytest.ini` (`log_cli = true`) para trazabilidad de la ejecución.
- **Markers** personalizados (`smoke`, `login`, `catalog`, `cart`) para poder filtrar la ejecución por tipo de caso.
- **Nomenclatura significativa** en español y comentarios descriptivos en cada paso de cada caso de prueba.

---

## 8. Notas de implementación

- En modo **headless** de Chrome, algunos botones de Sauce Demo no reciben bien el click nativo de Selenium si quedan fuera del viewport. Por eso se agregó un helper `click_seguro()` que primero hace `scrollIntoView` y dispara el click desde JavaScript. Para tests en modo no-headless, un `element.click()` clásico también funciona.
- Se usa Selenium Manager (integrado en Selenium 4) para resolver el ChromeDriver automáticamente; no hace falta descargarlo a mano. Si el entorno no tiene salida a internet, `webdriver-manager` queda como alternativa documentada en `requirements.txt`.
