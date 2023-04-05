import os
import telebot
import subprocess
import psutil

TOKEN = '5686085187:AAFsKj6p29_U4x_ITp3-rwWzY53GINKTLx0'
name_gpt_bot = "/bot/main.py"
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['next'])
def handle_next_command(message):
    # чтение первого токена из файла
    with open("token.txt", "r") as f:
        lines = f.readlines()
        if not lines:
            bot.reply_to(message, "Файл пуст.")
            return

        filename = "main.py"

        # ищем все запущенные процессы Python с заданным именем файла
        for process in psutil.process_iter():
            try:
                # получаем список аргументов командной строки, которыми был запущен процесс
                cmdline = process.cmdline()

                # если имя запущенного файла соответствует искомому имени
                if len(cmdline) > 1 and cmdline[1].endswith(filename):
                    # закрываем процесс
                    process.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        # запускаем новый процесс
        subprocess.Popen(["python3", f"bot/{filename}"])

        first_token = lines[0].strip()
        bot.reply_to(message, f'Бот перезапущен по токену: "{first_token}"')

        with open('.env', 'r') as f:
            text = f.readlines()
        for ind, vl in enumerate(text):
            if vl.__contains__('OPENAI_API_KEY'):
                text[ind] = f'OPENAI_API_KEY="{first_token}"\n'
                print(text[ind])
        with open('.env', 'w') as f:
            f.writelines(text)

    # удаление первого токена из файла
    with open("token.txt", "w") as f:
        f.writelines(lines[1:])


@bot.message_handler(commands=['add'])
def handle_add_command(message):
    # получение токенов после команды /add
    words = message.text.split()[1:]

    # запись слов в файл
    with open("token.txt", "a") as f:
        for word in words:
            f.write(word + "\n")

    # отправка подтверждения пользователю
    bot.reply_to(message, "Токены успешно добавлены.")


@bot.message_handler(content_types=['text'])
def get_command(message):
    bot.send_message(message.chat.id, f'Полученный API: {message.text}')
    with open('.env.example', 'r') as f:
        text = f.readlines()
    for ind, vl in enumerate(text):
        if vl.__contains__('OPENAI_API_KEY'):
            text[ind] = f'OPENAI_API_KEY="{message.text}"\n'
            print(text[ind])
    with open('.env.example', 'w') as f:
        f.writelines(text)





print('Bot started')
bot.polling(none_stop=True)