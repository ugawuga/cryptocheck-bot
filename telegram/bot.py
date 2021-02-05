import re
import requests
from requests import Response
from telegram.bcrypt import form_hash_key
from telegram.send_email import send_email
from telegram.send_tokens import send_to_contract_request
from utils.fapper import Map
from utils.is_unique import is_unique
from api.api import get_transactions, get_user, create_user, form_user_hash, get_user_hash, \
    update_user, check_address_exists, update_user_hash, get_anon_hash, update_anon_hash, add_anon_hash, \
    get_user_transaction, add_user_transaction, send_hash_list, send_hash_and_flag, get_used_hashes, send_used_hashes
from api.rest import SUCCESS_MESSAGE
from telegram.keyboard import back_or_next_keyboard, yes_or_no_keyboard, blockchain_keyboard, check_keyboard, \
    CB_DATA_NEXT, \
    CB_DATA_NO, CB_DATA_BACK, CB_DATA_YES, CB_DATA_HOME, BUTTON_YES, BUTTON_CUMBACK, BUTTON_HOME, CB_DATA_CASH, \
    CB_DATA_CHECK, CB_DATA_REPLENISH, \
    CB_DATA_FORM_CHECK, CB_DATA_FORM_ANON_CHECK, CB_DATA_BALANCE, CB_DATA_PAYLOAD, CB_DATA_STAT

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
USERS_CHECK_NODE_ID = "users_check_id"
ANON_CHECK_NODE_ID = "anon_check_node_id"
INVALID_USER_ID = "invalid_user_id"
CORRECT_USER_ID = "correct_user_id"
FORM_INVALID_BALANCE_ID = "invalid_balance_id"
FORM_CHECK_BALANCE_ID = "check_balance_id"
ANON_INVALID_BALANCE_ID = "anon_invalid_id"
CHECKOUT_ID = "checkout_id"
ERROR_ID = "error_id"
INVALID_HASH_ID = "invalid_hash_id"
CORRECT_HASH_ID = "correct_hash_id"
CHECK_CASH_ID = "check_cash_id"
GET_BALANCE_ID = "get_balance_id"
BALANCE_ID = "balance_id"
FORM_ANON_CHECK_ID = "anon_check_id"
GET_HASH_ID = "get_hash_id"
INVALID_FLAG_ID = "invalid_flag_id"
ANON_CHECKOUT_ID = "anon_checkout_id"
CHOOSE_HASH_ID = "choose_hash_id"
SEND_TO_CONTRACT_ID = "send_to_contract_id"
CONTRACT_RESPONSE_ID = "contract_response_id"
STATISTICS_ID = "statisitcs_id"


def get_url(token: str, method: str):
    return "https://api.telegram.org/bot" + token + "/" + method


def transaction_condition(transaction: object) -> bool:
    return transaction.excepted == "None" and transaction.confirmations > 1


class Bot:
    def __init__(self, token: str, chat_id: str):
        self.bcs_address = ""
        self.balance = 0
        self.hash = ""
        self.sender_hash = ""
        self.payment = 0
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
        print(r"""                 /\
            ____/__\____
            \  /    \  /
             \/      \/
             /\      /\
            /__\____/__\
                \  /
                 \/""")
        if not re.match(r"B.{33}", msg):
            return INVALID_ID

        self.bcs_address = msg
        res = get_user(str(self.chat_id))

        if res.state == SUCCESS_MESSAGE:
            return GO_BACK_ID
        else:
            print('Creating user..')
            new_user_res = create_user(str(self.chat_id), {
                "bcs_address": self.bcs_address,
                "balance": 0
            })
            if new_user_res.state == SUCCESS_MESSAGE:
                return GO_BACK_ID
            else:
                return ERROR_ID

    def check_for_user(self, msg: str):
        if not re.match(r"B.{33}", msg):
            return INVALID_ID
        self.bcs_address = msg

        res = check_address_exists(msg)
        if res.state == SUCCESS_MESSAGE:
            res_map = Map(res.data)
            if res_map.ok:
                return CORRECT_USER_ID
            else:
                return INVALID_USER_ID
        else:
            return ERROR_ID

    def check_transaction(self, msg: str):
        global is_valid, balance_sum
        if msg == CB_DATA_BACK:
            return BLOCKCHAIN_NODE_ID
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
            print(user_transaction_ids_list)

            for i in user_transaction_ids_list:
                if i is not None:
                    print(i, "------------------------------")
                    print("add transactions")
                    new_transactions = add_user_transaction(str(self.chat_id), {
                        "transaction_id": i,
                        "sender": "Bot",
                        "receiver": self.bcs_address,
                    })
                    print(new_transactions.data)

                    if new_transactions.state == SUCCESS_MESSAGE:
                        print("new transaction ----------------------------")
                    else:
                        return FORM_WRONG_ID
                else:
                    tx_id = get_user_transaction(str(self.chat_id))
                    if tx_id.state == SUCCESS_MESSAGE:
                        tx_id_map = Map(tx_id.data)

                        used_tx = tx_id_map.transaction_id
                        if used_tx == i:
                            return FORM_WRONG_ID
                    else:
                        return ERROR_ID

            user_transaction_balance = map(lambda t: t.evmLogs[-1], users_transactions_list)
            user_transaction_balance_list = list(user_transaction_balance)

            sum_list = []
            for i in user_transaction_balance_list:
                values = list(i.values())
                print(values)
                user_data = values[3]
                print(user_data, "raw user data")
                if len(user_data) != 0:
                    converted_data = int(user_data, 16)
                    print(converted_data, "uncut data")
                    str_data = str(converted_data)
                    print(len(str_data))
                    decimal_data = str_data[0:-6]
                    int_dec_data = int(decimal_data)
                    print(int_dec_data, "cut data")

                    if int_dec_data is not None:
                        sum_list.append(int_dec_data)
                        print(sum_list)
                        balance_sum = sum(sum_list)
                        print(balance_sum)

            if not is_unique(user_transaction_ids_list):
                return FORM_WRONG_ID

            found_transaction = next((t for t in users_transactions_list if transaction_condition(t)), None)

            is_valid = found_transaction is not None

        if is_valid:
            print(self.bcs_address, "ADDRESS")
            res = get_user(str(self.chat_id))
            if res.state == SUCCESS_MESSAGE:
                res_map = Map(res.data)
                self.balance = res_map.users.balance
            else:
                return ERROR_ID

            res = update_user(str(self.chat_id), {
                "balance": balance_sum + self.balance,
                "bcs_address": self.bcs_address
            })
            if res.state == SUCCESS_MESSAGE:
                return FORM_CHECK_ID
            else:
                return ERROR_ID
        else:
            return FORM_WRONG_ID

    def enter_balance(self, msg: str):
        self.payment = int(msg)
        res = get_user(str(self.chat_id))

        if res.state == SUCCESS_MESSAGE:
            res_map = Map(res.data)
            balance = res_map.users.balance
            if self.payment > balance:
                return ERROR_ID
            else:
                new_user_balance = update_user(str(self.chat_id), {
                    "balance": balance - self.payment,
                    "bcs_address": self.bcs_address
                })
                if new_user_balance.state == SUCCESS_MESSAGE:
                    self.balance = balance - self.payment
                    return BALANCE_ID
                else:
                    return ERROR_ID
        else:
            return ERROR_ID

    def enter_user_balance(self, msg: str):
        self.payment = int(msg)
        res = get_user(str(self.chat_id))

        if res.state == SUCCESS_MESSAGE:
            res_map = Map(res.data)
            balance = res_map.users.balance
            if self.payment > balance:
                return ERROR_ID
            else:
                new_user_balance = update_user(str(self.chat_id), {
                    "balance": balance - self.payment,
                    "bcs_address": self.bcs_address
                })
                if new_user_balance.state == SUCCESS_MESSAGE:
                    self.balance = balance - self.payment
                    send_hash = self.form_hash()
                    print(send_hash)
                    if send_hash is not None:
                        self.sender_hash = send_hash
                    return FORM_CHECK_BALANCE_ID
                else:
                    return ERROR_ID
        else:
            return ERROR_ID

    def form_hash(self):
        print('Creating hash..')
        new_user_hash = form_user_hash(str(self.chat_id), {
            "flag": False,
            "check_hash": form_hash_key("itsbondagegaywebsite"),
            "sender": self.bcs_address,
            "receiver": self.bcs_address,
            "value": self.payment
        })
        if new_user_hash.state == SUCCESS_MESSAGE:
            res = get_user_hash(str(self.chat_id))
            print(res, "____________________________________________-")
            if res.state == SUCCESS_MESSAGE:
                res_map = Map(res.data)
                print(res_map)
                user_hash = res_map.hash.check_hash
                return user_hash
            else:
                return None
        else:
            return ERROR_ID

    def get_hash(self, msg: str):
        self.hash = msg
        res = get_user_hash(str(self.chat_id))
        print(res)
        if res.state == SUCCESS_MESSAGE:
            res_map = Map(res.data)
            returned_hash = res_map.hash.check_hash
            hash_balance = res_map.hash.value
            hash_receiver = res_map.hash.receiver
            hash_flag = res_map.hash.flag
            print(hash_balance, hash_receiver, hash_flag, "___________________________")
            if self.hash == returned_hash:
                if not hash_flag:
                    if self.bcs_address == hash_receiver:
                        res = get_user(str(self.chat_id))
                        if res.state == SUCCESS_MESSAGE:
                            user_map = Map(res.data)
                            balance = user_map.users.balance
                            print(balance, "++")
                            new_user_balance = update_user(str(self.chat_id), {
                                "balance": balance + hash_balance,
                                "bcs_address": self.bcs_address
                            })
                            print(new_user_balance, "[")
                            if new_user_balance.state == SUCCESS_MESSAGE:
                                self.balance = balance + hash_balance
                                print(self.balance, "wwewewew")
                                check_flag = update_user_hash(str(self.chat_id), {
                                    "flag": True
                                })
                                if check_flag == SUCCESS_MESSAGE:
                                    print(check_flag, "________________________________________")
                                return CORRECT_HASH_ID

                            else:
                                return ERROR_ID
                        else:
                            return ERROR_ID
                    else:
                        return ERROR_ID
                else:
                    return INVALID_FLAG_ID
            else:
                return INVALID_HASH_ID
        else:
            return ERROR_ID

    def anon_hash(self):
        print('Creating hash..')
        new_user_hash = add_anon_hash(str(self.chat_id), {
            "flag": False,
            "check_hash": form_hash_key("itsbondagegaywebsite"),
            "sender": self.bcs_address,
            "value": self.payment
        })
        if new_user_hash.state == SUCCESS_MESSAGE:
            res = get_anon_hash(str(self.chat_id))
            print(res, "____________________________________________-")
            if res.state == SUCCESS_MESSAGE:
                res_map = Map(res.data)
                print(res_map)
                user_hash = res_map.hash.check_hash
                return user_hash
            else:
                return None
        else:
            return ERROR_ID

    def enter_anon_balance(self, msg: str):
        self.payment = int(msg)
        res = get_user(str(self.chat_id))
        if res.state == SUCCESS_MESSAGE:
            res_map = Map(res.data)
            balance = res_map.users.balance
            if self.payment > balance:
                return FORM_INVALID_BALANCE_ID
            else:
                new_user_balance = update_user(str(self.chat_id), {
                    "balance": balance - self.payment,
                    "bcs_address": self.bcs_address
                })
                if new_user_balance.state == SUCCESS_MESSAGE:
                    self.balance = balance - self.payment
                    send_hash = self.anon_hash()
                    print(send_hash)
                    if send_hash is not None:
                        self.sender_hash = send_hash
                    return FORM_CHECK_BALANCE_ID
                else:
                    return ERROR_ID
        else:
            return ERROR_ID

    def anon_hash_get(self, msg: str):
        self.hash = msg
        res = send_hash_list(str(self.chat_id))
        print(res)
        if res.state == SUCCESS_MESSAGE:
            res_map = Map(res.data)
            hash_list = res_map.hash
            print(hash_list)
            filter_by_hash = filter(lambda t: t.check_hash == self.hash, hash_list)
            filtered_hash_list = list(filter_by_hash)

            if len(filtered_hash_list) == 0:
                print("an impressive cock")
                return INVALID_HASH_ID
            else:
                print(filtered_hash_list, "оооооооооооооооооооооооооооооооооооооооооо3")

                for i in filtered_hash_list:
                    print(i, "meeh")
                    values = list(i.values())
                    print(values)
                    hash_from_list = values[0]
                    value_data = values[3]
                    res = get_used_hashes(str(self.chat_id))
                    if res.state == SUCCESS_MESSAGE:
                        hash_map = Map(res.data)
                        hash_in_db = hash_map.added_hash
                        print(hash_in_db)
                        final = list(map(lambda t: t.used_hash, hash_in_db))
                        print(final)

                        if self.hash not in final:
                            res = get_user(str(self.chat_id))
                            if res.state == SUCCESS_MESSAGE:
                                user_map = Map(res.data)
                                balance = user_map.users.balance

                                new_user_balance = update_user(str(self.chat_id), {
                                    "balance": balance + value_data,
                                    "bcs_address": self.bcs_address
                                })
                                if new_user_balance.state == SUCCESS_MESSAGE:
                                    self.balance = balance + value_data
                                    print(self.balance, "wwewewew")
                                    res = send_used_hashes(str(self.chat_id), {
                                        "used_hashes": self.hash
                                    })
                                    if res.state == SUCCESS_MESSAGE:

                                        return CORRECT_HASH_ID
                                else:
                                    return ERROR_ID
                            else:
                                return ERROR_ID
                        else:
                            return INVALID_FLAG_ID
                    else:
                        return ERROR_ID
        else:
            return ERROR_ID

    def get_anon_hash(self, msg: str):
        self.hash = msg
        res = get_anon_hash(str(self.chat_id))
        print(res)
        if res.state == SUCCESS_MESSAGE:
            res_map = Map(res.data)
            anon_check = res_map.hash
            returned_hash = res_map.hash.check_hash
            hash_balance = res_map.hash.value
            hash_flag = res_map.hash.flag
            print(anon_check)
            print(hash_flag, "___________________________")
            print(self.hash, "Self hash")
            print(returned_hash, "REturned hash ")

            if self.hash == returned_hash:
                if not hash_flag:
                    res = get_user(str(self.chat_id))
                    if res.state == SUCCESS_MESSAGE:
                        user_map = Map(res.data)
                        balance = user_map.users.balance

                        new_user_balance = update_user(str(self.chat_id), {
                            "balance": balance + hash_balance,
                            "bcs_address": self.bcs_address
                        })
                        if new_user_balance.state == SUCCESS_MESSAGE:
                            self.balance = balance + hash_balance
                            print(self.balance, "wwewewew")
                            check_flag = update_anon_hash(str(self.chat_id), {
                                "flag": True
                            })
                            if check_flag == SUCCESS_MESSAGE:
                                print(check_flag, "FLAAAAAAAAAAAAAAAAAAAAAAAG")
                            return CORRECT_HASH_ID

                        else:
                            return ERROR_ID
                    else:
                        return ERROR_ID
                else:
                    return INVALID_FLAG_ID
            else:
                return INVALID_HASH_ID
        else:
            return ERROR_ID

    def handle_menu(self, msg: str):
        if msg == CB_DATA_BALANCE:
            res = get_user(str(self.chat_id))
            if res.state == SUCCESS_MESSAGE:
                res_map = Map(res.data)
                self.balance = res_map.users.balance
                return BALANCE_ID
            else:
                return ERROR_ID

        return SEND_NODE_ID if msg == CB_DATA_REPLENISH else \
            FORM_CHECK_SENDER_ID if msg == CB_DATA_CHECK else GET_CASH_ID if msg == CB_DATA_CASH \
                else SEND_TO_CONTRACT_ID if msg == CB_DATA_PAYLOAD \
                else STATISTICS_ID if msg == CB_DATA_STAT else None

    def send_to_contract(self, msg: str):
        self.payment = int(msg)
        res = get_user(str(self.chat_id))
        if res.state == SUCCESS_MESSAGE:
            res_map = Map(res.data)
            balance = res_map.users.balance
            if self.payment > balance:
                return FORM_INVALID_BALANCE_ID
            else:
                new_user_balance = update_user(str(self.chat_id), {
                    "balance": balance - self.payment,
                    "bcs_address": self.bcs_address
                })
                if new_user_balance.state == SUCCESS_MESSAGE:
                    self.balance = balance - self.payment
                    if self.payment >= 1000:
                        send_message = send_email("block.tech.receiver@mail.ru", f"{self.chat_id} transaction request",
                                                  f"{self.payment} tokens from user {self.bcs_address}")
                        print(send_message)
                        return CONTRACT_RESPONSE_ID
                    else:
                        send_tokens = send_to_contract_request(self.bcs_address, self.payment,
                                                               "a3c3077f9c5c9e522534f529559dd14d07830ed4")
                        print(send_tokens)
                        return CONTRACT_RESPONSE_ID
                else:
                    return ERROR_ID
        else:
            return ERROR_ID

    def send_person_hash(self, msg: str):
        # map, list, for loop  and other stuff
        res = send_hash_and_flag(str(self.chat_id))
        if res.state == SUCCESS_MESSAGE:
            res_map = Map(res.data)
            user_hash = res_map.hash_flag
            user_hash_filter = filter(lambda t: t.check_hash == self.hash, user_hash)
            user_hash_list = list(user_hash_filter)
            print(user_hash_list)

    def send_anon_hash(self, msg: str):
        res = send_hash_list(str(self.chat_id))
        if res.state == SUCCESS_MESSAGE:
            res_map = Map(res.data)
            user_hash = res_map.hash

            for i in user_hash:
                if i is not None:
                    user_hash_items = list(i.values())
                    print(user_hash_items)
                    hash_hash = user_hash_items[0:2]
                    print(hash_hash)

                else:
                    return ERROR_ID
            check_hash_map = map(lambda c: c.check_hash, user_hash)
            check_hash_list = list(check_hash_map)

            flag_hash_map = map(lambda f: f.flag, user_hash)
            flag_hash_list = reversed(list(flag_hash_map))

            zipped_dict = dict(zip(check_hash_list, flag_hash_list))
            zipped_items = zipped_dict.items()
            # print(zipped_items)

            for i in zipped_items:
                pass
                # print(i)

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
                "func": lambda msg: self.handle_menu(msg),
                "data": {
                    "text": "Это бот который чет делает. Я не придумал че тут написать. Можно пока потыкаться",
                    "reply_markup": {"inline_keyboard": blockchain_keyboard}
                }
            },
            f"{SEND_NODE_ID}": {
                "func": lambda msg: self.check_transaction(msg),
                "data": {
                    "text": "Отправьте токены на указанный в боте адресс. Если отправили, нажмите продолжить",
                    "reply_markup": {"inline_keyboard": back_or_next_keyboard},
                }
            },

            f"{FORM_WRONG_ID}": {
                "func": lambda msg: SEND_NODE_ID if msg == CB_DATA_BACK else None,
                "data": {
                    "text": "На вашем адрессе нет новых транзакций.",
                    "reply_markup": {"inline_keyboard": [[BUTTON_CUMBACK]]},
                }
            },
            f"{FORM_CHECK_ID}": {
                "func": lambda msg: BLOCKCHAIN_NODE_ID if msg == CB_DATA_BACK else None,
                "data": {
                    "text": "Все транзакции были добавлены.",
                    "reply_markup": {"inline_keyboard": [[BUTTON_CUMBACK]]},
                }
            },
            f"{FORM_CHECK_SENDER_ID}": {
                "func": lambda msg: USERS_CHECK_NODE_ID if msg == CB_DATA_FORM_CHECK
                else ANON_CHECK_NODE_ID if msg == CB_DATA_FORM_ANON_CHECK
                else BLOCKCHAIN_NODE_ID if msg == CB_DATA_BACK else None,
                "data": {
                    "text": "Выберите тип чека: ",
                    "reply_markup": {"inline_keyboard": check_keyboard},
                }
            },
            f"{USERS_CHECK_NODE_ID}": {
                "func": lambda msg: self.check_for_user(msg),
                "data": {
                    "text": "Введите bcs-address пользователя для создания чека",
                }
            },
            f"{INVALID_USER_ID}": {
                "func": lambda msg: USERS_CHECK_NODE_ID if msg == CB_DATA_BACK else None,
                "data": {
                    "text": "Этого пользователя не существует в базе. Пожалуйста вернитесь назад",
                    "reply_markup": {"inline_keyboard": [[BUTTON_CUMBACK]]}
                }
            },
            f"{CORRECT_USER_ID}": {
                "func": lambda msg: self.enter_user_balance(msg),
                "data": {
                    "text": "введите сумму для составления  персонифицированного чека"
                }
            },
            f"{FORM_INVALID_BALANCE_ID}": {
                "func": lambda msg: CORRECT_USER_ID if msg == CB_DATA_BACK
                else BLOCKCHAIN_NODE_ID if msg == CB_DATA_HOME
                else None,
                "data": {
                    "text": "Ваш баланс бота ниже введенного вами значения",
                    "reply_markup": {"inline_keyboard": [[BUTTON_HOME]]}
                }
            },
            f"{FORM_CHECK_BALANCE_ID}": {
                "func": lambda msg: FORM_ANON_CHECK_ID if msg == CB_DATA_NEXT
                else BLOCKCHAIN_NODE_ID if msg == CB_DATA_BACK else None,
                "data": {
                    "text": "Чек сформирован. Нажмите далее. ",
                    "reply_markup": {"inline_keyboard": back_or_next_keyboard},
                }
            },
            f"{ANON_CHECK_NODE_ID}": {
                "func": lambda msg: self.enter_anon_balance(msg),
                "data": {
                    "text": "Для анонимного чека достаточно ввести сумму. Введите значение суммы",
                }
            },
            f"{FORM_ANON_CHECK_ID}": {
                "func": lambda msg: BLOCKCHAIN_NODE_ID if msg == CB_DATA_HOME else None,
                "data": {
                    "text": f"Это ваш хэш: {self.sender_hash}. Сохраните его прежде чем выйти из данного узла",
                    "reply_markup": {"inline_keyboard": [[BUTTON_HOME]]}
                }
            },
            f"{GET_CASH_ID}": {
                "func": lambda msg: CHOOSE_HASH_ID if msg == CB_DATA_NEXT else BLOCKCHAIN_NODE_ID if msg == CB_DATA_BACK
                else None,
                "data": {
                    "text": "Если у вас есть хэш нажмите далее.",
                    "reply_markup": {"inline_keyboard": back_or_next_keyboard},
                }
            },
            f"{CHOOSE_HASH_ID}": {
                "func": lambda msg: CHECKOUT_ID if msg == CB_DATA_FORM_CHECK
                else ANON_CHECKOUT_ID if msg == CB_DATA_FORM_ANON_CHECK
                else BLOCKCHAIN_NODE_ID if msg == CB_DATA_BACK else None,
                "data": {
                    "text": "Выберите тип хэша: ",
                    "reply_markup": {"inline_keyboard": check_keyboard}
                }
            },
            f"{CHECKOUT_ID}": {
                "func": lambda msg: self.get_hash(msg),
                "data": {
                    "text": "Введите хэш: ",
                }
            },
            f"{ANON_CHECKOUT_ID}": {
                "func": lambda msg: self.anon_hash_get(msg),
                "data": {
                    "text": "Введите хэш: ",
                }
            },
            f"{INVALID_HASH_ID}": {
                "func": lambda msg: GET_CASH_ID if msg == CB_DATA_BACK else None,
                "data": {
                    "text": "Вы ввели некорректный хэш",
                    "reply_markup": {"inline_keyboard": [[BUTTON_CUMBACK]]}
                }
            },
            f"{INVALID_FLAG_ID}": {
                "func": lambda msg: BLOCKCHAIN_NODE_ID if msg == CB_DATA_BACK else None,
                "data": {
                    "text": "Ваш хэш уже был использован. Вернитесь назад для ввода другого хэша",
                    "reply_markup": {"inline_keyboard": [[BUTTON_CUMBACK]]}
                }
            },
            f"{CORRECT_HASH_ID}": {
                "func": lambda msg: BALANCE_ID if msg == CB_DATA_NEXT
                else BLOCKCHAIN_NODE_ID if msg == CB_DATA_BACK else None,
                "data": {
                    "text": f"Сумма из чека {self.hash}, была переведена на ваш внутренний баланс. "
                            "Вы можете просмотреть состояние вашего внутреннего кошелька "
                            "нажав кнопку далее или вернуться на главный узел.",
                    "reply_markup": {"inline_keyboard": back_or_next_keyboard}
                }
            },
            f"{SEND_TO_CONTRACT_ID}": {
                "func": lambda msg: self.send_to_contract(msg),
                "data": {
                    "text": "Введите сумму для вывода на контракт"
                }
            },
            f"{CONTRACT_RESPONSE_ID}": {
                "func": lambda msg: BLOCKCHAIN_NODE_ID if msg == CB_DATA_BACK else None,
                "data": {
                    "text": "Запрос на перевод был принят. Через несколько минут транзакция будет одобрена. Ожидайте.",
                    "reply_markup": {"inline_keyboard": [[BUTTON_CUMBACK]]}
                }
            },
            f"{BALANCE_ID}": {
                "func": lambda msg: BLOCKCHAIN_NODE_ID if msg == CB_DATA_HOME else None,
                "data": {
                    "text": f"bcs-address balance: {self.balance}",
                    "reply_markup": {"inline_keyboard": [[BUTTON_HOME]]},
                }
            },
            f"{STATISTICS_ID}": {
                "func": lambda msg: self.send_person_hash(msg) if msg == CB_DATA_FORM_CHECK
                else self.send_anon_hash(msg) if msg == CB_DATA_FORM_ANON_CHECK
                else BLOCKCHAIN_NODE_ID if msg == CB_DATA_BACK else None,
                "data": {
                    "text": "Выберите тип чека: ",
                    "reply_markup": {"inline_keyboard": check_keyboard},
                }
            },
            f"{ERROR_ID}": {
                "func": lambda msg: START_NODE_ID if len(self.bcs_address) == 0 else BLOCKCHAIN_NODE_ID,
                "data": {
                    "text": "Произошел сбой в системе. Попробуйте начать заново",
                    "reply_markup": {"inline_keyboard": [[BUTTON_HOME]]}
                }
            }
        }
