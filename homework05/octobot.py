import json
from datetime import datetime, timedelta
from urllib.parse import urlparse

import gspread  # type: ignore
import pandas as pd  # type: ignore
import requests  # type: ignore
import telebot  # type: ignore

bot = telebot.TeleBot("6217258754:AAECo5MdD1DaFJI_GHfbgPcYhIpZSL8pgyM")
IS_CONNECTED = False
DATA = []
RETURN = "Меню"


def is_valid_date(date: str = "01/01/00", divider: str = "/") -> bool:
    """Проверяем, что дата дедлайна валидна:
    - дата не может быть до текущей
    - не может быть позже, чем через год
    - не может быть такой, которой нет в календаре
    - может быть сегодняшним числом
    - пользователь не должен быть обязан вводить конкретный формат даты
    (например, только через точку или только через слеш)"""
    if divider not in date:
        return False
    dmy = date.split(divider)
    if len(dmy) < 3:
        return False
    d, m, y = list(map(int, dmy))
    today = list(map(int, datetime.today().date().strftime("20%y/%m/%d").split(sep="/")))
    today = datetime(today[0], today[1], today[2])  # type: ignore
    try:
        date = datetime(2000 + y, m, d)  # type: ignore
    except ValueError:
        return False
    period = date - today  # type: ignore
    return period.days < 365 and date >= today  # type: ignore


def is_valid_url(url: str = "") -> bool:
    """Проверяем, что ссылка рабочая"""
    try:
        parsed_url = urlparse(url)
        if not parsed_url.scheme:
            url = "http://" + url
        response = requests.get(url)
        if response.status_code == 200:
            return True
    except (requests.exceptions.ConnectionError, requests.exceptions.InvalidURL):
        return False
    return False


def convert_date(date: str = "01/01/00"):
    """Конвертируем дату из строки в datetime"""
    return datetime.strptime(date, "%d.%m.%y")


def connect_table(message):
    """Подключаемся к Google-таблице"""
    global IS_CONNECTED
    url = message.text
    print(url)
    sheet_id = "15L-ZkV96TSxG4The10aiuEWh9fTbvu_FKZW3c7JTi-E"
    try:
        with open("tables.json", encoding="utf-8") as json_file:
            tables = json.load(json_file)
        title = len(tables) + 1
        tables[title] = {"url": url, "id": sheet_id}
    except FileNotFoundError:
        tables = {0: {"url": url, "id": sheet_id}}
    with open("tables.json", "w", encoding="utf-8") as json_file:
        json.dump(tables, json_file)
    IS_CONNECTED = True
    bot.send_message(message.chat.id, "Таблица подключена!")


def access_current_sheet():
    """Обращаемся к Google-таблице"""
    with open("tables.json", encoding="utf-8") as json_file:
        tables = json.load(json_file)

    sheet_id = tables[max(tables)]["id"]
    gc = gspread.service_account(filename="credentials.json")
    sh = gc.open_by_key(sheet_id)
    worksheet = sh.sheet1
    # Преобразуем Google-таблицу в таблицу pandas
    df = pd.DataFrame(worksheet.get_values(), columns=worksheet.row_values(1))
    return worksheet, tables[max(tables)]["url"], df


def choose_action(message):
    """Обрабатываем действия верхнего уровня"""
    if message.text == "Подключить Google-таблицу":
        connect_table(message)
    elif message.text == "Редактировать предметы":
        start_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        start_markup.row("Добавить предмет")
        start_markup.row("Редактировать предмет")
        start_markup.row("Удалить один предмет")
        start_markup.row("Удалить все предметы")
        start_markup.row(RETURN)
        info = bot.send_message(message.chat.id, "Чем могу помочь?", reply_markup=start_markup)
        bot.register_next_step_handler(info, choose_subject_action)
    elif message.text == "Редактировать дедлайн":
        start_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        start_markup.row("Добавить дедлайн")
        start_markup.row("Изменить дедлайн")
        start_markup.row(RETURN)
        information = bot.send_message(message.chat.id, "Чем могу помочь?", reply_markup=start_markup)
        bot.register_next_step_handler(information, choose_deadline_action)
    elif message.text == "Посмотреть дедлайны на этой неделе":
        today = datetime.today()
        week = today + timedelta(days=7)
        list_object, list_url, dataframe = access_current_sheet()
        message_1 = f""
        for i in range(2, len(list_object.col_values(1)) + 1):
            for deadline in list_object.row_values(i)[2:]:
                try:
                    if week >= convert_date(deadline) >= today - timedelta(days=1):
                        message_1 += f"{list_object.cell(i, 1).value}: {deadline}\n"
                except ValueError:
                    continue
        if not message_1:
            message_1 = "На этой неделе нет дедлайнов"
        bot.send_message(message.chat.id, message_1)
        start(message)


def choose_subject_action(message):
    """Выбираем действие в разделе Редактировать предметы"""
    if message.text == "Добавить предмет":
        message = bot.send_message(message.chat.id, "Введите название нового предмета")
        bot.register_next_step_handler(message, add_new_subject_name)
    elif message.text == "Редактировать предмет":
        list_object, list_url, dataframe = access_current_sheet()
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for element in dataframe.subject:
            if element != "subject":
                markup.row(f"{element}")
        markup.row(RETURN)
        information = bot.send_message(message.chat.id, "Какой предмет требуется отредактировать?", reply_markup=markup)
        bot.register_next_step_handler(information, choose_info_to_update)
    elif message.text == "Удалить один предмет":
        list_object, list_url, dataframe = access_current_sheet()
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for element in dataframe.subject:
            if element != "subject":
                markup.row(f"{element}")
        markup.row(RETURN)
        information = bot.send_message(message.chat.id, "Какой предмет удаляем?", reply_markup=markup)
        bot.register_next_step_handler(information, delete_subject)
    elif message.text == "Удалить все предметы":
        del_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        del_markup.row("Удалить")
        del_markup.row("Не удалять")
        information = bot.send_message(message.chat.id, "Вы точно хотите удалить всё?", reply_markup=del_markup)
        bot.register_next_step_handler(information, choose_removal_option)
    else:
        start(message)


def choose_deadline_action(message):
    """Выбираем действие в разделе Редактировать дедлайн"""
    global DATA
    if message.text != RETURN:
        DATA = [message.text]  # change or add
        list_object, list_url, dataframe = access_current_sheet()
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for element in dataframe.subject:
            if element != "subject":
                markup.row(f"{element}")
        markup.row(RETURN)
        text = (
            "Для какого предмета добавить дедлайн?"
            if message.text == "Добавить дедлайн"
            else "Для какого предмета изменить дедлайн?"
        )
        information = bot.send_message(message.chat.id, text, reply_markup=markup)

        bot.register_next_step_handler(information, choose_subject)
    else:
        start(message)


def choose_removal_option(message):
    """Уточняем, точно ли надо удалить все"""
    if message.text == "Удалить всё":
        clear_subject_list(message)
    else:
        start(message)


def choose_subject(message):
    """Выбираем предмет, у которого надо отредактировать дедлайн"""
    if message.text != RETURN:
        DATA.append(message.text)  # added subject
        list_object, list_url, dataframe = access_current_sheet()
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        any_options = False
        for element in dataframe.columns[2:]:
            row = list_object.find(f"{DATA[1]}").row
            col = list_object.find(f"{element}").col
            if DATA[0] == "Добавить дедлайн" and list_object.cell(row, col).value is None:
                markup.row(f"{element}")
            elif DATA[0] == "Изменить дедлайн" and list_object.cell(row, col).value is not None:
                any_options = True
                markup.row(f"{element}")
        if DATA[0] == "Добавить дедлайн":
            any_options = True
            markup.row("Добавить новую работу")
            mess = "Для какой работы Вы хотите добавить дедлайн?"
        else:
            mess = "Для какой работы Вы хотите изменить дедлайн?"
        if any_options:
            markup.row(RETURN)
            information = bot.send_message(message.chat.id, mess, reply_markup=markup)
            bot.register_next_step_handler(information, get_lab_number)
        else:
            bot.send_message(message.chat.id, "Дедлайнов для этого предмета не было. Попробуйте заново")
            start(message)
    else:
        start(message)


def get_lab_number(message):
    DATA.append(message.text)  # added lab num
    information = bot.send_message(message.chat.id, "Введите дедлайн в формате DD.MM.YY или DD/MM/YY")
    bot.register_next_step_handler(information, update_subject_deadline)


def update_subject_deadline(message):
    """Обновляем дедлайн"""
    try:
        date = message.text.strip()
        divider = date[2]
        date = date.replace(divider, ".")
        if is_valid_date(date, "."):
            list_object, list_url, dataframe = access_current_sheet()
            row = list_object.find(f"{DATA[1]}").row

            if DATA[2] == "Добавить новую работу":
                length = len(list_object.row_values(1))
                number = int(list_object.cell(1, length).value) if length > 2 else 0
                list_object.update_cell(1, length + 1, number + 1)
                col = length + 1
            else:
                col = list_object.find(f"{DATA[2]}").col

            list_object.update_cell(row, col, date)
            bot.send_message(message.chat.id, "Дедлайн установлен!")
            start(message)
        else:
            information = bot.send_message(
                message.chat.id,
                "Некорректная дата или дедлайн уже прошел. Введите дедлайн в формате DD.MM.YY или DD/MM/YY",
            )
            bot.register_next_step_handler(information, update_subject_deadline)
    except ValueError:
        information = bot.send_message(
            message.chat.id,
            "Введите дедлайн в формате DD.MM.YY или DD/MM/YY",
        )
        bot.register_next_step_handler(information, update_subject_deadline)


def add_new_subject_name(message):
    global DATA
    DATA = [message.text]
    list_object, list_url, dataframe = access_current_sheet()
    if message.text not in dataframe["subject"].unique():
        list_object.append_row([message.text])
        bot.send_message(message.chat.id, "Предмет добавлен")
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.row("Добавить ссылку на предмет")
        markup.row(RETURN)
        info = bot.send_message(
            message.chat.id, "Добавить ссылку к предмету " + message.text + "?", reply_markup=markup
        )
        bot.register_next_step_handler(info, update_info)
    else:
        information = bot.send_message(
            message.chat.id, "Такой предмет уже есть. Напишите уникальное название и ссылку на предмет через пробел"
        )
        bot.register_next_step_handler(information, add_new_subject_name)


def choose_info_to_update(message):
    global DATA
    if message.text != RETURN:
        DATA = [message.text]  # added subject
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.row("Изменить название предмета")

        list_object, list_url, dataframe = access_current_sheet()
        row, col = list_object.find(f"{DATA[0]}").row, 2
        if list_object.cell(row, col).value is None:
            markup.row("Добавить ссылку на предмет")
            markup.row("Изменить название предмета и добавить ссылку")
        else:
            markup.row("Изменить ссылку на предмет")
            markup.row("Изменить и название предмета, и ссылку на него")

        markup.row(RETURN)
        information = bot.send_message(message.chat.id, "Как требуется отредактировать?", reply_markup=markup)
        bot.register_next_step_handler(information, update_info)
    else:
        start(message)


def update_info(message):
    DATA.append("one")
    if message.text != RETURN:
        if message.text == "Изменить название предмета":
            get_updated_name(message)
        elif message.text == "Изменить ссылку на предмет" or message.text == "Добавить ссылку на предмет":
            get_updated_url(message)
        elif (
            message.text == "Изменить и название предмета, и ссылку на него"
            or message.text == "Изменить название предмета и добавить ссылку"
        ):
            DATA[1] = "both"
            get_updated_name(message)
    else:
        start(message)


def get_updated_name(message):
    information = bot.send_message(message.chat.id, "Введите новое название для предмета " + DATA[0])
    bot.register_next_step_handler(information, update_subject_name)


def get_updated_url(message):
    information = bot.send_message(message.chat.id, "Введите новую ссылку для предмета " + DATA[0])
    bot.register_next_step_handler(information, update_subject_url)


def update_subject_name(message):
    name = message.text
    list_object, list_url, dataframe = access_current_sheet()
    if name not in dataframe["subject"].unique():
        index = dataframe.loc[dataframe.isin(DATA).any(axis=1)].index[0] + 1
        cell_list = list_object.range(f"A{index}")
        cell_list[0].value = name
        list_object.update_cells(cell_list)
        bot.send_message(message.chat.id, "Название изменено")
        if DATA[1] == "both":
            DATA[0] = name
            get_updated_url(message)
        else:
            start(message)
    else:
        information = bot.send_message(message.chat.id, "Такой предмет уже есть. Введите уникальное название предмета")
        bot.register_next_step_handler(information, update_subject_name)


def update_subject_url(message):
    url = message.text
    if is_valid_url(url):
        list_object, list_url, dataframe = access_current_sheet()
        index = dataframe.loc[dataframe.isin(DATA).any(axis=1)].index[0] + 1
        cell_list = list_object.range(f"B{index}")
        cell_list[0].value = url
        list_object.update_cells(cell_list)
        bot.send_message(message.chat.id, "Ссылка установлена")
        start(message)
    else:
        information = bot.send_message(message.chat.id, "Ссылка некорректна. Введите новую ссылку в корректном формате")
        bot.register_next_step_handler(information, update_subject_url)


def delete_subject(message):
    """Удаляем предмет в Google-таблице"""
    if message.text != RETURN:
        list_object, list_url, dataframe = access_current_sheet()
        index = dataframe.loc[dataframe.isin([message.text]).any(axis=1)].index[0] + 1
        list_object.delete_rows(int(index), int(index))
        bot.send_message(message.chat.id, "Удалено")
    start(message)


def clear_subject_list(message):
    """Удаляем все из Google-таблицы"""
    with open("tables.json") as json_file:
        tables = json.load(json_file)
    sheet_id = tables[max(tables)]["id"]
    client = gspread.service_account(filename="credentials.json")
    sheet = client.open_by_key(sheet_id)
    worksheets = sheet.worksheets()
    # worksheet = sheet.sheet1
    # sheet.del_worksheet(worksheet)
    # start(message)
    reqs = [
        {"repeatCell": {"range": {"sheetId": s.id}, "fields": "*"}} if i == 0 else {"deleteSheet": {"sheetId": s.id}}
        for i, s in enumerate(worksheets)
    ]
    sheet.batch_update({"requests": reqs})
    start(message)


@bot.message_handler(commands=["start"])
def start(message):
    global IS_CONNECTED

    try:
        with open("tables.json", encoding="utf-8"):
            IS_CONNECTED = True
    except FileNotFoundError:
        IS_CONNECTED = False

    start_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    if not IS_CONNECTED:
        start_markup.row("Подключить Google-таблицу")
    else:
        list_object, list_url, dataframe = access_current_sheet()
        message_1 = f""
        try:
            for i in dataframe.index:
                if i >= 1:
                    message_1 += f"[{dataframe.loc[i, 'subject']}]({dataframe.loc[i, 'link']})\n"
            if message_1:
                bot.send_message(message.chat.id, message_1, parse_mode="MarkdownV2", disable_web_page_preview=True)
        except KeyError:
            bot.send_message(message.chat.id, "Таблица сейчас пуста", parse_mode="MarkdownV2")

    start_markup.row("Посмотреть дедлайны на этой неделе")
    start_markup.row("Редактировать дедлайн")
    start_markup.row("Редактировать предметы")
    information = bot.send_message(message.chat.id, "Что хотите сделать?", reply_markup=start_markup)
    bot.register_next_step_handler(information, choose_action)


if __name__ == "__main__":
    bot.infinity_polling()
