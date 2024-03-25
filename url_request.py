import random
import sys
import requests
from requests.exceptions import ConnectionError, ProxyError
import time
from fp.fp import FreeProxy
from fp.errors import FreeProxyException

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/92.0.902.62',
]


def get_proxy_with_retry():
    proxy = None
    while not proxy:
        try:
            proxy = {
                'http': f'{FreeProxy().get()}',
                'https': f'{FreeProxy(https=True).get()}'
            }
        except FreeProxyException:
            continue
    return proxy


def make_request(url, retry_limit=3, debug=False, activate_proxy=True):
    if debug:
        raise Exception(f"This is a debug exception")

    # Headers to mimic a browser request
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Cache-Control': 'no-cache',
    }

    for i in range(retry_limit):
        if activate_proxy:
            proxy = get_proxy_with_retry()
        else:
            proxy = None
        x = i + 1
        try:
            # Make the request using a proxy
            if proxy:
                response = requests.get(url, headers=headers, proxies=proxy)
            else:
                response = requests.get(url, headers=headers)
            response.raise_for_status()  #Raise an exception for 4xx and 5xx status codes
            return response
        except ProxyError as e:
            print(f"Failed to get {url}: {e}, wait: {10*x}")
            time.sleep(10 * x)
        except ConnectionError as e:
            print(f"Failed to get {url}: {e}, wait: {60*x}")
            time.sleep(60 * x)
        except Exception as e:
            print(f"Failed to get {url}: {e}, wait: {10*x}")
            time.sleep(10*x)
    raise Exception(f"Unable to get {url} after retries")


def make_multiple_request(url_list):
    proxy = get_proxy_with_retry()
    i = 0
    response_list = []

    while i < len(url_list):
        # Headers to mimic a browser request
        headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Cache-Control': 'no-cache',
        }
        try:
            response = requests.get(url_list[i], headers=headers, proxies=proxy)
            response.raise_for_status()
            response_list += response
            i += 1
        except Exception as e:
            print(f"Failed to get {url_list[i]}: {e}, changing proxy")
            proxy = get_proxy_with_retry()
    return response_list
