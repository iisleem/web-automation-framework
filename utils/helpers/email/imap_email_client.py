from __future__ import annotations

from datetime import datetime
from email import message_from_bytes
from email.message import Message
from email.utils import parsedate_to_datetime
import imaplib
import os

from utils.helpers.email.base_email_client import BaseEmailClient, EmailMessage


class ImapEmailClient(BaseEmailClient):
    def __init__(
        self,
        host: str,
        port: int = 993,
        username: str | None = None,
        password: str | None = None,
        username_env: str | None = None,
        password_env: str | None = None,
        use_ssl: bool = True,
    ) -> None:
        self.host = host
        self.port = port
        self.username = username or _get_env_value(username_env, "email username")
        self.password = password or _get_env_value(password_env, "email password")
        self.use_ssl = use_ssl

    @classmethod
    def from_config(cls, email_config: dict) -> "ImapEmailClient":
        return cls(
            host=email_config["host"],
            port=int(email_config.get("port", 993)),
            username=email_config.get("username"),
            password=email_config.get("password"),
            username_env=email_config.get("username_env"),
            password_env=email_config.get("password_env"),
            use_ssl=bool(email_config.get("use_ssl", True)),
        )

    def find_latest_email(
        self,
        sender: str | None = None,
        subject_contains: str | None = None,
        mailbox: str = "INBOX",
        unseen_only: bool = False,
    ) -> EmailMessage | None:
        with self._connect() as connection:
            connection.login(self.username, self.password)
            connection.select(mailbox)

            search_criteria = "UNSEEN" if unseen_only else "ALL"
            status, data = connection.search(None, search_criteria)
            if status != "OK" or not data or not data[0]:
                return None

            message_ids = data[0].split()
            for message_id in reversed(message_ids):
                status, payload = connection.fetch(message_id, "(RFC822)")
                if status != "OK" or not payload:
                    continue

                raw_message = payload[0][1]
                if not isinstance(raw_message, bytes):
                    continue

                parsed = message_from_bytes(raw_message)
                email_message = _to_email_message(parsed)
                if _matches(email_message, sender, subject_contains):
                    return email_message

        return None

    def _connect(self):
        if self.use_ssl:
            return imaplib.IMAP4_SSL(self.host, self.port)
        return imaplib.IMAP4(self.host, self.port)


def _get_env_value(env_name: str | None, label: str) -> str:
    if not env_name:
        raise ValueError(f"Missing {label}. Provide a value or environment variable name.")
    value = os.getenv(env_name)
    if not value:
        raise ValueError(f"Environment variable '{env_name}' is required for {label}.")
    return value


def _to_email_message(message: Message) -> EmailMessage:
    return EmailMessage(
        subject=str(message.get("Subject", "")),
        sender=str(message.get("From", "")),
        body=_extract_body(message),
        received_at=_parse_received_at(message),
    )


def _extract_body(message: Message) -> str:
    if message.is_multipart():
        parts: list[str] = []
        for part in message.walk():
            content_type = part.get_content_type()
            disposition = str(part.get("Content-Disposition", ""))
            if content_type in {"text/plain", "text/html"} and "attachment" not in disposition:
                payload = part.get_payload(decode=True)
                if payload:
                    parts.append(payload.decode(part.get_content_charset() or "utf-8", errors="ignore"))
        return "\n".join(parts)

    payload = message.get_payload(decode=True)
    if not payload:
        return str(message.get_payload())
    return payload.decode(message.get_content_charset() or "utf-8", errors="ignore")


def _parse_received_at(message: Message) -> datetime | None:
    date_header = message.get("Date")
    if not date_header:
        return None
    try:
        return parsedate_to_datetime(date_header)
    except (TypeError, ValueError):
        return None


def _matches(
    message: EmailMessage,
    sender: str | None,
    subject_contains: str | None,
) -> bool:
    sender_matches = not sender or sender.lower() in message.sender.lower()
    subject_matches = not subject_contains or subject_contains.lower() in message.subject.lower()
    return sender_matches and subject_matches
