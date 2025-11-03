from services.transaction_storage import save_transaction


class PaymentService:
    @staticmethod
    def create_payment_link(user_id: int, amount: int) -> str:
        # Заглушка ссылки. Здесь будет реальный вызов к YooKassa позже.
        save_transaction(user_id, amount)
        return f"https://pay.yookassa.ru/mock?user={user_id}&amount={amount}"
