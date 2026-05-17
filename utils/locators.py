"""
Localizadores centralizados para Sauce Demo.

Mantener los selectores en un solo archivo facilita el mantenimiento:
si la pagina cambia, solo hay que actualizar este modulo.
"""

from selenium.webdriver.common.by import By


class LoginLocators:
    """Localizadores de la pagina de login (https://www.saucedemo.com/)."""

    USERNAME_INPUT = (By.ID, "user-name")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login-button")
    ERROR_MESSAGE = (By.CSS_SELECTOR, "h3[data-test='error']")


class InventoryLocators:
    """Localizadores de la pagina de inventario (/inventory.html)."""

    PAGE_TITLE = (By.CLASS_NAME, "title")  # Texto esperado: "Products"
    APP_LOGO = (By.CLASS_NAME, "app_logo")  # Texto esperado: "Swag Labs"
    INVENTORY_CONTAINER = (By.ID, "inventory_container")
    INVENTORY_ITEMS = (By.CLASS_NAME, "inventory_item")
    INVENTORY_ITEM_NAME = (By.CLASS_NAME, "inventory_item_name")
    INVENTORY_ITEM_PRICE = (By.CLASS_NAME, "inventory_item_price")

    # Elementos de interfaz importantes
    BURGER_MENU_BUTTON = (By.ID, "react-burger-menu-btn")
    SORT_DROPDOWN = (By.CLASS_NAME, "product_sort_container")
    SHOPPING_CART_LINK = (By.CLASS_NAME, "shopping_cart_link")
    SHOPPING_CART_BADGE = (By.CLASS_NAME, "shopping_cart_badge")

    # Boton "Add to cart" generico de productos (clase compartida en el listado).
    # Para agregar el primer producto, el test toma el primero de la lista.
    ADD_TO_CART_BUTTONS = (By.CSS_SELECTOR, "button.btn_inventory")


class CartLocators:
    """Localizadores del carrito (/cart.html)."""

    CART_TITLE = (By.CLASS_NAME, "title")  # Texto esperado: "Your Cart"
    CART_ITEMS = (By.CLASS_NAME, "cart_item")
    CART_ITEM_NAME = (By.CLASS_NAME, "inventory_item_name")
    CART_ITEM_PRICE = (By.CLASS_NAME, "inventory_item_price")
    CHECKOUT_BUTTON = (By.ID, "checkout")
