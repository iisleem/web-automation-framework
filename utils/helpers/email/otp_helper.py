from __future__ import annotations

from utils.helpers.email.base_email_client import BaseEmailClient
from utils.helpers.text.extractors import DEFAULT_OTP_REGEX, extract_otp
from utils.helpers.wait.polling import wait_until


class EmailOtpHelper:
    def __init__(
        self,
        email_client: BaseEmailClient,
        mailbox: str = "INBOX",
        default_regex: str = DEFAULT_OTP_REGEX,
    ) -> None:
        self.email_client = email_client
        self.mailbox = mailbox
        self.default_regex = default_regex

    def get_latest_otp(
        self,
        sender: str | None = None,
        subject_contains: str | None = None,
        regex: str | None = None,
        unseen_only: bool = False,
    ) -> str | None:
        message = self.email_client.find_latest_email(
            sender=sender,
            subject_contains=subject_contains,
            mailbox=self.mailbox,
            unseen_only=unseen_only,
        )
        if not message:
            return None
        return extract_otp(message.body, regex or self.default_regex)

    def wait_for_otp(
        self,
        sender: str | None = None,
        subject_contains: str | None = None,
        regex: str | None = None,
        timeout_seconds: float = 60,
        interval_seconds: float = 5,
        unseen_only: bool = False,
    ) -> str:
        return wait_until(
            lambda: self.get_latest_otp(
                sender=sender,
                subject_contains=subject_contains,
                regex=regex,
                unseen_only=unseen_only,
            ),
            timeout_seconds=timeout_seconds,
            interval_seconds=interval_seconds,
            failure_message=(
                "OTP email was not found. "
                f"sender={sender!r}, subject_contains={subject_contains!r}"
            ),
        )
