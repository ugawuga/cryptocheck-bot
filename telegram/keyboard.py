LABEL_YES = "✅"
LABEL_NO = "❌"
LABEL_BACK = "↩️"
LABEL_NEXT = "➡️️"
LABEL_REPLENISH = "Пополнить "
LABEL_CHECK = "сформировать чек "
LABEL_CASH = "обналичить чек "
LABEL_SEND = "Продолжить "


CB_DATA_YES = "YES"
CB_DATA_NO = "NO"
CB_DATA_BACK = "BACK"
CB_DATA_NEXT = "NEXT"
CB_DATA_REPLENISH = "REPLENISH"
CB_DATA_CHECK = "CHECK"
CB_DATA_CASH = "CASH"
CB_DATA_SEND = "SEND"


BUTTON_NO = {"callback_data": CB_DATA_NO, "text": LABEL_NO}
BUTTON_YES = {"callback_data": CB_DATA_YES, "text": LABEL_YES}
BUTTON_CUMBACK = {"callback_data": CB_DATA_BACK, "text": LABEL_BACK}
BUTTON_NEXT = {"callback_data": CB_DATA_NEXT, "text": LABEL_NEXT}
BUTTON_CHECK = {"callback_data": CB_DATA_CHECK, "text": LABEL_CHECK}
BUTTON_CASH = {"callback_data": CB_DATA_CASH, "text": LABEL_CASH}
BUTTON_REPLENISH = {"callback_data": CB_DATA_REPLENISH, "text": LABEL_REPLENISH}
BUTTON_SEND = {"callback_data": CB_DATA_SEND, "text": LABEL_SEND}


yes_or_no_keyboard = [
    [BUTTON_NO, BUTTON_YES],
]
back_or_next_keyboard = [
    [BUTTON_CUMBACK, BUTTON_NEXT],
]
blockchain_keyboard = [
    [BUTTON_REPLENISH, BUTTON_CASH, BUTTON_CHECK],
]