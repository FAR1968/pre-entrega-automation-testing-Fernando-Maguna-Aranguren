"""
Tests de automatizacion para https://www.saucedemo.com/

Casos cubiertos (segun consignas del curso QA Automation - Pre Entrega):
1. Login automatizado con credenciales validas y verificacion de redireccion.
2. Navegacion y verificacion del catalogo de productos.
3. Interaccion con productos: agregar al carrito y verificar carrito.

Cada test es independiente: usa un driver fresco (fixture `driver`)
y vuelve a iniciar sesion cuando lo necesita. No comparten estado.
"""

import pytest

from utils.helpers import (
    click_seguro,
    esperar_visible,
    hacer_login,
    ir_a_login,
    log,
)
from utils.locators import CartLocators, InventoryLocators


# ---------------------------------------------------------------------------
# CASO 1: Login automatizado
# ---------------------------------------------------------------------------
@pytest.mark.smoke
@pytest.mark.login
def test_login_exitoso_con_usuario_estandar(driver, credenciales):
    """
    Verifica el login con el usuario 'standard_user'.

    Criterios:
    - Navegar a saucedemo.com
    - Ingresar credenciales validas
    - Validar redireccion a /inventory.html
    - Validar presencia de los textos 'Products' y 'Swag Labs'
    - Toda la sincronizacion usa esperas explicitas
    """
    log.info("=== Caso 1: Login automatizado ===")

    # 1) Ir a la pagina de login.
    ir_a_login(driver, credenciales["base_url"])

    # 2) Hacer login con las credenciales validas.
    hacer_login(driver, credenciales["usuario_valido"], credenciales["password_valido"])

    # 3) Validar redireccion a /inventory.html.
    assert "/inventory.html" in driver.current_url, (
        f"Se esperaba redireccion a /inventory.html, URL actual: {driver.current_url}"
    )

    # 4) Validar presencia del titulo 'Products'.
    titulo_pagina = esperar_visible(driver, InventoryLocators.PAGE_TITLE)
    assert titulo_pagina.text.strip() == "Products", (
        f"Se esperaba el titulo 'Products', se encontro: '{titulo_pagina.text}'"
    )

    # 5) Validar presencia del logo/encabezado 'Swag Labs'.
    logo = esperar_visible(driver, InventoryLocators.APP_LOGO)
    assert logo.text.strip() == "Swag Labs", (
        f"Se esperaba 'Swag Labs', se encontro: '{logo.text}'"
    )

    log.info("Caso 1 OK: login exitoso y elementos esperados visibles")


# ---------------------------------------------------------------------------
# CASO 2: Navegacion y verificacion del catalogo
# ---------------------------------------------------------------------------
@pytest.mark.smoke
@pytest.mark.catalog
def test_catalogo_inventario_muestra_productos_y_elementos_ui(driver, credenciales):
    """
    Verifica el catalogo de productos.

    Criterios:
    - Titulo correcto de la pagina ('Products').
    - Presencia de al menos un producto visible.
    - Elementos de UI clave presentes: menu (burger), filtro de orden y carrito.
    - Listar (loggear) el nombre y precio del primer producto.
    """
    log.info("=== Caso 2: Navegacion y verificacion del catalogo ===")

    # Login previo (cada test es independiente).
    ir_a_login(driver, credenciales["base_url"])
    hacer_login(driver, credenciales["usuario_valido"], credenciales["password_valido"])

    # 1) Titulo de la pagina de inventario.
    titulo = esperar_visible(driver, InventoryLocators.PAGE_TITLE)
    assert titulo.text.strip() == "Products", (
        f"Titulo de inventario incorrecto: '{titulo.text}'"
    )

    # 2) Presencia de al menos un producto.
    productos = driver.find_elements(*InventoryLocators.INVENTORY_ITEMS)
    assert len(productos) >= 1, "No se encontraron productos visibles en el inventario"
    log.info("Productos visibles en el inventario: %d", len(productos))

    # 3) Elementos importantes de la UI.
    esperar_visible(driver, InventoryLocators.BURGER_MENU_BUTTON)
    esperar_visible(driver, InventoryLocators.SORT_DROPDOWN)
    esperar_visible(driver, InventoryLocators.SHOPPING_CART_LINK)

    # 4) Listar nombre y precio del primer producto.
    primer_producto = productos[0]
    nombre = primer_producto.find_element(*InventoryLocators.INVENTORY_ITEM_NAME).text
    precio = primer_producto.find_element(*InventoryLocators.INVENTORY_ITEM_PRICE).text

    assert nombre, "El nombre del primer producto esta vacio"
    assert precio.startswith("$"), f"El precio no tiene formato esperado: '{precio}'"

    log.info("Primer producto -> Nombre: '%s' | Precio: '%s'", nombre, precio)
    log.info("Caso 2 OK")


# ---------------------------------------------------------------------------
# CASO 3: Interaccion con productos / Carrito
# ---------------------------------------------------------------------------
@pytest.mark.smoke
@pytest.mark.cart
def test_agregar_primer_producto_al_carrito(driver, credenciales):
    """
    Verifica el flujo de agregar el primer producto al carrito.

    Criterios:
    - Agregar el primer producto al carrito.
    - El contador (badge) del carrito debe incrementarse a 1.
    - Navegar a /cart.html.
    - El producto agregado debe aparecer correctamente en el carrito
      (mismo nombre y mismo precio que en el listado).
    """
    log.info("=== Caso 3: Agregar primer producto al carrito ===")

    # Login previo (independencia entre tests).
    ir_a_login(driver, credenciales["base_url"])
    hacer_login(driver, credenciales["usuario_valido"], credenciales["password_valido"])

    # Capturamos nombre y precio del primer producto ANTES de agregarlo,
    # para luego compararlo en el carrito.
    productos = driver.find_elements(*InventoryLocators.INVENTORY_ITEMS)
    assert productos, "No hay productos en el inventario, no se puede ejecutar el test"

    primer_producto = productos[0]
    nombre_esperado = primer_producto.find_element(*InventoryLocators.INVENTORY_ITEM_NAME).text
    precio_esperado = primer_producto.find_element(*InventoryLocators.INVENTORY_ITEM_PRICE).text
    log.info("Producto a agregar -> '%s' (%s)", nombre_esperado, precio_esperado)

    # 1) Click en "Add to cart" del primer producto.
    botones_agregar = driver.find_elements(*InventoryLocators.ADD_TO_CART_BUTTONS)
    assert botones_agregar, "No se encontraron botones 'Add to cart' en el inventario"
    click_seguro(driver, botones_agregar[0])

    # 2) Verificar que el badge del carrito muestre '1'.
    badge = esperar_visible(driver, InventoryLocators.SHOPPING_CART_BADGE)
    assert badge.text.strip() == "1", (
        f"Se esperaba contador de carrito '1', se encontro: '{badge.text}'"
    )
    log.info("Badge del carrito = %s", badge.text)

    # 3) Navegar al carrito.
    link_carrito = esperar_visible(driver, InventoryLocators.SHOPPING_CART_LINK)
    click_seguro(driver, link_carrito)

    # 4) Verificar que estamos en /cart.html y que el titulo es 'Your Cart'.
    assert "/cart.html" in driver.current_url, (
        f"No se navego a /cart.html, URL actual: {driver.current_url}"
    )
    titulo_carrito = esperar_visible(driver, CartLocators.CART_TITLE)
    assert titulo_carrito.text.strip() == "Your Cart"

    # 5) Verificar que el producto aparece en el carrito con su nombre y precio.
    items_carrito = driver.find_elements(*CartLocators.CART_ITEMS)
    assert len(items_carrito) == 1, (
        f"Se esperaba 1 producto en el carrito, hay {len(items_carrito)}"
    )

    nombre_en_carrito = items_carrito[0].find_element(*CartLocators.CART_ITEM_NAME).text
    precio_en_carrito = items_carrito[0].find_element(*CartLocators.CART_ITEM_PRICE).text

    assert nombre_en_carrito == nombre_esperado, (
        f"Nombre en carrito '{nombre_en_carrito}' no coincide con '{nombre_esperado}'"
    )
    assert precio_en_carrito == precio_esperado, (
        f"Precio en carrito '{precio_en_carrito}' no coincide con '{precio_esperado}'"
    )

    log.info(
        "Caso 3 OK: producto '%s' (%s) presente en el carrito",
        nombre_en_carrito,
        precio_en_carrito,
    )
