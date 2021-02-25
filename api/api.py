from global_config import BCS_API_URL, DB_API_URL, DB_API_PORT
from api.rest import Rest

BASE_API_URL = DB_API_URL + ":" + DB_API_PORT

"""for api"""
def get_transactions(address: str, contract: str):
    return Rest.get(BCS_API_URL + '/address/' + address + '/contract-txs/' + contract)


def get_api_balance(address: str, contract: str):
    return Rest.get(BCS_API_URL + '/address/' + address + '/contract-txs/' + contract)


"""for personified hash"""
def form_user_hash(chat_id: str, data: object):
    return Rest.post(BASE_API_URL + '/user/formhash/' + chat_id, data)


def get_user_hash(chat_id: str):
    return Rest.get(BASE_API_URL + '/user/hash/' + chat_id)


def get_all_hash(chat_id: str):
    return Rest.get(BASE_API_URL + "/user/get/phash/" + chat_id)


"""for users in tabtables"""
def get_users():
    return Rest.get(BASE_API_URL + '/users')


def get_user(chat_id: str):
    print(BASE_API_URL + '/user/' + chat_id)
    return Rest.get(BASE_API_URL + '/user/' + chat_id)


def create_user(chat_id: str, data: object):
    print(BASE_API_URL + '/user/' + chat_id, data)
    return Rest.post(BASE_API_URL + '/user/' + chat_id, data)


def update_user(chat_id: str, data: object):
    return Rest.put(BASE_API_URL + '/user/' + chat_id, data)


"""for transaction id"""
def get_user_transaction(chat_id: str):
    return Rest.get(BASE_API_URL + '/user/transaction/' + chat_id)


def add_user_transaction(chat_id: str, data: object):
    return Rest.post(BASE_API_URL + '/user/transaction/' + chat_id, data)


def update_user_transaction(chat_id: str, data: object):
    return Rest.put(BASE_API_URL + '/user/transaction/' + chat_id, data)


def delete_user_transaction(chat_id: str):
    return Rest.delete(BASE_API_URL + "/user/transaction/" + chat_id)


"""for address checking"""
def check_address_exists(address: str):
    return Rest.get(BASE_API_URL + "/address/" + address)


"""for anon hash"""
def get_anon_hash(chat_id: str):
    return Rest.get(BASE_API_URL + "/user/get/anonhash/" + chat_id)


def add_anon_hash(chat_id: str, data: object):
    return Rest.post(BASE_API_URL + "/user/form/anonhash/" + chat_id, data)


def send_hash_list(chat_id: str):
    return Rest.get(BASE_API_URL + "/user/get/hashlist/" + chat_id)


"""for private used hashes"""
def get_used_private(chat_id: str):
    return Rest.get(BASE_API_URL + "/user/used/hash/" + chat_id)


def send_used_private(chat_id: str, data: object):
    return Rest.post(BASE_API_URL + "/user/add/hash/" + chat_id, data)


"""for person used hashes"""
def get_person_hash(chat_id: str):
    return Rest.get(BASE_API_URL + "/user/used/person/" + chat_id)


def put_person_hash(chat_id: str, data: object):
    return Rest.post(BASE_API_URL + "/user/add/person/" + chat_id, data)


"""for contract address"""
def get_address_contract():
    return Rest.get(BASE_API_URL + '/user/address/')
