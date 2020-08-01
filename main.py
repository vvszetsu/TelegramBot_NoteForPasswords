import os
from backend.crypto_and_keePass_interaction import keys
from backend.crypto_and_keePass_interaction.encrypt import encrypt, auto_mode
from backend.user_data.db_requests import UsersDataBase
from backend.crypto_and_keePass_interaction.auth import is_user_auth, try_to_auth_user as try_auth, get_user_database, \
    deauth, get_db_id
from backend.decorators import auth_check
from bot import bot, keyboard, empty_kb
from logs.log import log_err, log_crit_err, log_info, log_warn

add_data = UsersDataBase.add_user
search_data = UsersDataBase.search_user
del_data = UsersDataBase.del_user


def err_msg(user_id):
    try:
        bot.send_message(user_id, "Что-то пошло не так, попробуйте снова")
    except Exception as exc:
        log_err(exc)
        return


@bot.message_handler(commands=['start'])
def start_message(message):
    """
    Первый шаг к созданию базы данных. Проверяет, есть ли база данных у данного пользователя
    """
    path_to_db = os.path.join('.', 'backend', 'databases', str(message.from_user.id) + '.kdbx')
    if os.path.exists(path_to_db):
        bot.send_message(message.from_user.id, 'У тебя уже есть база данных!')  # , reply_markup=keyboard")
    else:
        send = bot.send_message(message.from_user.id,
                                'Введите данные для регистрации в формате пароль:логин '
                                '(второй параметр необязательный, если указан только пароль,'
                                ' то логином по умолчанию станет текущий хэндл в телеграме)')
        bot.register_next_step_handler(send, create_db)


def create_db(message):
    """
    Создаёт базу данных с паролями
    """
    log_info(f"user {message.from_user.id} tried to create new database")
    login_default = message.text.find(':') == -1  # Проверка, нужен дефолтный логин, или нет
    if login_default:
        login = message.from_user.username
        str_pass = encrypt(message.text)
    else:
        login = message.text[message.text.find(':') + 1:]
        str_pass = encrypt(message.text[:message.text.find(':')])
    if len(search_data(login)) != 0:
        bot.send_message(message.from_user.id, 'Этот логин уже занят. Попробуйте снова')
    else:
        superlogin = encrypt(login)
        try:
            add_data(message.from_user.username, message.from_user.id, superlogin)
            keys.make_db('./backend/databases/' + str(message.from_user.id), str_pass)
        except Exception as exc:
            log_err(exc)
            err_msg(message.from_user.id)
            return
        bot.send_message(message.from_user.id, 'База данных создана! ')  # , reply_markup=keyboard")


@bot.message_handler(commands=['get_password'])
@auth_check
def get_password(message):
    """
    Первый шаг к получению пароля
    """
    log_info(f"user {message.from_user.id} tried to get password by title")
    send = bot.send_message(message.from_user.id, "Введите название записи")
    bot.register_next_step_handler(send, send_password)


def send_password(message):
    """
    Отсылает данные о записи после проверки
    """
    recording = message.text
    try:
        kp = get_user_database(message.from_user.id)
        passwords = keys.load_password(kp, recording)
    except Exception as exc:
        log_err(exc)
        err_msg(message.from_user.id)
        return
    if passwords == '':
        bot.send_message(message.from_user.id, 'Такой записи нет. Попробуй снова')
    else:
        bot.send_message(message.from_user.id, passwords)


@bot.message_handler(commands=['add_password'])
@auth_check
def add_pass(message):
    """
    Проверяет, есть ли у пользователя база паролей, и если да - перенаправляет на следующий шаг
    """
    send = bot.send_message(message.from_user.id,
                            'Напишите название записи, логин и пароль в формате название:логин:пароль, либо'
                            'название:логин, если хотите, чтоб пароль был сгенерирован за вас')
    bot.register_next_step_handler(send, create_recording)


def create_recording(message):
    """
    Создаёт в базе паролей запись
    """
    content = message.text.split(':')
    try:
        kp = get_user_database(message.from_user.id)
    except Exception as exc:
        log_err(exc)
        err_msg(message.from_user.id)
        return
    if len(content) == 3:
        try:
            log_info(f"user {message.from_user.id} tried to create new entry")
            keys.new_entry(kp, content[0], content[1], content[2])
            log_info(f"user {message.from_user.id} successfully created new entry")
            bot.send_message(message.from_user.id, 'Запись успешно добавлена под названием ' + content[0])
        except Exception as exc:
            if str(exc).find('already exists'):
                log_info(f"user {message.from_user.id} tried to create already existed entry")
                bot.send_message(message.from_user.id, 'Такая запись уже существует')
            else:
                bot.send_message(message.from_user.id, 'Напиши в телеграм @k1ngpin или @delanary, '
                                                       'это явно какой-то баг')
    elif len(content) == 2:
        password = auto_mode()
        try:
            keys.new_entry(kp, content[0], content[1], password)
            bot.send_message(message.from_user.id, 'Запись успешно добавлена под названием ' + content[0] +
                             ', пароль от неё - ' + password)
        except Exception as exc:
            if str(exc).find('already exists'):
                bot.send_message(message.from_user.id, 'Такая запись уже существует')
            else:
                bot.send_message(message.from_user.id, 'Напиши в телеграм @k1ngpin или @delanary, '
                                                       'это явно какой-то баг')
                log_err(exc)
                err_msg(message.from_user.id)
                return
    else:
        bot.send_message(message.from_user.id, 'Неправильный формат. Попробуй ещё раз')


@bot.message_handler(commands=['show_names'])
@auth_check
def show_names(message):
    """
    Присылает пользователю список записей
    :param message:
    :return:
    """
    log_info(f"user {message.from_user.id} requested names")
    try:
        kp = get_user_database(message.from_user.id)
        names = keys.all_names(kp)
        bot.send_message(message.from_user.id, '\n'.join(names))
    except Exception as exc:
        log_err(exc)
        err_msg(message.from_user.id)
        return


@bot.message_handler(commands=['deauth'])
def deauth_me(message):
    """
    Удаляет запись про аутентификацию из словаря
    :param message:
    :return:
    """
    log_info(f"user {message.from_user.id} deauthed")
    if is_user_auth(message.from_user.id):
        deauth(message.from_user.id)
        bot.send_message(message.from_user.id, 'Вы вышли из системы')


@bot.message_handler(commands=['auth'])
@auth_check
def auth_me(message):
    """
    Создает запись про аутентификацию в словаре
    :param message:
    :return:
    """
    bot.send_message(message.from_user.id, 'Вы вошли в систему')


@bot.message_handler(commands=['kill_all'])
@auth_check
def kill_all(message):
    """
    Удаляет полностью объект PyKeePass и запись из БД
    :param message:
    :return:
    """
    send = bot.send_message(message.from_user.id, 'Вы уверены, что хотите удалить свою базу паролей? [Да или Нет]',
                            reply_markup=keyboard)
    bot.register_next_step_handler(send, kill_confirm)


def kill_confirm(message):
    """
    Проверяет, подтвердли ли пользователь удаление, и если да - удаляет
    :param message:
    :return:
    """
    if message.text.lower() == 'да':
        database_id = get_db_id(message.from_user.id)
        del_data(database_id)
        path_to_kp = os.path.join('backend', 'databases', str(database_id) + '.kdbx')
        os.remove(path_to_kp)
        deauth(message.from_user.id)
        bot.send_message(message.from_user.id, 'Ваша база паролей была успешно удалена.', reply_markup=empty_kb)
    elif message.text.lower() == 'нет':
        bot.send_message(message.from_user.id, 'Процедура удаления базы паролей прервана', reply_markup=empty_kb)
    else:
        bot.send_message(message.from_user.id, 'Вы написали что-то странное. Попробуйте ещё раз', reply_markup=empty_kb)


@bot.message_handler(commands=['generate_password'])
def generate_pass(message):
    """
    Генерирует пользователю сильный пароль

    :param message:
    :return:
    """
    password = auto_mode()
    bot.send_message(message.from_user.id, password)


bot.polling()
