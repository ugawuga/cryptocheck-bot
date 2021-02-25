import re
import requests
from requests import Response
from telegram.bcrypt import form_hash_key
from telegram.send_email import send_email
from telegram.send_tokens import send_to_contract_request
from utils.fapper import Map
from utils.is_unique import is_unique
from api.api import get_transactions, get_user, create_user, form_user_hash, get_user_hash, \
    update_user, check_address_exists, get_anon_hash, add_anon_hash, \
    get_user_transaction, add_user_transaction, send_hash_list, get_used_private, send_used_private, \
    get_all_hash, put_person_hash, get_person_hash, get_address_contract
from api.rest import SUCCESS_MESSAGE
from telegram.keyboard import back_or_next_keyboard, yes_or_no_keyboard, blockchain_keyboard, check_keyboard, \
    choice_keyboard, \
    CB_DATA_NEXT, \
    CB_DATA_NO, CB_DATA_BACK, CB_DATA_YES, CB_DATA_HOME, BUTTON_YES, BUTTON_CUMBACK, BUTTON_HOME, CB_DATA_CASH, \
    CB_DATA_CHECK, CB_DATA_REPLENISH, \
    CB_DATA_FORM_CHECK, CB_DATA_FORM_ANON_CHECK, CB_DATA_BALANCE, CB_DATA_PAYLOAD, CB_DATA_STAT, CB_DATA_ACTIVATED, \
    CB_DATA_NON_ACTIVATED, BUTTON_NEXT

NEWLINE = '\n'
START_NODE_ID = "start_id"
CONTRACT_ID = "contract_id"
WRONG_CONTRACT_ID = "wrong_contract_id"
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
EMPTY_HASH_LIST = "empty_id"
EMPTY_ACTIVE_HASH = "none_active_id"
ACTIVATED_HASH_ID = "activated_id"
NON_ACTIVATED_HASH_ID = "non_activated_id"
HASH_CHOOSE_ID = "hash_choose_id"
EMPTY_NON_ACTIVE_HASH = "empty_non_active_id"
ANON_HASH_CHOOSE_ID = "anon_id"
OTHER_PAGE_ID = "other_page_id"
ACTIVATED_PRIVATE_HASH_ID = "activated_private_id"
NON_ACTIVATED_PRIVATE_HASH_ID = "non_activated_private_id"
ANOTHER_PAGE_ID = "another_page_id"


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
        self.address_contract = ""
        self.payment = 0
        self.activated = []
        self.non_activated = []
        self.p_activated = []
        self.non_p_activated = []
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

    def get_address_contract(self, msg:str):
        self.address_contract = msg
        res = get_address_contract()
        if res.state == SUCCESS_MESSAGE:
            res_map = Map(res.data)
            addreses = res_map.address
            relate = list(filter(lambda t: t.address_contract == self.address_contract, addreses))
            if len(relate) == 0:
                return WRONG_CONTRACT_ID
            else:
                return ADDRESS_NODE_ID
        else:
            return ERROR_ID

    def get_bcs_address(self, msg: str):

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
        global balance_sum
        if msg == CB_DATA_BACK:
            return BLOCKCHAIN_NODE_ID
        res = get_transactions(self.bcs_address, self.address_contract)
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
        else:
            return ERROR_ID

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

    def get_preson_hash(self, msg: str):
        self.hash = msg
        res = get_all_hash(str(self.chat_id))
        if res.state == SUCCESS_MESSAGE:
            res_map = Map(res.data)
            hash_list = res_map.hash
            print(hash_list)
            filter_by_hash = filter(lambda t: t.check_hash == self.hash, hash_list)
            filtered_hash_list = list(filter_by_hash)

            if len(filtered_hash_list) == 0:
                print("an impressive cock")
                return INVALID_HASH_ID

            for i in filtered_hash_list:
                print(i, "meeh")
                values = list(i.values())

                check_data = values[4]
                receiver_data = values[3]
                print(receiver_data)
                res = get_person_hash(str(self.chat_id))
                if res.state == SUCCESS_MESSAGE:
                    hash_map = Map(res.data)
                    hash_in_db = hash_map.added_hash
                    final = list(map(lambda t: t.used_hash, hash_in_db))
                    print(final)

                    if self.hash not in final:
                        if self.bcs_address == receiver_data:
                            res = get_user(str(self.chat_id))
                            if res.state == SUCCESS_MESSAGE:
                                user_map = Map(res.data)
                                balance = user_map.users.balance

                                new_user_balance = update_user(str(self.chat_id), {
                                    "balance": balance + check_data,
                                    "bcs_address": self.bcs_address
                                })
                                if new_user_balance.state == SUCCESS_MESSAGE:
                                    self.balance = balance + check_data
                                    res = put_person_hash(str(self.chat_id), {
                                        "used_hashes": self.hash
                                    })
                                    if res.state == SUCCESS_MESSAGE:
                                        return CORRECT_HASH_ID
                                else:
                                    return ERROR_ID
                            else:
                                return ERROR_ID
                        else:
                            return INVALID_USER_ID
                    else:
                        return INVALID_FLAG_ID
                else:
                    return ERROR_ID
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

                for i in filtered_hash_list:
                    print(i, "meeh")
                    values = list(i.values())
                    print(values)
                    value_data = values[3]
                    res = get_used_private(str(self.chat_id))
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
                                    res = send_used_private(str(self.chat_id), {
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
                        return ERROR_ID

                        # send_tokens = send_to_contract_request(self.bcs_address, self.payment,
                        #                                        self.address_contract)
                        # print(send_tokens)
                        # return CONTRACT_RESPONSE_ID
                else:
                    return ERROR_ID
        else:
            return ERROR_ID

    def send_person_ahash(self, msg: str):
        # map, list, for loop  and other stuff
        res = get_all_hash(str(self.chat_id))
        if res.state == SUCCESS_MESSAGE:
            res_map = Map(res.data)
            hash_list = res_map.hash
            map_by_hash = list(map(lambda t: t.check_hash, hash_list))
            print(map_by_hash, "HASH LIST")

            if len(map_by_hash) == 0:
                return EMPTY_HASH_LIST
            else:
                res = get_person_hash(str(self.chat_id))
                if res.state == SUCCESS_MESSAGE:
                    res_map = Map(res.data)
                    used_hash_list = res_map.added_hash
                    mapped_hash_list = list(map(lambda t: t.used_hash, used_hash_list))
                    print(mapped_hash_list, "MAPPED LIST")

                    person_active_list = []
                    for i in map_by_hash:
                        print(i, "i values")
                        if i in mapped_hash_list:
                            person_active_list.append(i)
                    self.activated = person_active_list
                    print(self.activated)

                    return ACTIVATED_HASH_ID
                else:
                    return ERROR_ID
        else:
            return ERROR_ID

    def send_person_nhash(self, msg: str):
        res = get_all_hash(str(self.chat_id))
        if res.state == SUCCESS_MESSAGE:
            res_map = Map(res.data)
            hash_list = res_map.hash
            map_by_hash = list(map(lambda t: t.check_hash, hash_list))
            print(map_by_hash, "HASH LIST")

            if len(map_by_hash) == 0:
                return EMPTY_HASH_LIST
            else:
                res = get_person_hash(str(self.chat_id))
                if res.state == SUCCESS_MESSAGE:
                    res_map = Map(res.data)
                    used_hash_list = res_map.added_hash
                    mapped_hash_list = list(map(lambda t: t.used_hash, used_hash_list))
                    print(mapped_hash_list, "MAP LIST")

                    use_list = []
                    for i in map_by_hash:
                        print(i, "person n i")
                        if i not in mapped_hash_list:
                            if i not in self.non_activated:
                                use_list.append(i)
                                self.non_activated = list(filter(lambda t: t not in self.activated, use_list))
                                print(self.non_activated)
                    return NON_ACTIVATED_HASH_ID
                else:
                    return ERROR_ID
        else:
            return ERROR_ID

    def send_anon_ahash(self, msg: str):
        res = send_hash_list(str(self.chat_id))
        if res.state == SUCCESS_MESSAGE:
            res_map = Map(res.data)
            hash_list = res_map.hash
            map_by_hash = list(map(lambda t: t.check_hash, hash_list))
            print(map_by_hash, "HASH LIST ANON")

            if len(map_by_hash) == 0:
                return EMPTY_HASH_LIST
            else:
                res = get_used_private(str(self.chat_id))
                if res.state == SUCCESS_MESSAGE:
                    res_map = Map(res.data)
                    used_hash_list = res_map.added_hash
                    mapped_hash_list = list(map(lambda t: t.used_hash, used_hash_list))
                    print(mapped_hash_list, "ALL HASH")

                    anon_used_list = []
                    for i in map_by_hash:
                        print(i, "i anon active")
                        if i in mapped_hash_list:
                            anon_used_list.append(i)
                            self.p_activated = anon_used_list
                            print(self.p_activated)

                    return ACTIVATED_PRIVATE_HASH_ID
                else:
                    return ERROR_ID
        else:
            return ERROR_ID

    def send_anon_nhash(self, msg: str):
        res = send_hash_list(str(self.chat_id))
        if res.state == SUCCESS_MESSAGE:
            res_map = Map(res.data)
            hash_list = res_map.hash
            map_by_hash = list(map(lambda t: t.check_hash, hash_list))
            print(map_by_hash, "SEND NHASH")

            if len(map_by_hash) == 0:
                return EMPTY_HASH_LIST
            else:
                res = get_used_private(str(self.chat_id))
                if res.state == SUCCESS_MESSAGE:
                    res_map = Map(res.data)
                    used_hash_list = res_map.added_hash
                    mapped_hash_list = list(map(lambda t: t.used_hash, used_hash_list))
                    print(mapped_hash_list, "ALL HASH")

                    used_list = []
                    for i in map_by_hash:
                        print(i, "values")
                        if i not in mapped_hash_list:
                            if i not in self.non_p_activated:
                                used_list.append(i)
                                self.non_p_activated = list(filter(lambda t: t not in self.p_activated, used_list))

                    return NON_ACTIVATED_PRIVATE_HASH_ID
                else:
                    return ERROR_ID
        else:
            return ERROR_ID

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
                "func": lambda msg: CONTRACT_ID if msg == CB_DATA_YES else REFUSE_ID if msg == CB_DATA_NO else None,
                "data": {
                    "text": "это тестовый бот BCS. Для начала работы необходимо привязать BCS адресс к боту \n"
                            "У вас есть bcs-address? ",
                    "reply_markup": {"inline_keyboard": yes_or_no_keyboard}
                }
            },
            f"{CONTRACT_ID}": {
               "func": lambda msg: self.get_address_contract(msg),
               "data": {
                    "text": "Введите адресс вашего контракта"
                }
            },
            f"{WRONG_CONTRACT_ID}" : {
                "func": lambda msg: CONTRACT_ID if msg == CB_DATA_BACK else None,
                "data": {
                    "text": "Вы ввели некорректный адресс контракта",
                    "reply_markup": {"inline_keyboard": [[BUTTON_CUMBACK]]}
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
                "func": lambda msg: BLOCKCHAIN_NODE_ID if msg == CB_DATA_BACK else None,
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
                "func": lambda msg: self.get_preson_hash(msg),
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
                "func": lambda msg: HASH_CHOOSE_ID if msg == CB_DATA_FORM_CHECK
                else ANON_HASH_CHOOSE_ID if msg == CB_DATA_FORM_ANON_CHECK
                else BLOCKCHAIN_NODE_ID if msg == CB_DATA_BACK else None,
                "data": {
                    "text": "Выберите тип чека: ",
                    "reply_markup": {"inline_keyboard": check_keyboard},
                }
            },
            f"{EMPTY_HASH_LIST}": {
                "func": lambda msg: STATISTICS_ID if msg == CB_DATA_BACK else None,
                "data": {
                    "text": "Вы пока не сформировали ни одного чека",
                    "reply_markup": {"inline_keyboard": [[BUTTON_CUMBACK]]}
                }
            },
            f"{EMPTY_ACTIVE_HASH}": {
                "func": lambda msg: STATISTICS_ID if msg == CB_DATA_BACK else None,
                "data": {
                    "text": "Вы пока не активировали ни одного чека",
                    "reply_markup": {"inline_keyboard": [[BUTTON_CUMBACK]]}
                }
            },
            f"{EMPTY_NON_ACTIVE_HASH}": {
                "func": lambda msg: STATISTICS_ID if msg == CB_DATA_BACK else None,
                "data": {
                    "text": "На вашем аккаунте нет неактивированных чеков",
                    "reply_markup": {"inline_keyboard": [[BUTTON_CUMBACK]]}
                }
            },
            f"{HASH_CHOOSE_ID}": {
                "func": lambda msg: self.send_person_ahash(msg) if msg == CB_DATA_ACTIVATED
                else self.send_person_nhash(msg) if msg == CB_DATA_NON_ACTIVATED
                else STATISTICS_ID if msg == CB_DATA_BACK else None,
                "data": {
                    "text": "Здесь можно посмотреть активированные и \n "
                            "неактивированные чеки персонифицированные чеки.",
                    "reply_markup": {"inline_keyboard": choice_keyboard},
                }
            },
            f"{ANON_HASH_CHOOSE_ID}": {
                "func": lambda msg: self.send_anon_ahash(msg) if msg == CB_DATA_ACTIVATED
                else self.send_anon_nhash(msg) if msg == CB_DATA_NON_ACTIVATED
                else STATISTICS_ID if msg == CB_DATA_BACK else BLOCKCHAIN_NODE_ID if msg == CB_DATA_HOME else None,
                "data": {
                    "text": "Здесь можно посмотреть активированные чеки и \n "
                            "неактивированные чеки приватные чеки.",
                    "reply_markup": {"inline_keyboard": choice_keyboard}
                }
            },
            f"{ACTIVATED_HASH_ID}": {
                "func": lambda msg: STATISTICS_ID if msg == CB_DATA_BACK
                else OTHER_PAGE_ID if msg == CB_DATA_NEXT else None,
                "data": {
                    "text": f"Использованные чеки: \n"
                            f"{NEWLINE.join(self.activated[0:10])} \n "
                            f"Отображаются первые 10 чеков",
                    "reply_markup": {"inline_keyboard": [[BUTTON_CUMBACK], [BUTTON_NEXT]]},
                }
            },
            f"{OTHER_PAGE_ID}": {
                "func": lambda msg: ACTIVATED_HASH_ID if msg == CB_DATA_BACK else None,
                "data": {
                    "text": f"Использованные чеки: \n"
                            f"{NEWLINE.join(self.activated[10:-1])} \n"
                            f"Отображаются оставшиеся чеки",
                    "reply_markup": {"inline_keyboard": [BUTTON_CUMBACK]}
                }
            },
            f"{NON_ACTIVATED_HASH_ID}": {
                "func": lambda msg: STATISTICS_ID if msg == CB_DATA_BACK else None,
                "data": {
                    "text": f"Неиспользованные чеки: \n"
                            f"{NEWLINE.join(self.non_activated)} \n"
                            f"Если видите здесь чек, который был использован, просто создайте новый чек "
                            f"или перезайдите на свой аккаунт",
                    "reply_markup": {"inline_keyboard": [[BUTTON_CUMBACK]]},
                }
            },
            f"{ACTIVATED_PRIVATE_HASH_ID}": {
                "func": lambda msg: STATISTICS_ID if msg == CB_DATA_BACK
                else OTHER_PAGE_ID if msg == CB_DATA_NEXT else None,
                "data": {
                    "text": f"Использованные чеки: \n"
                            f"{NEWLINE.join(self.p_activated[0:10])} \n "
                            f"Отображаются первые 10 чеков",
                    "reply_markup": {"inline_keyboard": [[BUTTON_CUMBACK], [BUTTON_NEXT]]},
                }
            },
            f"{NON_ACTIVATED_PRIVATE_HASH_ID}": {
                "func": lambda msg: STATISTICS_ID if msg == CB_DATA_BACK else None,
                "data": {
                    "text": f"Неиспользованные чеки: \n"
                            f"{NEWLINE.join(self.non_p_activated)} \n"
                            f"Если видите здесь чек, который был использован, просто создайте новый чек "
                            f"или перезайдите на свой аккаунт",
                    "reply_markup": {"inline_keyboard": [[BUTTON_CUMBACK]]},
                }
            },
            f"{ANOTHER_PAGE_ID}": {
                "func": lambda msg: ACTIVATED_HASH_ID if msg == CB_DATA_BACK else None,
                "data": {
                    "text": f"Использованные чеки: \n"
                            f"{NEWLINE.join(self.p_activated[10:-1])} \n"
                            f"Отображаются оставшиеся чеки ",
                    "reply_markup": {"inline_keyboard": [BUTTON_CUMBACK]}
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
