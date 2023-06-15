import typing as tp

import requests  # type: ignore
from requests.adapters import HTTPAdapter  # type: ignore
from requests.packages.urllib3.util.retry import Retry  # type: ignore


class Session:
    """
    Сессия.
    :param base_url: Базовый адрес, на который будут выполняться запросы.
    :param timeout: Максимальное время ожидания ответа от сервера.
    :param max_retries: Максимальное число повторных запросов.
    :param backoff_factor: Коэффициент экспоненциального нарастания задержки.
    """

    def __init__(
        self,
        base_url: str,
        timeout: float = 5.0,
        max_retries: int = 3,
        backoff_factor: float = 0.3,
    ) -> None:
        self.session = requests.Session()
        self.base_url = base_url
        self.timeout = timeout
        method_whitelist = ["GET", "POST"]
        self.retries = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            method_whitelist=method_whitelist,
            status_forcelist=[i for i in range(400, 601)],
        )
        self.adapter = HTTPAdapter(max_retries=self.retries)
        self.http = requests.Session()
        self.session.mount(base_url, self.adapter)

    def get(self, url: str, *args: tp.Any, **kwargs: tp.Any) -> requests.Response:
        kwargs["timeout"] = self.timeout if "timeout" not in kwargs else kwargs["timeout"]
        return self.session.get(self.base_url + url, *args, **kwargs)

    def post(self, url: str, *args: tp.Any, **kwargs: tp.Any) -> requests.Response:
        kwargs["timeout"] = self.timeout if "timeout" not in kwargs else kwargs["timeout"]
        return self.session.post(self.base_url + url, *args, **kwargs)
