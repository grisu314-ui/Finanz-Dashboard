import socket

import pytest


def test_create_connection_is_blocked():
    with pytest.raises(RuntimeError, match="Network access"):
        socket.create_connection(("example.org", 443), timeout=1)


def test_socket_connect_is_blocked():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        with pytest.raises(RuntimeError, match="Network access"):
            sock.connect(("127.0.0.1", 9))
