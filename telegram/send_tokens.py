import json
import requests
from telegram import bcs_config


def jsonrpc_request(method, params):
    """
    Отправляет запрос и возвращает ответ от json rpc из демона
    """

    payload = json.dumps({"method": method, "params": params})
    headers = {"content-type": "application/json", "cache-control": "no-cache"}

    response = requests.request(
        "POST",
        bcs_config.NODE_URL,
        data=payload,
        headers=headers,
        auth=(bcs_config.NODE_USER, bcs_config.NODE_PASSWORD),
    )
    return json.loads(response.text)


def get_hex_address_request(address):
    """
    Возвращает кошелёк в хексе из ответа jsonrpc
    """

    hexaddress = jsonrpc_request("gethexaddress", [address])

    return str(hexaddress["result"])


def repeat_to_length(stirng, wanted):
    """
    Вспомогательная функция для заполнения строки нулями до определённого размера
    """

    return (stirng * (wanted // len(stirng) + 1))[:wanted]


def send_to_contract_request(address, amount, contract_address):
    """
    Отправляет токены в смарт-котракт
    """

    contract_amount = 0
    gas_limit = 250000
    gas_price = 0.0000001
    sender_address = 'BNm5NQUekm9ty2SxB2Kj5HiSKVxhKYLsrE'  # default addres to send tokens from

    hex_amount = format(amount, "x")
    datahex = (
            "a9059cbb"
            + "000000000000000000000000"
            + get_hex_address_request(address)
            + repeat_to_length("0", 64 - len(hex_amount))
            + hex_amount
    )
    res = jsonrpc_request(
        "sendtocontract",
        [
            str(contract_address),
            datahex,
            contract_amount,  # ignore
            gas_limit,  # ignore
            gas_price,  # ignore
            sender_address,
        ],
    )

    return res["result"]["txid"]


# js = jsonrpc_request(method="POST", params=[bcs_config.NODE_USER, bcs_config.NODE_URL, bcs_config.NODE_PASSWORD])
# print(js)
