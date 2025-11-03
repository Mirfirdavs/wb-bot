# Заглушка хранилища транзакций
TRANSACTIONS = []


def save_transaction(user_id: int, amount: int) -> None:
    TRANSACTIONS.append({"user_id": user_id, "amount": amount, "status": "pending"})
