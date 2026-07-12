import pytest

from utils.helpers.email.base_email_client import BaseEmailClient, EmailMessage
from utils.helpers.email.otp_helper import EmailOtpHelper


pytestmark = pytest.mark.helpers


class FakeEmailClient(BaseEmailClient):
    def __init__(self, messages: list[EmailMessage | None]) -> None:
        self.messages = messages
        self.calls: list[dict] = []

    def find_latest_email(
        self,
        sender: str | None = None,
        subject_contains: str | None = None,
        mailbox: str = "INBOX",
        unseen_only: bool = False,
    ) -> EmailMessage | None:
        self.calls.append(
            {
                "sender": sender,
                "subject_contains": subject_contains,
                "mailbox": mailbox,
                "unseen_only": unseen_only,
            }
        )
        if not self.messages:
            return None
        return self.messages.pop(0)


def test_get_latest_otp_returns_code_from_matching_email():
    client = FakeEmailClient(
        [
            EmailMessage(
                subject="Login Code",
                sender="security@example.com",
                body="Your verification code is 482913.",
            )
        ]
    )
    helper = EmailOtpHelper(client, mailbox="QA")

    otp = helper.get_latest_otp(
        sender="security@example.com",
        subject_contains="Login Code",
    )

    assert otp == "482913"
    assert client.calls[0]["mailbox"] == "QA"


def test_get_latest_otp_returns_none_when_email_not_found():
    helper = EmailOtpHelper(FakeEmailClient([]))

    assert helper.get_latest_otp(sender="missing@example.com") is None


def test_get_latest_otp_supports_custom_regex():
    client = FakeEmailClient(
        [
            EmailMessage(
                subject="Login Code",
                sender="security@example.com",
                body="Use code AB-4829 to continue.",
            )
        ]
    )
    helper = EmailOtpHelper(client)

    assert helper.get_latest_otp(regex=r"AB-\d{4}") == "AB-4829"


def test_wait_for_otp_polls_until_code_arrives():
    client = FakeEmailClient(
        [
            None,
            EmailMessage(
                subject="Login Code",
                sender="security@example.com",
                body="Your code is 738291",
            ),
        ]
    )
    helper = EmailOtpHelper(client)

    otp = helper.wait_for_otp(
        sender="security@example.com",
        subject_contains="Login Code",
        timeout_seconds=1,
        interval_seconds=0.01,
    )

    assert otp == "738291"
    assert len(client.calls) == 2
