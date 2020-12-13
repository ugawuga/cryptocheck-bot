from global_config import BCS_API_URL, DB_API_URL, DB_API_PORT
from api.rest import Rest

BASE_API_URL = DB_API_URL + ":" + DB_API_PORT


def get_transactions(address: str, contract: str):
    return Rest.get(BCS_API_URL + '/address/' + address + '/contract-txs/' + contract)


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




