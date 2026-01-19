import socket

def can_reach_google_stt(timeout: float = 1.5) -> bool:
    # Проверяем именно доступность endpoint'а STT, а не абстрактный "интернет"
    try:
        with socket.create_connection(("speech.googleapis.com", 443), timeout=timeout):
            return True
    except OSError:
        return False
