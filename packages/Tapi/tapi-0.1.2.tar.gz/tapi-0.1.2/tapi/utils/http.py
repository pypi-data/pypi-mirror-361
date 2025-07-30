import urllib3
from tapi.client import Client


def disable_ssl_verification(supress_warnings: bool = True) -> None:
    Client.verify_ssl = False
    if supress_warnings:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
