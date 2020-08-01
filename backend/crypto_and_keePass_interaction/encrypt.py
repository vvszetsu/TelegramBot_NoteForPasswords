import hashlib
import string
import random

small = string.ascii_lowercase
big = string.ascii_uppercase
spec = '!@#$%&*?^'
digits = string.digits
all_symbols = spec + digits + string.ascii_letters


def encrypt(string):
    """
    Хэширует строку

    :param string: хэшируемая строка
    :return: 16-ричное представление хэша
    """
    password = hashlib.sha512()
    password.update(string.encode('utf-8'))
    for i in range(100000):
        string = password.hexdigest()
        password.update(string.encode('utf-8'))
    return password.hexdigest()


def auto_mode(all_s=all_symbols, length=25):
    count = 0
    res = []
    while count < length:
        res.append(random.choice(all_s))
        count += 1
    password = ''.join(res)
    return password
