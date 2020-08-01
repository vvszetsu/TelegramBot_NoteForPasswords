import threading
import datetime
import os.path
from backend.crypto_and_keePass_interaction import keys
from logs.log import log_info, log_err, log_warn, log_crit_err


class AuthHolder:
    def __init__(self, kp, database_id, auth_time=datetime.datetime.now()):
        self.kp = kp
        self.database_id = database_id
        self.auth_time = datetime.datetime.now()

    def get_auth_time(self):
        return self.auth_time

    def get_kp(self):
        return self.kp

    def get_db_id(self):
        return self.database_id


actual_auth_users = {0: AuthHolder(None, None, auth_time=datetime.datetime.now() - datetime.timedelta(minutes=20))}


def is_user_auth(user_id: int):
    """
    Проверка на аутентификаци
    :param user_id:
    :return: возвращает тру, если юзера можно считать аутентифицированым, иначе фолс.
    """
    return bool(actual_auth_users.get(user_id, 0))


def try_to_auth_user(user_id: int, database_id: int, password: str):
    """

    :param user_id: id пользлователья Telegram
    :param database_id: id базы данных, в которую пользователь хочет войти
    :param password: пароль
    :return: True или False в зависимости от того, получилось ли АУФнуться
    """
    try:
        if database_id is None:
            database_id = user_id
        path_to_db = os.path.join('.', 'backend', 'databases', f'{database_id}.kdbx')
        kp = keys.load_db(path_to_db, password)
        actual_auth_users[user_id] = AuthHolder(kp, database_id)
        return True
    except Exception as exc:
        log_err(exc)
        return False


NONE = None


def get_user_database(user_id):
    return actual_auth_users.get(user_id, NONE).get_kp()


def get_db_id(user_id):
    return actual_auth_users.get(user_id, NONE).get_db_id()


class MyThread(threading.Thread):
    def __init__(self, event_to_do, func_to_do, time=10):
        threading.Thread.__init__(self)
        self.stopped = event_to_do
        self.func = func_to_do
        self.time = time

    def run(self):
        while not self.stopped.wait(self.time):
            self.func()


def check():
    lst = []
    for user_id, authHolder in actual_auth_users.items():
        if (datetime.datetime.now() - authHolder.get_auth_time()) > datetime.timedelta(minutes=1):
            lst.append(user_id)
    for user_id in lst:
        log_info(f"user {user_id}'s auth has expired ")
        deauth(user_id)


def deauth(user_id):
    if user_id in actual_auth_users.keys():
        actual_auth_users.pop(user_id)


stopFlag = threading.Event()
s = MyThread(stopFlag, check)
s.start()
