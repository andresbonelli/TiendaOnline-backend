__all__ = ["send_email"]

from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType
from fastapi.background import BackgroundTasks
from typing import List
from pathlib import Path

from .__base import APP_TITLE, MAIL_FROM, MAIL_PASSWORD, MAIL_PORT, MAIL_SERVER, MAIL_USERNAME

conf = ConnectionConfig(
    MAIL_USERNAME = MAIL_USERNAME,
    MAIL_PASSWORD = MAIL_PASSWORD,
    MAIL_PORT = MAIL_PORT,
    MAIL_SERVER = MAIL_SERVER,
    MAIL_FROM = MAIL_FROM,
    MAIL_FROM_NAME = APP_TITLE,
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    MAIL_DEBUG=True,
    USE_CREDENTIALS = True,
    TEMPLATE_FOLDER=Path(__file__).parent.parent.parent / "templates"
)

fm = FastMail(conf)

async def send_email(
    recipients: List,
    subject: str,
    context: dict,
    template_name: str,
    background_tasks: BackgroundTasks
    ):
    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        template_body=context,
        subtype=MessageType.html
    )
    
    background_tasks.add_task(fm.send_message, message, template_name=template_name)