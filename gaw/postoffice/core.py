import json
from Crypto.Cipher import AES
import random
from jwt.algorithms import HMACAlgorithm
from jwt.exceptions import DecodeError
from gaw.postoffice.exceptions import PostofficeException
import time
import base64

class ConnectionTerminated(Exception):
    def __init__(self): super(ConnectionTerminated, self).__init__('Connection Terminated')


def pad(b, block_size):
    """
    padding to blocksize according to PKCS #7
    """
    padsize = block_size - len(b) % block_size
    return b + padsize * bytes(bytearray([padsize])) # python 2 compatible

def unpad(b):
    """
    unpadding according to PKCS #7
    """
    i = bytearray([b[-1]])[0]  # python 2 compatible
    return b[:-i]

def get_random_bytes(length):
    ba = bytearray(length)
    for i in range(length):
        ba[i] = random.getrandbits(8)
    return bytes(ba)

def _sign(b, secret):
    alg = HMACAlgorithm(HMACAlgorithm.SHA256)
    key = alg.prepare_key(secret)
    signature = alg.sign(b, key)
    return signature

def _verify(b, secret, signature):
    alg = HMACAlgorithm(HMACAlgorithm.SHA256)
    key = alg.prepare_key(secret)
    if not alg.verify(b, key, signature):
        raise PostofficeException(name='DecodeError',
                                  message='signature verification failed')
    return True

def attach_signature(payload, secret):
    b_payload = payload.encode('utf-8')
    return _sign(b_payload, secret) + b_payload

def verify_signature(b, secret):
    signature, b_payload = b[:32], b[32:]
    _verify(b_payload, secret, signature)
    payload = b_payload.decode('utf-8')
    return payload

def encrypt_and_sign(payload, secret):
    '''
    vi (16), ciphertext (signature 32, payload)
    '''
    iv = get_random_bytes(16)
    cipher = AES.new(secret, AES.MODE_CBC, iv)
    signed_payload = attach_signature(payload, secret)
    ciphertext = cipher.encrypt(pad(signed_payload, 16))
    return iv + ciphertext

def decrypt_and_verify(b, secret):
    iv, ciphertext = b[:16], b[16:]
    cipher = AES.new(secret, AES.MODE_CBC, iv)
    signed_payload = unpad(cipher.decrypt(ciphertext))
    payload = verify_signature(signed_payload, secret)
    return payload

def send(socket, data, secret, is_encrypt):
    # serialize
    try:
        payload = json.dumps(data)
        if secret:
            if is_encrypt:
                to_send = encrypt_and_sign(payload, secret)
            else:
                to_send = attach_signature(payload, secret)
        else:
            to_send = payload.encode('utf-8')
    except (TypeError, ValueError) as e:
        raise PostofficeException(name='ValueError',
                                  message='You can only send JSON-serializable.')

    # send the data
    socket.send('{}\n'.format(len(to_send)).encode('ascii'))
    socket.sendall(to_send)

def recieve(socket, secret, is_encrypt):
    # read the length of the data, letter by letter until we reach EOL
    length_str = b''
    char = socket.recv(1)

    # check termination
    if not char:
        raise ConnectionTerminated()

    # got a message
    # read message length
    while char != b'\n':
        length_str += char
        char = socket.recv(1)

    bulk_length = int(length_str.decode('ascii'))

    # get the payload
    buffer = memoryview(bytearray(bulk_length))
    next_offset = 0
    while bulk_length - next_offset > 0:
        recv_size = socket.recv_into(buffer[next_offset:], bulk_length - next_offset)
        next_offset += recv_size

    # deserialize payload
    try:
        if secret:
            if is_encrypt:
                payload = decrypt_and_verify(buffer.tobytes(), secret)
            else:
                payload = verify_signature(buffer.tobytes(), secret)
        else:
            payload = buffer.tobytes().decode('utf-8')
        data = json.loads(payload)
    except (TypeError, ValueError):
        raise PostofficeException(name='ValueError',
                                  message='Data received was not in JSON or not decryptable format.')

    return data