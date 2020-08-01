import sqlite3
import pandas as pd
import os.path
from logs.log import log_info, log_warn, log_err, log_crit_err
import datetime
from backend.crypto_and_keePass_interaction.encrypt import encrypt


class UsersDataBase:
    conn = sqlite3.connect(os.path.join("./backend/user_data/databasesql.db"), check_same_thread=False)
    cursor = conn.cursor()

    @classmethod
    def add_user(cls, handle: str, user_id: int, superlogin_hash: str):
        """
        Добавляет запись в базу данных

        :param handle: хэндл
        :param user_id: айди чата
        :param superlogin_hash: хэш от суперлогина
        """
        try:
            cls.cursor.execute("""INSERT INTO USERS
            VALUES (?, ?, ?, datetime("now", "localtime"))""", (handle, user_id, superlogin_hash))
            cls.conn.commit()
        except Exception as exc:
            log_err(exc)

    @classmethod
    def search_user(cls, superlogin: str):
        """
        Осуществляет поиск строк по суперлогину

        :param superlogin:
        :return: возвращает датафрейм, в котором находятся строки, где хэш суперлогина такой же, как у входного
        """
        superlogin_hash = encrypt(superlogin)
        print(superlogin_hash)
        try:
            cls.cursor.execute("""SELECT * FROM USERS WHERE superlogin_hash=?""", (superlogin_hash,))
            lst = cls.cursor.fetchall()
            cls.conn.commit()
        except Exception as exc:
            log_err(exc)
            return pd.DataFrame(columns=["handle", "chat_id", "superlogin_hash", "last_auth_time"])
        return pd.DataFrame(lst, columns=["handle", "chat_id", "superlogin_hash", "last_auth_time"])

    @classmethod
    def del_user(cls, database_id: int):
        """
        Удаляет строку из БД

        :param database_id:
        :return:
        """
        cls.cursor.execute("""DELETE FROM USERS
        WHERE chat_id=(?) """, (database_id, ))
        cls.conn.commit()
