import uuid

# Моковые настройки (заглушки) для YooKassa API
YOOKASSA_SHOP_ID = "demo_shop_id"  # Идентификатор магазина (заменить на реальный)
YOOKASSA_SECRET_KEY = "demo_secret_key"  # Секретный ключ API (заменить на реальный)


def create_payment_link(amount: float) -> str:
    """
    Создает платеж в YooKassa и возвращает ссылку для оплаты.
    Сейчас функция возвращает тестовый URL (заглушка).
    В реальной интеграции здесь будет запрос к YooKassa и получение confirmation_url.
    """
    # TODO: Реализовать реальный запрос к YooKassa API.
    # Пример (псевдокод):
    # response = requests.post("https://api.yookassa.ru/v3/payments",
    #     auth=(YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY),
    #     json={
    #         "amount": {"value": f"{amount:.2f}", "currency": "RUB"},
    #         "confirmation": {"type": "redirect", "return_url": "https://your-site.com/return"},
    #         "description": "Donation"
    #     }
    # )
    # payment_url = response.json()["confirmation"]["confirmation_url"]
    # return payment_url

    # Для демонстрации создаем фейковый уникальный идентификатор платежа и формируем ссылку:
    payment_id = uuid.uuid4()
    return f"https://yookassa.ru/payments/{payment_id}"


def save_transaction(user_id: int, amount: float):
    """
    Сохраняет информацию о транзакции (мок-функция).
    В реальной реализации здесь можно сохранить данные транзакции в базе данных.
    """
    # Мокаем сохранение: выводим информацию (в продакшн-коде заменить на запись в БД)
    print(f"[TRANSACTION] Пользователь {user_id} пожертвовал {amount} RUB")
