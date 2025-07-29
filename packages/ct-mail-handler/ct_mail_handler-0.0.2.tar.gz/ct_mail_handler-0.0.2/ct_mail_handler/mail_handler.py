import logging
import requests

from dataclasses import asdict
from typing import List, Optional

from .models import Attachment, MailDetail


class CredentiMailHandler(logging.Handler):
    def __init__(self, fromaddr, toaddrs, subject, mail_server_url,secure=None, timeout=5.0):
        logging.Handler.__init__(self)
        self.fromaddr = fromaddr
        if isinstance(toaddrs, str):
            toaddrs = [toaddrs]
        self.toaddrs = toaddrs
        self.subject = subject
        self.mail_server_url = mail_server_url
        self.secure = secure
        self.timeout = timeout
        
    def getSubject(self, record):
        return self.subject

    def emit(self, record):
        """
        Emit a log record
        Perform a POST request with the log record data transformed to a MailDetail object to the configured mail server
        """
        try:
            content = self.format(record)
            mail = CredentiMailHandler.prepare_email(self.fromaddr, self.toaddrs, self.getSubject(record), content)
            response = CredentiMailHandler.send_email(mail, self.mail_server_url)
            if not response.ok:
                self.handleError(record)
        except Exception:
            self.handleError(record)

    @staticmethod
    def prepare_email(from_address: str, to_address: List[str], subject: str, body: str, attachments: Optional[List[Attachment]] =None) -> MailDetail:
        return MailDetail(from_address=from_address, to_address=to_address, subject=subject, body=body, attachments=attachments)

    @staticmethod
    def send_email(message: MailDetail, mail_server_url:str, request_id: Optional[str] = None) -> requests.Response:
        """
        Send an email object to a mail server using the POST method, and returns the response.
        Requires a mail server to be configured.
        Args:
            message (MailDetail): MailDetail dataclass
            mail_server_url (str): Mail server url, POST method is called
            request_id (Optional[str], optional): Request id. Defaults to None.

        Returns:
            requests.Response: [description]
        """
        headers = {"Content-Type": "application/json"}
        if request_id:
            headers["X-Request-ID"] = request_id
        response = requests.post(
            mail_server_url,
            headers=headers,
            json=asdict(message),
        )
        return response