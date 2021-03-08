import base64
# pip3 install pycryptodome
from Crypto.Cipher import AES


class AESCipher:
    """
    AES加密、解密工具类
    """
    def __init__(self, key, iv=b'0000000000000000'):
        self.key = self._pad_key(key)
        self.iv = iv

    @staticmethod
    def _pad_key(key, num=16):
        if len(key) > 16:
            raise Exception(f"length of key > {num}")
        amount_to_pad = num-len(key)
        pad = chr(amount_to_pad)
        return str.encode(key + pad * amount_to_pad)

    def encrypt(self, raw):
        """
        加密方法
        :param raw: 需要加密的密文 str
        :return: base64编码的密文 str
        """
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        return base64.b64encode(cipher.encrypt(self._pad(raw).encode())).decode()

    def decrypt(self, enc):
        """
        解密方法
        :param enc: base64编码的密文 str
        :return: 解密后的明文 str
        """
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        return self._unpad(cipher.decrypt(base64.b64decode(enc)).decode())

    @staticmethod
    def _pad(text):
        # 填充方法，加密内容必须为16字节的倍数
        text_length = len(text)
        amount_to_pad = AES.block_size - (text_length % AES.block_size)
        if amount_to_pad == 0:
            amount_to_pad = AES.block_size
        pad = chr(amount_to_pad)
        return text + pad * amount_to_pad

    @staticmethod
    def _unpad(text):
        # 截取填充的字符
        pad = ord(text[-1])
        return text[:-pad]


if __name__ == '__main__':
    c = AESCipher("keyskey")
    import sys
    encrypt = c.encrypt(sys.argv[1])
    print('加密后:\n%s' % encrypt)
    decrypt = c.decrypt(encrypt)
    print('解密后:\n%s' % decrypt)
