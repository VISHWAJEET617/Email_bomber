import telebot
import requests
import random
import string
import time
import threading
import os
from collections import deque
from datetime import datetime
from flask import Flask

BOT_TOKEN = os.environ.get('BOT_TOKEN', '')

app = Flask(__name__)

@app.route('/')
def home():
    return 'Email Bomber Bot is alive on Render!'

def run_flask():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False, threaded=True)

threading.Thread(target=run_flask, daemon=True).start()
time.sleep(2)

bot = telebot.TeleBot(BOT_TOKEN)
bomb_lock = threading.Lock()
current_operation = None
queue = deque()
user_data = {}
NL = chr(10)
P = '[EmailBomber] '

DOMAINS = [
    'sharklasers.com',
    'grr.la',
    'guerrillamail.com',
    'guerrillamail.de',
    'guerrillamail.net',
    'guerrillamail.org',
    'guerrillamail.biz'
]

def rand_email():
    u = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    return u + '@' + random.choice(DOMAINS)

def rand_subject():
    prefixes = ['Signal', 'Drop', 'Echo', 'Void', 'Pulse', 'Noise']
    return random.choice(prefixes) + ' #' + str(random.randint(1000, 9999))

def rand_body():
    templates = [
        'Random transmission received. No origin detected.',
        'Pointless data packet delivered to inbox.',
        'Clutter level increased by one unit.',
        'Null message arrived for no reason.',
        'Entropy injection complete.'
    ]
    filler = ''.join(random.choices(string.ascii_letters + string.digits + ' .,!?', k=random.randint(30, 80)))
    return random.choice(templates) + ' ' + filler

def send_email(to, subject, body):
    try:
        s = requests.Session()
        r = s.get('https://api.guerrillamail.com/ajax.php?f=get_email_address', timeout=10)
        sid = r.json().get('sid_token')
        if not sid:
            return False
        payload = {
            'f': 'send_email',
            'sid_token': sid,
            'to': to,
            'from': rand_email(),
            'subject': subject,
            'body': body
        }
        res = s.post('https://api.guerrillamail.com/ajax.php', data=payload, timeout=10)
        return res.json().get('status') == 'sent'
    except Exception as e:
        print('send_email error: ' + str(e))
        return False

def run_bomb():
    global current_operation
    op = current_operation
    cid = op['chat_id']
    uid = op['user_id']
    sent = 0
    consecutive_fails = 0
    t0 = datetime.now()
    msg = P + 'Operation started!' + NL + 'Target: ' + op['target'] + NL + 'Messages: ' + str(op['count']) + NL + 'Delay: ' + str(op['interval']) + 's'
    bot.send_message(cid, msg)
    for i in range(op['count']):
        if current_operation is None or current_operation['user_id'] != uid:
            break
        ok = send_email(op['target'], rand_subject(), rand_body())
        if ok:
            sent += 1
            consecutive_fails = 0
        else:
            consecutive_fails += 1
        if consecutive_fails >= 3:
            msg = P + 'Service restricted. Stopped early.' + NL + 'Sent: ' + str(sent) + '/' + str(op['count'])
            bot.send_message(cid, msg)
            break
        if (i + 1) % 5 == 0:
            elapsed = (datetime.now() - t0).total_seconds()
            if elapsed > 0:
                rate = (i + 1) / elapsed
                rem = op['count'] - (i + 1)
                eta = rem / rate if rate > 0 else rem * op['interval']
                em = int(eta // 60)
                es = int(eta % 60)
                msg = P + 'Progress: ' + str(sent) + '/' + str(op['count']) + ' sent' + NL + 'ETA: ' + str(em) + 'm ' + str(es) + 's remaining'
                bot.send_message(cid, msg)
        time.sleep(op['interval'])
    msg = P + 'Operation complete!' + NL + 'Messages sent: ' + str(sent) + '/' + str(op['count'])
    bot.send_message(cid, msg)
    current_operation = None
    if queue:
        nxt = queue.popleft()
        current_operation = nxt.copy()
        current_operation['sent'] = 0
        current_operation['start_time'] = datetime.now()
        threading.Thread(target=run_bomb).start()
        msg = P + 'Your turn has started!' + NL + 'Target: ' + nxt['target'] + NL + 'Messages: ' + str(nxt['count'])
        bot.send_message(nxt['chat_id'], msg)


@bot.message_handler(commands=['start'])
def cmd_start(message):
    msg = P + 'Welcome to Email Bomber Bot!' + NL
    msg += 'Sends random emails from disposable temp addresses.' + NL
    msg += 'Effective limit: ~20 to 50 messages per session.' + NL + NL
    msg += 'Type /help to see all commands.'
    bot.reply_to(message, msg)

@bot.message_handler(commands=['help'])
def cmd_help(message):
    msg = P + 'All Commands:' + NL
    msg += '/target <email>   - Set target email address' + NL
    msg += '/count <1-100>    - Number of messages to send' + NL
    msg += '/interval <3-30>  - Delay between messages in seconds' + NL
    msg += '/bomb             - Start the operation' + NL
    msg += '/status           - View your current settings' + NL
    msg += '/queue            - Check your position in queue' + NL
    msg += '/cancel           - Remove yourself from queue' + NL
    msg += '/stop             - Stop your active operation' + NL
    msg += '/reset            - Clear all your settings'
    bot.reply_to(message, msg)

@bot.message_handler(commands=['target'])
def cmd_target(message):
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            raise ValueError('missing email')
        email = parts[1].strip()
        if '@' not in email or '.' not in email.split('@')[-1]:
            bot.reply_to(message, P + 'Invalid email format.' + NL + 'Example: user@domain.com')
            return
        uid = message.from_user.id
        if uid not in user_data:
            user_data[uid] = {}
        user_data[uid]['target'] = email
        bot.reply_to(message, P + 'Target set: ' + email + NL + 'Next step: /count <number>')
    except Exception:
        bot.reply_to(message, P + 'Usage: /target email@example.com')

@bot.message_handler(commands=['count'])
def cmd_count(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            raise ValueError('missing number')
        n = int(parts[1])
        if not 1 <= n <= 100:
            raise ValueError('out of range')
        uid = message.from_user.id
        if uid not in user_data:
            user_data[uid] = {}
        user_data[uid]['count'] = n
        bot.reply_to(message, P + 'Message count set to: ' + str(n))
    except Exception:
        bot.reply_to(message, P + 'Usage: /count 20' + NL + 'Allowed range: 1 to 100')

@bot.message_handler(commands=['interval'])
def cmd_interval(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            raise ValueError('missing seconds')
        sec = int(parts[1])
        if not 3 <= sec <= 30:
            raise ValueError('out of range')
        uid = message.from_user.id
        if uid not in user_data:
            user_data[uid] = {}
        user_data[uid]['interval'] = sec
        bot.reply_to(message, P + 'Delay set to: ' + str(sec) + ' seconds')
    except Exception:
        bot.reply_to(message, P + 'Usage: /interval 5' + NL + 'Allowed range: 3 to 30 seconds')

@bot.message_handler(commands=['bomb'])
def cmd_bomb(message):
    uid = message.from_user.id
    if uid not in user_data or 'target' not in user_data[uid] or 'count' not in user_data[uid]:
        bot.reply_to(message, P + 'Please set /target and /count first.')
        return
    iv = user_data[uid].get('interval', 3)
    tg = user_data[uid]['target']
    ct = user_data[uid]['count']
    confirm_text = P + 'Confirm operation?' + NL
    confirm_text += 'Target: ' + tg + NL
    confirm_text += 'Count: ' + str(ct) + NL
    confirm_text += 'Delay: ' + str(iv) + 's' + NL + NL
    confirm_text += 'Reply YES to start.'
    msg = bot.reply_to(message, confirm_text)
    bot.register_next_step_handler(msg, lambda m: confirm_handler(m, uid, message.chat.id, tg, ct, iv))

def confirm_handler(message, uid, chat_id, target, count, interval):
    if message.text is None or message.text.strip().upper() != 'YES':
        bot.reply_to(message, P + 'Operation cancelled.')
        return
    global current_operation
    with bomb_lock:
        if current_operation:
            queue.append({'user_id': uid, 'target': target, 'count': count, 'interval': interval, 'chat_id': chat_id})
            pos = len(queue)
            msg = P + 'Added to queue!' + NL + 'Your position: ' + str(pos) + NL + 'Use /queue to check status.'
            bot.reply_to(message, msg)
        else:
            current_operation = {'user_id': uid, 'target': target, 'count': count, 'interval': interval, 'sent': 0, 'start_time': datetime.now(), 'chat_id': chat_id}
            threading.Thread(target=run_bomb).start()

@bot.message_handler(commands=['queue'])
def cmd_queue(message):
    uid = message.from_user.id
    if not queue:
        bot.reply_to(message, P + 'Queue is currently empty.')
        return
    pos = 1
    found = False
    for req in queue:
        if req['user_id'] == uid:
            found = True
            msg = P + 'Queue Status' + NL
            msg += 'Your position: ' + str(pos) + ' of ' + str(len(queue)) + NL
            msg += 'Target: ' + req['target'] + NL
            msg += 'Count: ' + str(req['count'])
            bot.reply_to(message, msg)
            break
        pos += 1
    if not found:
        bot.reply_to(message, P + 'You are not currently in the queue.')

@bot.message_handler(commands=['cancel'])
def cmd_cancel(message):
    global queue
    uid = message.from_user.id
    old_len = len(queue)
    queue = deque([r for r in queue if r['user_id'] != uid])
    if len(queue) < old_len:
        bot.reply_to(message, P + 'Successfully removed from queue.')
    else:
        bot.reply_to(message, P + 'You were not in the queue.')

@bot.message_handler(commands=['status'])
def cmd_status(message):
    uid = message.from_user.id
    if uid in user_data:
        d = user_data[uid]
        msg = P + 'Your Current Settings:' + NL
        msg += 'Target   : ' + str(d.get('target', 'not set')) + NL
        msg += 'Count    : ' + str(d.get('count', 'not set')) + NL
        msg += 'Interval : ' + str(d.get('interval', 3)) + ' seconds' + NL
        msg += 'Active op: ' + ('Yes' if current_operation else 'No') + NL
        msg += 'Queue    : ' + str(len(queue)) + ' waiting'
    else:
        msg = P + 'No settings configured yet.' + NL + 'Queue: ' + str(len(queue)) + ' waiting'
    bot.reply_to(message, msg)

@bot.message_handler(commands=['stop'])
def cmd_stop(message):
    global current_operation
    uid = message.from_user.id
    if current_operation and current_operation['user_id'] == uid:
        current_operation = None
        bot.reply_to(message, P + 'Your operation has been stopped.')
    else:
        bot.reply_to(message, P + 'No active operation found for you.')

@bot.message_handler(commands=['reset'])
def cmd_reset(message):
    uid = message.from_user.id
    if uid in user_data:
        del user_data[uid]
    bot.reply_to(message, P + 'All your settings have been cleared.')


print('Email Bomber Bot starting on Render...')
bot.infinity_polling(skip_pending=True, none_stop=True)
