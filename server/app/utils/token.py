from __future__ import annotations

import base64
import secrets
import string
import time

import itsdangerous


class Tokens:
    def __init__(self, epoch: int, secret: str, link_length: int):
        self.epoch = epoch
        self.secret = secret
        self.link_length = link_length

        self.signer = itsdangerous.TimestampSigner(secret)
        self.incrementor: int = 0

    def create_id(self) -> str:
        self.incrementor += 1
        now = int(time.time() * 1000 - self.epoch)

        snowflake = now << 22
        snowflake |= self.incrementor

        return str(snowflake)

    def create_token(self, id: str) -> str:
        b64_token = base64.b64encode(id.encode())
        token = self.signer.sign(b64_token)
        return token.decode()

    def validate_token(self, token: str, *, max_age: int | None = None) -> str:
        encoded_token = token.encode()
        result = self.signer.unsign(encoded_token, max_age=max_age)

        if isinstance(result, tuple):
            id = bytes(result[0])
        else:
            id = result

        return base64.b64decode(id.decode()).decode()

    AVAILABLE_CHARS: str = string.ascii_letters + string.digits

    def create_link_id(self) -> str:
        return ''.join(secrets.choice(self.AVAILABLE_CHARS) for i in range(self.link_length))
