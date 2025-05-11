import smtplib
from email.message import EmailMessage

def send_email(email: str, login: str) -> None:
    msg = EmailMessage()
    msg["Subject"] = f"{login}, Спасибо за ваш тикет!"
    msg["From"] = "xrinde8@gmail.com"
    msg["To"] = email
    msg.set_content(f"{login}, тикет успешно обработан. Спасибо что связались с нами")
    with smtplib.SMTP_SSL("smtp.yandex.ru", 465) as server:
        server.login("pythonyandex", "apwkujanhczpshgn")
        server.send_message(msg)