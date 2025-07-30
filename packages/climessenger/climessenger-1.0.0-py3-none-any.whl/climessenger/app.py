import logging
import sys
from datetime import datetime
import json
import requests
import urllib3
from flask import Flask, request
from threading import Thread
from pathlib import Path
from climessenger.certgen import generate_cert

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
base_dir = Path(__file__).resolve().parent.parent
cfg_path = base_dir / 'climessenger_config.json'

def create_default_config():
    """Создает конфиг по умолчанию, если он не существует"""
    default_config = {
        "cert_file": "climessenger_cert.pem",
        "key_file": "climessenger_key.pem",
        "listen_port": 8864
    }
    with open(cfg_path, 'w') as f:
        json.dump(default_config, f, indent=4)
    return default_config

def load_config():
    """Загружает конфиг или создает новый, если его нет"""
    if not cfg_path.exists():
        return create_default_config()
    with open(cfg_path) as f:
        return json.load(f)

def ensure_certificates_exist(cert_path, key_path):
    """Проверяет наличие сертификатов и генерирует их при необходимости"""
    if not cert_path.exists() or not key_path.exists():
        print("Generating SSL certificates...")
        generate_cert(str(cert_path), str(key_path))
        print(f"Certificates generated: {cert_path}, {key_path}")

@app.route('/message', methods=['POST'])
def receive_message():
    message = request.data.decode('utf-8')
    print(f"{(datetime.now()).strftime('%d.%m.%Y, %H:%M')}. New message from {request.remote_addr}: {message}")
    return "OK"

def send_message(ip, message, config):
    """Отправка сообщения с использованием конфига"""
    def _send():
        url = f"https://{ip}:{config['listen_port']}/message"
        try:
            response = requests.post(
                url,
                data=message.encode('utf-8'),
                verify=False,
                timeout=5
            )
            print(f"Server responded: {response.text}")
        except Exception as e:
            print(f"Failed to send message: {e}")
    Thread(target=_send).start()

def main():
    # Загружаем конфиг
    cfg = load_config()
    
    # Полные пути к файлам сертификатов
    cert_path = base_dir / cfg["cert_file"]
    key_path = base_dir / cfg["key_file"]
    
    # Убедимся, что сертификаты существуют
    ensure_certificates_exist(cert_path, key_path)

    if len(sys.argv) < 2:
        print("Usage:")
        print("  climessenger receive")
        print("  climessenger send <ip> <message>")
        return

    command = sys.argv[1]
    if command == 'receive':
        port = cfg.get("listen_port", 8864)
        print(f"Listening on https://0.0.0.0:{port} (multithreaded)")
        app.run(
            debug=False,
            host='0.0.0.0',
            port=port,
            ssl_context=(str(cert_path), str(key_path)),
            threaded=True
        )
    elif command == 'send':
        if len(sys.argv) < 4:
            print("Usage: climessenger send <ip> <message>")
            return
        ip = sys.argv[2]
        message = sys.argv[3]
        send_message(ip, message, cfg)  # Передаем конфиг в функцию
    else:
        print("Unknown command. Use 'receive' or 'send'")
