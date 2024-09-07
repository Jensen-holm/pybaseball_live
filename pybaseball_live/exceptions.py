__all__ = ["BadResponseCode", "BadResponseData"]


class BadResponseCode(Exception):
    MSG = "response status code != 200 in get request to '{url}': {status_code}"

    def __init__(self, url: str, bad_code: int) -> None:
        super().__init__(self.MSG.format(url=url, status_code=bad_code))


class BadResponseData(Exception):
    MSG = "response data json does not contain '{key}' in get request to '{url}'"

    def __init__(self, url: str, key: str) -> None:
        super().__init__(self.MSG.format(url=url, key=key))
