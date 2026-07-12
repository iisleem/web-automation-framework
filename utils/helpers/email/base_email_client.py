from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class EmailMessage:
    subject: str
    sender: str
    body: str
    received_at: datetime | None = None


class BaseEmailClient(ABC):
    @abstractmethod
    def find_latest_email(
        self,
        sender: str | None = None,
        subject_contains: str | None = None,
        mailbox: str = "INBOX",
        unseen_only: bool = False,
    ) -> EmailMessage | None:
        raise NotImplementedError
