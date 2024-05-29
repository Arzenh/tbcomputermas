import telebot
from telebot import types
import mysql.connector
from mysql.connector import errorcode

try:
    db = mysql.connector.connect(
        host="DESKTOP-8TD8BQ8",
        port=3306,
        user="artemk",
        password="khol_pass",
        database="computermas"
    )
    print("Connected to database successfully")

except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)

bot = telebot.TeleBot('6808400632:AAEUZaHadxeZpHk-3iy3JEuwzKW2JuqZZCs')

@bot.message_handler(commands=['start', 'меню'])
def start_command(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_services = types.KeyboardButton(text='Показати сервіси')
    button_add_service = types.KeyboardButton(text='Додати новий сервіс')
    button_add_manager = types.KeyboardButton(text='Додати менеджера')
    button_add_engineer = types.KeyboardButton(text='Додати інженера')
    button_delete_service = types.KeyboardButton(text='Видалити сервіс')
    button_delete_manager = types.KeyboardButton(text='Видалити менеджера')
    button_delete_enginer = types.KeyboardButton(text='Видалити інженера')
    keyboard.add( button_services ,button_add_service, button_add_manager, button_add_engineer, button_delete_service, button_delete_manager, button_delete_enginer)
    bot.send_message(message.chat.id, 'Вибрати дію:', reply_markup=keyboard)



@bot.message_handler(func=lambda message: message.text == 'Показати сервіси')
def show_services(message):
    try:
        cursor = db.cursor()
        cursor.execute("SELECT id_service, name_service, address, time_begin, time_end FROM comp_service")
        services = cursor.fetchall()
        cursor.close()

        if services:
            for service in services:
                response = f"<b>{service[1]}</b>\nАдреса: {service[2]}\nчас роботи: {service[3]} - {service[4]}"
                keyboard = types.InlineKeyboardMarkup()
                button = types.InlineKeyboardButton(
                    text="Вибрати",
                    callback_data=f'service_{service[0]}'
                )
                keyboard.add(button)
                bot.send_message(message.chat.id, response, reply_markup=keyboard, parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, "Сервіси не занйдено.", parse_mode='HTML')
    except mysql.connector.Error as err:
        bot.send_message(message.chat.id, f"Помилка при виконанню запиту: {err}", parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: call.data.startswith('service_'))
def service_callback(call):
    service_id = call.data.split('_')[1]
    keyboard = types.InlineKeyboardMarkup()
    button_managers = types.InlineKeyboardButton(text='Показати менеджеров', callback_data=f'managers_{service_id}')
    button_engineers = types.InlineKeyboardButton(text='Показати інженеров', callback_data=f'engineers_{service_id}')
    keyboard.add(button_managers, button_engineers)
    bot.send_message(call.message.chat.id, f'Ви обрали сервіс {service_id}. Виберіть дію:', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith('managers_'))
def show_managers(call):
    service_id = call.data.split('_')[1]
    try:
        cursor = db.cursor()
        cursor.execute(f"SELECT id_manager, name, phone FROM manager WHERE comp_service_id_service = {service_id}")
        managers = cursor.fetchall()
        cursor.close()

        if managers:
            response = f"<b>Список менеджеров сервіса {service_id}:</b>\n"
            for manager in managers:
                response += f"{manager[0]}: {manager[1]}, Телефон: {manager[2]}\n"
            bot.send_message(call.message.chat.id, response, parse_mode='HTML')
        else:
            bot.send_message(call.message.chat.id, "Менеджери не знайдені.", parse_mode='HTML')
    except mysql.connector.Error as err:
        bot.send_message(call.message.chat.id, f"Помилка при виконанню запиту: {err}", parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: call.data.startswith('engineers_'))
def show_engineers(call):
    service_id = call.data.split('_')[1]
    try:
        cursor = db.cursor()
        cursor.execute(f"SELECT id_enganer, name, phone, specialization FROM service_enganer WHERE comp_service_id_service = {service_id}")
        engineers = cursor.fetchall()
        cursor.close()

        if engineers:
            response = f"<b>Список інженерів сервіса {service_id}:</b>\n"
            for engineer in engineers:
                response += f"{engineer[0]}: {engineer[1]}, Телефон: {engineer[2]}, Спеціалізація: {engineer[3]}\n"
            bot.send_message(call.message.chat.id, response, parse_mode='HTML')
        else:
            bot.send_message(call.message.chat.id, "Інженери не знайдені.", parse_mode='HTML')
    except mysql.connector.Error as err:
        bot.send_message(call.message.chat.id, f"Помилка при виконанню запиту: {err}", parse_mode='HTML')

@bot.message_handler(func=lambda message: message.text == 'Додати сервіс')
def add_service_handler(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_existing_services = types.KeyboardButton(text='Вибрати існуючий сервіс')
    button_new_service = types.KeyboardButton(text='Додати новий сервіс')
    keyboard.add(button_existing_services, button_new_service)
    bot.send_message(message.chat.id, "Вибрати опцію:", reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == 'Вибрати існуючий сервіс')
def choose_existing_service(message):
    try:
        cursor = db.cursor()
        cursor.execute("SELECT id_service, name_service FROM comp_service")
        services = cursor.fetchall()
        cursor.close()

        if services:
            keyboard = types.InlineKeyboardMarkup()
            for service in services:
                button = types.InlineKeyboardButton(
                    text=service[1],
                    callback_data=f'existing_service_{service[0]}'
                )
                keyboard.add(button)
            bot.send_message(message.chat.id, "Вибрати сервіс:", reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, "Сервіси не знайдені.")
    except mysql.connector.Error as err:
        bot.send_message(message.chat.id, f"Помилка при виконанні запиту: {err}")


@bot.message_handler(func=lambda message: message.text == 'Додати новий сервіс')
def add_new_service(message):
    cursor = db.cursor()
    cursor.execute("SELECT id_service, name_service, address FROM comp_service")
    services = cursor.fetchall()
    cursor.close()
    
    services_info = "\n".join([f"ID: {service[0]}, Назва: {service[1]}, Адреса: {service[2]}" for service in services])
    bot.send_message(message.chat.id, f"Існуючі сервіси:\n{services_info}")

    msg = bot.send_message(message.chat.id, "Введіть нове ID сервіса:")
    bot.register_next_step_handler(msg, add_service_name)

def add_service_name(message):
    chat_id = message.chat.id
    service_id = message.text
    msg = bot.send_message(chat_id, "Введіть назву сервіса:")
    bot.register_next_step_handler(msg, lambda msg: add_service_address(service_id, msg))

def add_service_address(service_id, message):
    chat_id = message.chat.id
    service_name = message.text
    msg = bot.send_message(chat_id, "Введіть адресу сервіса:")
    bot.register_next_step_handler(msg, lambda msg: add_service_time(service_id, service_name, msg))

def add_service_time(service_id, service_name, message):
    chat_id = message.chat.id
    address = message.text
    msg = bot.send_message(chat_id, "Введіть час початку роботи (HH:MM):")
    bot.register_next_step_handler(msg, lambda msg: add_service_end_time(service_id, service_name, address, msg))

def add_service_end_time(service_id, service_name, address, message):
    chat_id = message.chat.id
    time_begin = message.text
    msg = bot.send_message(chat_id, "Введіть час завершення роботи (HH:MM):")
    bot.register_next_step_handler(msg, lambda msg: save_service(service_id, service_name, address, time_begin, msg))


def save_service(service_id, service_name, address, time_begin, message):
    chat_id = message.chat.id
    time_end = message.text
    try:
        cursor = db.cursor()
        cursor.execute("INSERT INTO comp_service (id_service, name_service, address, time_begin, time_end) VALUES (%s, %s, %s, %s, %s)",
                       (service_id, service_name, address, time_begin, time_end))
        db.commit()
        cursor.close()
        bot.send_message(chat_id, f"Сервіс '{service_name}' успішно додан.")
    except mysql.connector.Error as err:
        bot.send_message(chat_id, f"Помилка при додаванню сервіса: {err}")


@bot.message_handler(func=lambda message: message.text == 'Додати менеджера')
def add_manager(message):
    cursor = db.cursor()
    cursor.execute("SELECT id_service, name_service FROM comp_service")
    services = cursor.fetchall()
    cursor.close()
    
    services_info = "\n".join([f"ID: {service[0]}, Назва: {service[1]}" for service in services])
    bot.send_message(message.chat.id, f"Існуючі сервіси:\n{services_info}")
    
    cursor = db.cursor()
    cursor.execute("SELECT id_manager, name, comp_service_id_service FROM manager")
    managers = cursor.fetchall()
    cursor.close()

    managers_info = "\n".join([f"ID: {manager[0]}, Ім'я: {manager[1]}, ID сервіса: {manager[2]}" for manager in managers])
    bot.send_message(message.chat.id, f"Існуючі менеджери:\n{managers_info}")

    msg = bot.send_message(message.chat.id, "Введіть ID менеджера:")
    bot.register_next_step_handler(msg, add_manager_name)

def add_manager_name(message):
    chat_id = message.chat.id
    manager_id = message.text
    msg = bot.send_message(chat_id, "Введіть ім'я менеджера:")
    bot.register_next_step_handler(msg, lambda msg: add_manager_phone(manager_id, msg))

def add_manager_phone(manager_id, message):
    chat_id = message.chat.id
    manager_name = message.text
    msg = bot.send_message(chat_id, "Введіть номер телефона менеджера:")
    bot.register_next_step_handler(msg, lambda msg: add_manager_service_id(manager_id, manager_name, msg))

def add_manager_service_id(manager_id, manager_name, message):
    chat_id = message.chat.id
    manager_phone = message.text
    msg = bot.send_message(chat_id, "Введіть ID сервіса для менеджера:")
    bot.register_next_step_handler(msg, lambda msg: save_manager(manager_id, manager_name, manager_phone, msg))

def save_manager(manager_id, manager_name, manager_phone, message):
    chat_id = message.chat.id
    comp_service_id_service = message.text
    try:
        cursor = db.cursor()
        cursor.execute("INSERT INTO manager (id_manager, name, phone, comp_service_id_service) VALUES (%s, %s, %s, %s)",
                       (manager_id, manager_name, manager_phone, comp_service_id_service))
        db.commit()
        cursor.close()
        bot.send_message(chat_id, f"Менеджер '{manager_name}' успішно додан в сервіс {comp_service_id_service}.")
    except mysql.connector.Error as err:
        bot.send_message(chat_id, f"Помилка при додаванню менеджера: {err}")


@bot.message_handler(func=lambda message: message.text == 'Додати інженера')
def add_engineer(message):
    cursor = db.cursor()
    cursor.execute("SELECT id_service, name_service FROM comp_service")
    services = cursor.fetchall()
    cursor.close()
    
    services_info = "\n".join([f"ID: {service[0]}, Назва: {service[1]}" for service in services])
    bot.send_message(message.chat.id, f"Існуючі сервіси:\n{services_info}")
    
    cursor = db.cursor()
    cursor.execute("SELECT id_enganer, name, comp_service_id_service FROM service_enganer")
    engineers = cursor.fetchall()
    cursor.close()

    engineers_info = "\n".join([f"ID: {engineer[0]}, Ім'я: {engineer[1]}, ID сервіса: {engineer[2]}" for engineer in engineers])
    bot.send_message(message.chat.id, f"Існуючі інженери:\n{engineers_info}")

    msg = bot.send_message(message.chat.id, "Введіть нове ID інженера:")
    bot.register_next_step_handler(msg, add_engineer_name)

def add_engineer_name(message):
    chat_id = message.chat.id
    engineer_id = message.text
    msg = bot.send_message(chat_id, "Введіть ім'я інженера:")
    bot.register_next_step_handler(msg, lambda msg: add_engineer_phone(engineer_id, msg))

def add_engineer_phone(engineer_id, message):
    chat_id = message.chat.id
    engineer_name = message.text
    msg = bot.send_message(chat_id, "Введіть номер телефона інженера:")
    bot.register_next_step_handler(msg, lambda msg: add_engineer_specialization(engineer_id, engineer_name, msg))

def add_engineer_specialization(engineer_id, engineer_name, message):
    chat_id = message.chat.id
    engineer_phone = message.text
    msg = bot.send_message(chat_id, "Введіть спеціалізацію інженера:")
    bot.register_next_step_handler(msg, lambda msg: add_engineer_service_id(engineer_id, engineer_name, engineer_phone, msg))

def add_engineer_service_id(engineer_id, engineer_name, engineer_phone, message):
    chat_id = message.chat.id
    specialization = message.text
    msg = bot.send_message(chat_id, "Введіть ID сервіса інженера:")
    bot.register_next_step_handler(msg, lambda msg: save_engineer(engineer_id, engineer_name, engineer_phone, specialization, msg))

def save_engineer(engineer_id, engineer_name, engineer_phone, specialization, message):
    chat_id = message.chat.id
    comp_service_id_service = message.text
    try:
        cursor = db.cursor()
        cursor.execute("INSERT INTO service_enganer (id_enganer, name, phone, specialization, comp_service_id_service) VALUES (%s, %s, %s, %s, %s)",
                       (engineer_id, engineer_name, engineer_phone, specialization, comp_service_id_service))
        db.commit()
        cursor.close()
        bot.send_message(chat_id, f"Інженер '{engineer_name}' успішно додан в сервіс {comp_service_id_service}.")
    except mysql.connector.Error as err:
        bot.send_message(chat_id, f"Помилка при додаванні інженера: {err}")

# Обработчик для действия "Удалить сервис"
@bot.message_handler(func=lambda message: message.text == 'Видалити сервіс')
def ask_service_id_to_delete(message):
    try:
        cursor = db.cursor()
        cursor.execute("SELECT id_service, name_service FROM comp_service")
        services = cursor.fetchall()
        cursor.close()

        if not services:
            bot.send_message(message.chat.id, "Нема доступних сервісів для видалення.")
            return

        # Відправляємо список сервісів для вибору
        text = "Введіть ID для видалення сервісу:\n"
        for service in services:
            text += f"{service[0]}: {service[1]}\n"
        bot.send_message(message.chat.id, text)
        bot.register_next_step_handler(message, delete_service)
    except mysql.connector.Error as err:
        bot.send_message(message.chat.id, f"Помилка при отриманні списку сервісів: {err}")

def delete_service(message):
    selected_service_id = message.text
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM comp_service WHERE id_service = %s", (selected_service_id,))
        service = cursor.fetchone()

        if not service:
            bot.send_message(message.chat.id, f"Сервіс з ID {selected_service_id} не знайдено.")
            return

        cursor.execute("DELETE FROM comp_service WHERE id_service = %s", (selected_service_id,))
        db.commit()
        cursor.close()
        bot.send_message(message.chat.id, f"Сервіс з ID {selected_service_id} успішно видалено.")
    except mysql.connector.Error as err:
        bot.send_message(message.chat.id, f"Помилка при видаленні сервісу: {err}")

# Обробник для дії "Видалити менеджера"
@bot.message_handler(func=lambda message: message.text == 'Видалити менеджера')
def ask_manager_id_to_delete(message):
    try:
        cursor = db.cursor()
        cursor.execute("SELECT id_manager, name FROM manager")
        managers = cursor.fetchall()
        cursor.close()

        if not managers:
            bot.send_message(message.chat.id, "Нема доступних менеджерів для видалення.")
            return

        # Відправляємо список менеджерів для вибору
        text = "Виберіть менеджера для видалення:\n"
        for manager in managers:
            text += f"{manager[0]}: {manager[1]}\n"
        bot.send_message(message.chat.id, text)
        bot.register_next_step_handler(message, delete_manager)
    except mysql.connector.Error as err:
        bot.send_message(message.chat.id, f"Помилка при отриманні списку менеджерів: {err}")

def delete_manager(message):
    selected_manager_id = message.text
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM manager WHERE id_manager = %s", (selected_manager_id,))
        manager = cursor.fetchone()

        if not manager:
            bot.send_message(message.chat.id, f"Менеджер з ID {selected_manager_id} не знайдено.")
            return

        cursor.execute("DELETE FROM manager WHERE id_manager = %s", (selected_manager_id,))
        db.commit()
        cursor.close()
        bot.send_message(message.chat.id, f"Менеджера з ID {selected_manager_id} успішно видалено.")
    except mysql.connector.Error as err:
        bot.send_message(message.chat.id, f"Помилка при видаленні менеджера: {err}")

# Обробник для дії "Видалити інженера"
@bot.message_handler(func=lambda message: message.text == 'Видалити інженера')
def ask_engineer_id_to_delete(message):
    try:
        cursor = db.cursor()
        cursor.execute("SELECT id_enganer, name FROM service_enganer")
        engineers = cursor.fetchall()
        cursor.close()

        if not engineers:
            bot.send_message(message.chat.id, "Нема доступних інженерів для видалення.")
            return

        # Відправляємо список інженерів для вибору
        text = "Виберіть інженера для видалення:\n"
        for engineer in engineers:
            text += f"{engineer[0]}: {engineer[1]}\n"
        bot.send_message(message.chat.id, text)
        bot.register_next_step_handler(message, delete_engineer)
    except mysql.connector.Error as err:
        bot.send_message(message.chat.id, f"Помилка при отриманні списку інженерів: {err}")

def delete_engineer(message):
    selected_engineer_id = message.text
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM service_enganer WHERE id_enganer = %s", (selected_engineer_id,))
        engineer = cursor.fetchone()

        if not engineer:
            bot.send_message(message.chat.id, f"Інженер з ID {selected_engineer_id} не знайдено.")
            return

        cursor.execute("DELETE FROM service_enganer WHERE id_enganer = %s", (selected_engineer_id,))
        db.commit()
        cursor.close()
        bot.send_message(message.chat.id, f"Інженера з ID {selected_engineer_id} успішно видалено.")
    except mysql.connector.Error as err:
        bot.send_message(message.chat.id, f"Помилка при видаленні інженера: {err}")
        
bot.polling(none_stop=True)