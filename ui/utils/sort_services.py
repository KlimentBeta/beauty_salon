from typing import List, Dict, Optional, Callable

DISCOUNT_RANGES = [
    ("Все", None, None),
    ("0% – 5%", 0.0, 5.0),
    ("5% – 15%", 5.0, 15.0),
    ("15% – 30%", 15.0, 30.0),
    ("30% – 70%", 30.0, 70.0),
    ("70% – 100%", 70.0, 100.0),
]

def calculate_discount_percent(service: Dict) -> float:
    """Вычисляет размер скидки в процентах из поля Discount."""
    try:
        discount_factor = float(service.get('Discount', 1.0))
        # Защита от некорректных значений
        if discount_factor < 0:
            discount_factor = 0.0
        elif discount_factor > 1.0:
            discount_factor = 1.0
        return round((1.0 - discount_factor) * 100.0, 2)
    except (ValueError, TypeError):
        return 0.0

def filter_services_by_discount(services: List[Dict], selected_range: str) -> List[Dict]:
    """
    Фильтрует услуги по выбранному диапазону скидки.
    
    :param services: список услуг
    :param selected_range: название диапазона (например, "15% – 30%")
    :return: отфильтрованный список
    """
    # Находим границы
    min_d, max_d = None, None
    for label, mn, mx in DISCOUNT_RANGES:
        if label == selected_range:
            min_d, max_d = mn, mx
            break

    # "Все" — возвращаем как есть
    if min_d is None and max_d is None:
        return services[:]

    filtered = []
    for s in services:
        d = calculate_discount_percent(s)
        # Условие: min <= d < max, НО для последнего диапазона — до 100 включительно
        if max_d == 100.0:
            # Разрешаем 100.0% (например, при Discount = 0.0)
            include = min_d <= d <= max_d
        else:
            include = min_d <= d < max_d
        if include:
            filtered.append(s)
    return filtered

def sort_services_by_cost(services, reverse=False, extra_conditions=None):
    """
    Сортирует список услуг по стоимости (Cost).
    
    :param services: список словарей (как из fetch_all)
    :param reverse: False → по возрастанию, True → по убыванию
    :param extra_conditions: (опционально) функция-фильтр вида (srv) -> bool
    :return: новый отсортированный список
    """
    # Применяем дополнительные условия (например, только активные)
    filtered = services
    if extra_conditions and callable(extra_conditions):
        filtered = [s for s in services if extra_conditions(s)]

    # Сортируем вручную — в будущем сюда можно добавить сложную логику
    try:
        return sorted(
            filtered,
            key=lambda s: float(s.get('Cost', 0)),
            reverse=reverse
        )
    except (ValueError, TypeError) as e:
        # fallback: оставить как есть, но залогировать
        print(f"⚠️ Ошибка при сортировке по стоимости: {e}")
        return filtered
    

def search_services(services: List[Dict], query: str) -> List[Dict]:
    """
    Ищет услуги, где Title или Description содержат query (регистронезависимо).
    Пустой или None query → возвращает все входные услуги.
    """
    if not query or not query.strip():
        return services[:]

    q = query.strip().lower()
    result = []
    for s in services:
        title = str(s.get('Title', '')).lower()
        desc = str(s.get('Description', '')).lower()
        if q in title or q in desc:
            result.append(s)
    return result