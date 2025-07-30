import os
import json
import datetime
import nest_asyncio

from telegram import Bot
from telegram.error import TelegramError

import asyncio
import textwrap
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from utils_hj3415 import setup_logger


mylogger = setup_logger(__name__, 'INFO')

nest_asyncio.apply()


def mail_to(title: str, text: str, to_mail:str) -> bool:
    from_mail = os.getenv("GMAIL_USER")
    app_pass = os.getenv("GMAIL_APP_PASS")

    mylogger.info(f'from: {from_mail}')
    mylogger.info(f'app_password: {app_pass}')

    if not from_mail or not app_pass:
        mylogger.error('GMAIL_USER or GMAIL_APP_PASS is not set.')
        return False

    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    msg = MIMEMultipart()
    msg['From'] = from_mail
    msg['Subject'] = title
    msg['To'] = to_mail
    current_time_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    msg.attach(MIMEText(f"{current_time_str}\n{text}"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(from_mail, app_pass)
            smtp.sendmail(from_mail, to_mail, msg.as_string())
        mylogger.info(f'Email sent from {from_mail} to {to_mail} successfully.')
        return True
    except smtplib.SMTPAuthenticationError as auth_err:
        mylogger.error(f'SMTP Authentication failed: {auth_err}')
    except smtplib.SMTPException as smtp_err:
        mylogger.error(f'SMTP error occurred: {smtp_err}')
    except Exception as e:
        mylogger.error(f'Unexpected error occurred while sending email: {e}')

    return False



async def send_message(bot: Bot, chat_id: str, text: str):
    """Telegram 메시지 전송 (비동기)"""
    try:
        await bot.send_message(chat_id=chat_id, text=text)
        mylogger.info(f"Message sent successfully: {text}")
    except TelegramError as e:
        mylogger.error(f"Failed to send message via Telegram: {e}")


def parse_telegram_tokens() -> dict:
    """환경변수에서 Telegram 봇 토큰 JSON을 변환"""
    try:
        return json.loads(os.getenv("TELEGRAM_BOT_TOKENS"))
    except json.JSONDecodeError as e:
        mylogger.error(f"Error decoding Telegram token JSON: {e}")
        return {}


def telegram_to(botname: str, text: str):
    """Telegram 메시지 전송"""
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    bot_dict = parse_telegram_tokens()

    if not chat_id or not bot_dict:
        mylogger.error('TELEGRAM_CHAT_ID or TELEGRAM_BOT_TOKENS is not set.')
        return

    # 봇 이름 확인 및 전송
    if botname not in bot_dict:
        mylogger.error(f'Invalid bot name: {botname}. Available: {list(bot_dict.keys())}')
        return

    bot = Bot(token=bot_dict[botname])

    try:
        asyncio.run(send_message(bot, chat_id, textwrap.dedent(text)))
    except RuntimeError as e:
        mylogger.error(f"Failed to send message due to event loop issue: {e}")