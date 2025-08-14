"""
Keep the Flask server running for Replit public access
"""
from threading import Thread
from flask import Flask
import requests
import time
import os

def keep_alive():
    """
    Función para mantener el servidor activo enviando pings periódicos
    """
    app = Flask('')
    
    @app.route('/')
    def home():
        return "Panel L3HO - Servidor activo", 200
    
    @app.route('/health')
    def health():
        return {"status": "active", "message": "API Liga MX funcionando"}, 200
    
    def run():
        app.run(host='0.0.0.0', port=8080)
    
    def ping_self():
        """Ping periódico para mantener el servidor activo"""
        while True:
            try:
                # Ping al servidor principal
                requests.get("http://localhost:5000/", timeout=10)
                print("✅ Ping exitoso al servidor principal")
            except Exception as e:
                print(f"⚠️ Ping fallido: {e}")
            time.sleep(300)  # Ping cada 5 minutos
    
    server = Thread(target=run)
    pinger = Thread(target=ping_self)
    
    server.daemon = True
    pinger.daemon = True
    
    server.start()
    pinger.start()

if __name__ == "__main__":
    keep_alive()