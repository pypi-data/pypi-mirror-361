from functools import wraps

import requests

from .lib import LOGGER


def handle_exception(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.HTTPError as e:
            LOGGER.error(f"请求失败，状态码: {e.response.status_code}")
            return None
        except requests.exceptions.Timeout as e:
            LOGGER.error(f"请求超时: {e}")
            return None
        except requests.exceptions.RequestException as e:
            LOGGER.error(f"发生错误: {e}")
            return None
        except Exception as e:
            LOGGER.error(f"发生错误: {e}")
            return None

    return wrapper


def __get_headers(token: str):
    return {
        "Access-Token": token,
    }


@handle_exception
def get_task_info(
    task_id: str, token: str, domain: str, session: requests.Session = None
):
    url = f"{domain}/api/v2/task/get/task-info"
    headers = __get_headers(token)
    params = {"taskId": task_id}
    response = (session or requests).post(url, headers=headers, params=params)
    response.raise_for_status()
    if response.status_code != 200:
        return None
    return response.json()


@handle_exception
def get_item_info(
    item_id: str, token: str, domain: str, session: requests.Session = None
):
    url = f"{domain}/api/v2/item/get-item-info"
    headers = __get_headers(token)
    params = {"itemId": item_id}
    response = (session or requests).post(url, headers=headers, params=params)
    response.raise_for_status()
    if response.status_code != 200:
        return None
    return response.json()


@handle_exception
def find_labels(
    task_id: str,
    item_id: str,
    token: str,
    domain: str,
    session: requests.Session = None,
):
    url = f"{domain}/api/v2/label/find-labels"
    headers = __get_headers(token)
    params = {"taskId": task_id, "itemId": item_id}
    response = (session or requests).post(url, headers=headers, params=params)
    response.raise_for_status()
    if response.status_code != 200:
        return None
    return response.json()
