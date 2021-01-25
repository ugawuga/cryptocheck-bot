import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(addr_to, msg_subj, msg_text):
    addr_from = "block.tech@mail.ru"
    password = "qawsedqwerty"

    msg = MIMEMultipart()
    msg["From"] = addr_from
    msg["To"] = addr_to
    msg["Subject"] = msg_subj

    body = msg_text
    msg.attach(MIMEText(body, "plain"))

    server = smtplib.SMTP_SSL('smtp.mail.ru', 465)  # Создаем объект SMTP
    # server.starttls()                                  # Начинаем шифрованный обмен по TLS
    server.login(addr_from, password)  # Получаем доступ
    server.send_message(msg)  # Отправляем сообщение
    server.quit()


