import re
import requests
from requests import Response
from utils.fapper import Map
from utils.is_unique import is_unique
from api.api import get_transactions, get_user, create_user
from api.rest import SUCCESS_MESSAGE
from telegram.keyboard import back_or_next_keyboard, yes_or_no_keyboard, blockchain_keyboard, CB_DATA_NEXT, \
    CB_DATA_NO, CB_DATA_BACK, CB_DATA_YES, BUTTON_YES, BUTTON_CUMBACK, CB_DATA_CASH, CB_DATA_CHECK, CB_DATA_REPLENISH

START_NODE_ID = "start_id"
BLOCKCHAIN_NODE_ID = "blockchain_id"
REFUSE_ID = "refuse_id"
ADDRESS_NODE_ID = "address_node_id"
GO_BACK_ID = "go_back_id"
SEND_NODE_ID = "send_id"
FORM_CHECK_ID = "form_check_id"
GET_CASH_ID = "get_cash_id"
FORM_CHECK_SENDER_ID = "get_sender_id"
FORM_WRONG_ID = "wrong_number_id"
SUCCESS_TRANSACTION_ID = "success_transaction_id"
INVALID_ID = "invalid_bcs_id"


def get_url(token: str, method: str):
    return "https://api.telegram.org/bot" + token + "/" + method


def transaction_condition(transaction: object) -> bool:
    return transaction.excepted == "None" and transaction.confirmations > 1


class Bot:
    def __init__(self, token: str, chat_id: str):
        self.bcs_address = ""
        self.token = token
        self.chat_id = chat_id
        self.last_message_id = None
        self.current_node = START_NODE_ID
        self.go_to_node(node=self.current_node)

    def send_message(self, options: object) -> Response:
        options["chat_id"] = self.chat_id
        res = requests.post(get_url(self.token, "sendMessage"), json=options)
        return res

    def edit_message(self, options: object):
        options["chat_id"] = self.chat_id
        options["message_id"] = self.last_message_id
        requests.post(get_url(self.token, "editMessageText"), json=options)

    def answer_callback_query(self, callback_query_id: str):
        requests.post(get_url(self.token, "answerCallbackQuery"), json={"callback_query_id": callback_query_id})

    def answer_callback_data(self, callback_data_id: str):
        requests.post(get_url(self.token, "answerCallbackData"), json={"callback_data": callback_data_id})

    def go_to_node(self, node: str):
        nodes = self.render()
        if node in nodes:
            self.current_node = node
            data = nodes[node]["data"]
            if self.last_message_id is None:
                res = self.send_message(options=data)
                json = res.json()
                self.last_message_id = json["result"]["message_id"]
            else:
                self.edit_message(options=data)
        else:
            print(f"no results for {node}")

    def handle_input(self, text: str):
        dialogue_node = self.render()[self.current_node]
        func = dialogue_node["func"]

        next_id = func(msg=text)
        print(next_id, text)
        if next_id is not None:
            self.go_to_node(node=next_id)

    def get_bcs_address(self, msg: str):
        self.bcs_address = msg
        res = get_user(str(self.chat_id))

        if res.state == SUCCESS_MESSAGE:
            print(res.data)
        else:
            print('Creating user..')
            new_user_res = create_user(str(self.chat_id), {
                "bcs_address": self.bcs_address,
                "balance": 0
            })
            print(new_user_res.state)

        return INVALID_ID if not re.match(r"B.{33}", msg) else GO_BACK_ID

    def check_transaction(self, msg: str):
        res = get_transactions("BNYRnkPPkRuPmtwQWexpQ1ECXgYdFMPL9H", "a3c3077f9c5c9e522534f529559dd14d07830ed4")
        if res.state == SUCCESS_MESSAGE:
            res_map = Map(res.data)
            transactions = res_map.transactions

            users_transactions = filter(lambda t: t.sender == self.bcs_address, transactions)
            users_transactions_list = list(users_transactions)
            if len(users_transactions_list) == 0:
                return FORM_WRONG_ID

            user_transaction_ids = map(lambda t: t.transactionId, users_transactions_list)
            user_transaction_ids_list = list(user_transaction_ids)
            if not is_unique(user_transaction_ids_list):
                return FORM_WRONG_ID

            found_transaction = next((t for t in users_transactions_list if transaction_condition(t)), None)
            is_valid = found_transaction is not None

        return FORM_WRONG_ID if not is_valid else FORM_CHECK_ID

    def render(self):
        return {
            f"{REFUSE_ID}": {
                "func": lambda msg: ADDRESS_NODE_ID if msg == CB_DATA_YES else None,
                "data": {
                    "text": "Получить bcs-address можно на сайте: https://meeh.com/ . \n "
                            "Как только получите адресс нажмите на кнопку ✅",
                    "reply_markup": {"inline_keyboard": [[BUTTON_YES]]}
                }
            },
            f"{START_NODE_ID}": {
                "func": lambda msg: ADDRESS_NODE_ID if msg == CB_DATA_YES else REFUSE_ID if msg == CB_DATA_NO else None,
                "data": {
                    "text": "это тестовый бот BCS. Для начала работы необходимо привязать BCS адресс к боту \n"
                            "У вас есть bcs-address? ",
                    "reply_markup": {"inline_keyboard": yes_or_no_keyboard}
                }
            },
            f"{ADDRESS_NODE_ID}": {
                "func": lambda msg: self.get_bcs_address(msg),
                "data": {
                    "text": "Введите bcs-address:",
                }
            },
            f"{INVALID_ID}": {
                "func": lambda msg: ADDRESS_NODE_ID if msg == CB_DATA_BACK else None,
                "data": {
                    "text": "Вы ввели некорректный bcs-address. Пожалуйста вернитесь назад",
                    "reply_markup": {"inline_keyboard": [[BUTTON_CUMBACK]]}
                }
            },
            f"{GO_BACK_ID}": {

                "func": lambda msg: BLOCKCHAIN_NODE_ID if msg == CB_DATA_NEXT
                else ADDRESS_NODE_ID if msg == CB_DATA_BACK else None,
                "data": {
                    "text": f"bcs-address: {self.bcs_address}",
                    "reply_markup": {"inline_keyboard": back_or_next_keyboard},
                }
            },
            f"{BLOCKCHAIN_NODE_ID}": {

                "func": lambda msg: SEND_NODE_ID if msg == CB_DATA_REPLENISH else FORM_CHECK_ID if msg == CB_DATA_CHECK
                else GET_CASH_ID if msg == CB_DATA_CASH else None,
                "data": {
                    "text": "Это бот который чет делает. Я не придумал че тут написать. Можно пока потыкаться",
                    "reply_markup": {"inline_keyboard": blockchain_keyboard}
                }
            },
            f"{SEND_NODE_ID}": {

                "func": lambda msg: self.check_transaction(msg),
                "data": {
                    "text": "Отправьте токены на нужный вам адресс. Если отправили, нажмите продолжить",
                    "reply_markup": {"inline_keyboard": back_or_next_keyboard},
                }
            },

            f"{FORM_WRONG_ID}": {
                "func": lambda msg: SEND_NODE_ID if msg == CB_DATA_BACK else None,
                "data": {
                    "text": "до связи...",
                    "reply_markup": {"inline_keyboard": [[BUTTON_CUMBACK]]},
                }
            },
            f"{FORM_CHECK_ID}": {
                "func": lambda msg: BLOCKCHAIN_NODE_ID if msg == CB_DATA_BACK else None,
                "data": {
                    "text": "C кайфом",
                    "reply_markup": {"inline_keyboard": [[BUTTON_CUMBACK]]},
                }
            },
        }
