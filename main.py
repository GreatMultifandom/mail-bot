from telebot import TeleBot
from db import Database
from config import mongo_url, token
import re
from subprocess import Popen

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9]+@gmf\.org\.ua$'
    match = re.match(pattern, email)
    return match is not None

db = Database(mongo_url)
bot = TeleBot(token)

@bot.message_handler(commands=["start"])
def init_handler(m):
    user, status = db.process_user(m.from_user.id)
    if status == 2:
        bot.reply_to(m, f"Hi, {user['email']}"+'\n\n/password 1234 - set password\n<a href="https://gmf.org.ua/c">Rainloop</a> - your email client', parse_mode='HTML')
        return
    elif status == 1:
        bot.reply_to(m, 'Send your desired email to me! It should be like "username@gmf.org.ua"')
        return
    elif status == 0:
        bot.reply_to(m, 'Hi, welcome to GMF Mail! Send your desired email to me! It should be like "username@gmf.org.ua"')

@bot.message_handler(commands=["password"])
def init_handler(m):
    user, status = db.process_user(m.from_user.id)
    if status == 1:
        bot.reply_to(m, 'Send your email first! It should be like "username@gmf.org.ua"')
        return 
    if not m.text.count(' '):
        bot.reply_to(m, 'You should set your password like this: /password yourPassword. No spaces allowed in the password.')
        return
    username = user['email'].split('@')[0]
    password = m.text.split(' ')[1]
    if not (8 <= len(password) <= 30) or not password.isalnum():
        bot.reply_to(m, 'Password must be between 8 and 30, and contain only letters and numbers.')
        return
    process = Popen(args=f"bash_-c_docker-compose exec admin flask mailu user {username} gmf.org.ua '{password}'".split("_"),
                    cwd='/home/gmf/mailu')
    bot.reply_to(m, 'Password set! Press /start for the main menu.')

@bot.message_handler()
def init_handler(m):
    user, status = db.process_user(m.from_user.id)
    if status == 2:
        bot.reply_to(m, f"Hi, {user['email']}"+'\n\n/password - set password\n<a href="https://gmf.org.ua/c">Rainloop</a> - your email client', parse_mode='HTML')
        return
    if not is_valid_email(m.text):
        bot.reply_to(m, 'This does not look like valid email. Try again!')
        return
    db.set_email(m.from_user.id, m.text)
    bot.reply_to(m, 'Email saved! Now set your FIRST password with /password command, otherwise you wont be able to use it.\n\nDO NOT use this command second time, change your password ONLINE. This command WONT work second time.')    

bot.infinity_polling()