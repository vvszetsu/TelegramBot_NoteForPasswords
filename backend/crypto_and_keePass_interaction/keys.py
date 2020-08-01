from pykeepass import PyKeePass, create_database


def load_db(path, pas):
    """

    :param path: путь к файлу
    :param pas: пароль
    :return: объект PyKeePass по указанным параметрам
    """
    kp = PyKeePass(path, password=pas)
    return kp


def load_group(kp, name='Root'):
    """
    :param kp: объект PyKeePass
    :param name: Название группы
    :return: Группу PyKeePass
    """
    return kp.find_groups(name=name)


def all_names(kp):
    """
    :param kp: объект PyKeePass
    :return:
    """
    names = []
    for index, item in enumerate(kp.entries):
        names.append(f"{index + 1}. {item.title if item.title else ''}{' ' + item.url if item.url else ''}")
    return names


def load_password(kp, title):
    """

    :param kp: объект PyKeePass
    :param title: название записи
    :return: записи с указанным названием
    """
    entries = kp.find_entries(title=title)
    passwords = ''
    for ent in entries:
        passwords += 'log: ' + ent.username + ', pass: ' + ent.password + '\n'
    return passwords


def make_db(name, password):
    """
    Создаёт базу паролей по заданным параметрам

    :param name: название базы паролей
    :param password: мастер-пароль
    """
    create_database(name + '.kdbx', password=password)


def new_entry(kp, name, login, password):
    """
    Создаёт новую запись в базе паролей

    :param kp: объект PyKeePass
    :param name: название записи
    :param login: логин
    :param password: пароль
    """
    group = load_group(kp)
    kp.add_entry(group[0], name, login, password)
    kp.save()
