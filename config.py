
LOGO_PATH: str = "assets/beauty_logo.png"
FONT_FAMILY: str = "Tahoma"

# Цвета в RGB (удобно для Qt)
COLOR_MAIN = (255, 255, 255)        # Белый — фон карточек
COLOR_SECONDARY = (225, 228, 255)  # Светло-голубой — фон приложения / акценты
COLOR_ATTENTION = (255, 74, 109)   # Розово-красный — скидки, кнопки

# Дополнительные цвета для UI
COLOR_TEXT_PRIMARY = (33, 33, 33)      # Основной текст
COLOR_TEXT_SECONDARY = (102, 102, 102) # Доп. текст (время, старая цена)
COLOR_PRICE = (46, 125, 50)            # Зелёный — цена
COLOR_DISCOUNT = (211, 47, 47)         # Красный — скидка
COLOR_BUTTON_BOOK = (56, 142, 60)      # Темно-зелёный — "Записаться"
COLOR_BUTTON_ADMIN = (25, 118, 210)    # Синий — "Редактировать"
COLOR_BUTTON_DANGER = (211, 47, 47)    # Красный — "Удалить"

def rgb_to_hex(rgb: tuple) -> str:
    """Преобразует (R, G, B) → '#RRGGBB'"""
    return f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"

################ DB CONSTANTS  ################
DB_HOST = "localhost"
DB_PORT = 3306
DB_NAME = "beauty_salon"
DB_USER = "kali"
DB_PASSWORD = "Kali@2025!"