from stem import Signal
from stem.control import Controller
from src.conf import torControlPassword


def change_ip():
    """Change IP using TOR"""
    try:
        with Controller.from_port(port=9051) as controller:
            controller.authenticate(password=torControlPassword)
            controller.signal(Signal.NEWNYM)
    except Exception:
        pass