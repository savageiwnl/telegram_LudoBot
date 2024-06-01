import telebot
from telebot import types
import re
import random


api_token = 'ur api token'
bot = telebot.TeleBot(api_token)

# Функция для чтения данных о командах из файла
def read_teams_info_from_file(filename):
    teams_info = {}
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            match = re.search(r"'name': '([^']*)', 'points': '([^']*)'", line)
            if match:
                team_name = match.group(1)
                team_points = match.group(2)
                teams_info[team_name.lower()] = {'name': team_name, 'points': team_points}
    return teams_info

# Проверка содержимого teams_info
teams_info = read_teams_info_from_file('teams_info.txt')

# Функция для создания клавиатуры с командами
def create_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ['/help', '/hello', '/match', '/teams', '/link']
    for button in buttons:
        keyboard.add(types.KeyboardButton(button))
    return keyboard

# Функция для отправки приветственного сообщения с клавиатурой
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = "Добро пожаловать! Выберите команду:"
    bot.send_message(message.chat.id, welcome_text, reply_markup=create_keyboard())

# Функция для отправки ссылки на создателя
def write_link(message):
    text = "Ты хочешь узнать моего создателя?"
    keyboard = types.InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')
    keyboard.add(key_yes)
    key_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
    keyboard.add(key_no)
    bot.send_message(message.chat.id, text=text, reply_markup=keyboard)

# Функция для обработки команды /help
@bot.message_handler(commands=['help'])
def send_help(message):
    COMMANDS = ['help', 'hello', 'match', 'teams', 'link']  # Список доступных команд
    bot.send_message(message.chat.id, 'Существующие команды: /' + ', /'.join(COMMANDS))

# Функция для обработки команды /hello
@bot.message_handler(commands=['hello'])
def say_hello(message):
    bot.send_message(message.chat.id, f"Привет, {message.from_user.first_name}!")

# Функция для обработки команды /teams
@bot.message_handler(commands=['teams'])
def list_teams(message):
    teams_info = read_teams_info_from_file('teams_info.txt')
    teams_list = [team_info['name'] for team_info in teams_info.values()]
    response = "Доступные команды:\n" + "\n".join(teams_list)
    bot.send_message(message.chat.id, response)

# Функция для обработки команды /match
@bot.message_handler(commands=['match'])
def match_winner(message):
    # Пример чтения данных из файла
    teams_info = read_teams_info_from_file('teams_info.txt')

    # Получаем команды из сообщения, используя кавычки для разделения названий
    text = message.text
    pattern = r'"([^"]+)"'
    teams = re.findall(pattern, text)

    # Проверяем, что введено две команды
    if len(teams) != 2:
        bot.send_message(message.chat.id, 'Введите две команды для сравнения в формате /match "Team One" "Team Two".')
        return

    # Проверяем, что обе команды присутствуют в данных
    for team in teams:
        if team.lower() not in teams_info:
            bot.send_message(message.chat.id, f'Команда "{team}" не найдена в данных.')
            return

    # Получаем информацию о каждой команде
    team1_info = teams_info[teams[0].lower()]
    team2_info = teams_info[teams[1].lower()]

    # Определяем шансы на победу для каждой команды
    total_points = int(team1_info['points']) + int(team2_info['points'])
    team1_base_chance = (int(team1_info['points']) / total_points) * 100
    team2_base_chance = (int(team2_info['points']) / total_points) * 100

    # Добавляем элемент случайности
    randomness = random.uniform(-5, 5)
    team1_chance = team1_base_chance + randomness
    team2_chance = 100 - team1_chance

    # Обеспечиваем, что шансы остаются в пределах 0-100%
    if team1_chance < 0:
        team1_chance = 0
        team2_chance = 100
    elif team2_chance < 0:
        team2_chance = 0
        team1_chance = 100

    # Определяем победителя на основе шансов
    winner = teams[0] if random.uniform(0, 100) < team1_chance else teams[1]

    # Отправляем информацию о командах, их очках и победителе
    response = f'Сравнение команд:\n\n{team1_info["name"]} ({team1_info["points"]} очков)\n' \
               f'{team2_info["name"]} ({team2_info["points"]} очков)\n\n' \
               f'Шансы на победу:\n\n{team1_info["name"]}: {team1_chance:.2f}%\n' \
               f'{team2_info["name"]}: {team2_chance:.2f}%\n\n' \
               f'Победитель: {winner}'
    bot.send_message(message.chat.id, response)

# Функция для обработки нажатия кнопок в инлайн-клавиатуре
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "yes":
        bot.send_message(call.message.chat.id, 'Мой создатель - @thegreatsene4ka - самый классный человек в мире')
    elif call.data == "no":
        bot.send_message(call.message.chat.id, 'Жаль, что ты не хочешь это узнать')

# Функция для обработки входящих сообщений
@bot.message_handler(func=lambda message: message.text.startswith('/'))
def handle_messages(message):
    if message.text == "/link":
        write_link(message)
    elif message.text == "/help":
        send_help(message)
    elif message.text == "/hello":
        say_hello(message)
    elif message.text.lower().startswith("/match"):
        match_winner(message)
    elif message.text == "/teams":
        list_teams(message)
    else:
        bot.send_message(message.chat.id, 'Я тебя не понимаю, лудоман. Напиши /help')

# Запускаем бота
bot.polling(none_stop=True)