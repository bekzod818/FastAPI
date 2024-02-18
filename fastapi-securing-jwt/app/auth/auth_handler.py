import time

from decouple import config

import jwt

"""
Next, create an environment file called .env in the base directory:

secret=please_please_update_me_please
algorithm=HS256
"""

JWT_SECRET = config("secret")
JWT_ALGORITHM = config("algorithm")


def token_response(token: str):
    return {"access_token": token}


def signJWT(user_id: str) -> dict[str, str]:
    payload = {
        "user_id": user_id,
        "expires": time.time() + 600,  # 10 minutes = 600 seconds
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token_response(token)


def decodeJWT(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except Exception as error:
        print("Decode JWT:", error)
        return {}
