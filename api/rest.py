import requests

SUCCESS_MESSAGE = 'success'
FAILED_MESSAGE = 'failed'


class Response:
    def __init__(self, state: str, data=None):
        self.state = state
        self.data = data


class Rest:
    @staticmethod
    def get(url) -> Response:
        try:
            res = requests.get(url)
            return Response(SUCCESS_MESSAGE, res.json()) if res.status_code == 200 else Response(FAILED_MESSAGE)
        except Exception:
            return Response(FAILED_MESSAGE)

    @staticmethod
    def post(url, data) -> Response:

        try:
            res = requests.post(url, json=data)
            print(res.status_code, "_______________________________________________________________")
            return Response(SUCCESS_MESSAGE, res.json()) if res.status_code == 200 else Response(FAILED_MESSAGE)
        except Exception as e:
            print(e)
            return Response(FAILED_MESSAGE)

    @staticmethod
    def put(url, data) -> Response:
        try:
            res = requests.put(url, json=data)
            return Response(SUCCESS_MESSAGE, res.json()) if res.status_code == 200 else Response(FAILED_MESSAGE)
        except Exception:
            return Response(FAILED_MESSAGE)

    @staticmethod
    def delete(url) -> Response:
        try:
            res = requests.delete(url)
            return Response(SUCCESS_MESSAGE, res.json()) if res.status_code == 200 else Response(FAILED_MESSAGE)
        except Exception:
            return Response(FAILED_MESSAGE)
