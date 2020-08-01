from backend.crypto_and_keePass_interaction.auth import is_user_auth, try_to_auth_user as try_auth
from backend.crypto_and_keePass_interaction.encrypt import encrypt
from logs.log import log_info, log_warn, log_err, log_crit_err
from backend.user_data.db_requests import UsersDataBase
from bot import bot

search_user = UsersDataBase.search_user


def auth_check(function_to_auth_check):
    """
    :param function_to_auth_check:
    :return:
    """

    def wrapper(*args, **kwargs):
        try:
            user_id = args[0].from_user.id
        except Exception as exc:
            log_err(exc)
            return
        if is_user_auth(user_id):
            function_to_auth_check(*args, **kwargs)
        else:
            def check_password(message):
                """
                Сверяет пароль с тем, что есть в базе данных
                """
                user_id = message.from_user.id
                right_login = True
                if message.text.find(':') != -1:
                    lst = message.text.split(':')
                    str_pass = encrypt(lst[0])
                    line_user = search_user(lst[1])['chat_id']
                    if len(line_user) != 0:
                        database_id = line_user.iloc[0]
                        try:
                            log_info(f"User {message.from_user.id} tried to auth as user {database_id}")
                            bot.send_message(database_id, f'В твою базу данных пытается зайти '
                                                          f'@{message.from_user.username if message.from_user.username is not None else " неизвестно"}. '
                                                          f'Его TelegramID - {message.from_user.id}')
                        except Exception as exc:
                            log_err(exc)
                    else:
                        right_login = False
                else:
                    str_pass = encrypt(message.text)
                    database_id = user_id
                if right_login and try_auth(user_id, database_id, str_pass):
                    log_info(f"user {message.from_user.id} successfully authed as {database_id}")
                    bot.send_message(user_id, 'Пароль подошёл.')
                    function_to_auth_check(*args, **kwargs)
                elif not right_login:
                    bot.send_message(message.from_user.id, 'Такого логина нет')
                else:
                    log_info(f"user {message.from_user.id} unsuccessfully tried to auth as {database_id}")
                    bot.send_message(message.from_user.id, 'Пароль неправильный. Попробуйте позже')

            send = bot.send_message(user_id, "Введите мастер-пароль, если хотите войти в свою базу данных, или "
                                             "мастер-пароль:суперлогин, "
                                             "если хотите войти в базу данных другого пользователя")
            bot.register_next_step_handler(send, check_password)

    return wrapper
