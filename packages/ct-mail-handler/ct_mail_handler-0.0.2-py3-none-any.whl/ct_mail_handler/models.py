import mimetypes

from dataclasses import dataclass
from typing import List, Literal, Optional


@dataclass
class Attachment:
    file_content_b64: str
    file_name: Optional[str]
    file_type: Optional[str]
    disposition: Literal["attachment", "inline"] = "attachment"

    @classmethod
    def from_dict(cls, data: Optional[List[dict]]):
        if data is None:
            return None
        return [cls(**attachment) for attachment in data]

@dataclass
class MailDetail:
    from_address: str
    to_address: List[str]
    subject: str
    body: str
    attachments: Optional[List[Attachment]]

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            from_address=data["from_address"],
            to_address=data["to_address"],
            subject=data["subject"],
            body=data["body"],
            attachments=Attachment.from_dict(data["attachments"])
        )

    def add_attachment(self, file_content_b64: str, file_name: Optional[str] = None, file_type: Optional[str] = None, disposition: Literal["attachment", "inline"] = "attachment"):
        if self.attachments is None:
            self.attachments = []
        if file_name is None:
            if file_type is None:
                file_name = "attachment.txt"
            else:
                extension = mimetypes.guess_extension(file_type)
                if extension is None:
                    extension = ".txt"
                file_name = "attachment" + extension
        self.attachments.append(Attachment(file_content_b64=file_content_b64, file_name=file_name, file_type=file_type, disposition=disposition))