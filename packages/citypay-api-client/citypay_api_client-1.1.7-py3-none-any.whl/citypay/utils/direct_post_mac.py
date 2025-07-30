# coding: utf-8
import hmac
import hashlib


def direct_post_create_mac(licence_key: str, nonce: bytes, amount: int, identifier: str):
    """
    @param licence_key: a licence key provided
    @param nonce: a random 16 byte value
    @param amount: transaction amount in the lowest currency unit
    @param identifier: the identifier value of the transaction
    @return: a hex encoded mac value
    """
    value = str()
    value += nonce.hex().upper()
    value += str(amount)
    value += identifier

    digest = hmac.new(bytes(licence_key, 'utf-8'),
                      msg=bytes(value, 'utf-8'),
                      digestmod=hashlib.sha256).hexdigest()
    return digest.upper()


def verify(licence_key: str, nonce: bytes, amount: int, identifier: str, mac: str):
    """
    @param licence_key: a licence key provided
    @param nonce: a random 16 byte value
    @param amount: transaction amount in the lowest currency unit
    @param identifier: the identifier value of the transaction
    @param: a hex encoded mac value
    @return: boolean
    """
    return mac == direct_post_create_mac(licence_key, nonce, amount, identifier)
