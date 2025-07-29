import base64
import requests
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5


class Authorization:
    """
    获取 token
    pip install pycryptodome
    """
    def __init__(self, SERVER: str, USER: str, PASSWORD: str):
        self.SERVER = SERVER
        self.USER = USER
        self.PASSWORD = PASSWORD
        self.HEADERS = {"Cookie": f"token={self.get_token()}"}

    def _get_rsa_public_key(self) -> str:
        """
        获取 RSA 公钥
        :return: RSA 公钥
        """
        url = f"{self.SERVER}/gateway/get_rsa_public_key/direct"
        response = requests.get(url, verify=False)
        return f"""-----BEGIN PUBLIC KEY-----\n{response.text}\n-----END PUBLIC KEY-----"""

    def _encrypt_password(self) -> str:
        """
        RSA 加密密码
        :return: 加密后的密码
        """
        rsa_key = RSA.import_key(self._get_rsa_public_key())
        cipher = PKCS1_v1_5.new(rsa_key)
        encrypted = cipher.encrypt(self.PASSWORD.encode('utf-8'))
        return base64.b64encode(encrypted).decode('utf-8')

    def get_token(self) -> str:
        """
        获取 token
        :return: token
        """
        url = f"{self.SERVER}/usercenter/userAuth/oauth/token"
        headers = {
            "Authorization": "Basic cXo6c2hxejg4NjYu"
        }
        params = {
            "username": self.USER,
            "password": self._encrypt_password()
        }
        response = requests.post(url, headers=headers, params=params, verify=False)
        return response.json().get("body")