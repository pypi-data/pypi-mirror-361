import io
import re
import unittest

from http import HTTPStatus
from uuid import UUID, uuid4

from app import create_logger_and_app_with_middleware


class RequestIdLogMiddlewareTestCase(unittest.TestCase):
    def setUp(self):
        self.logger, self.app, self.client = create_logger_and_app_with_middleware(self.callback_mail)
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def callback_mail(self, data):
        self.assertEqual(data["from_address"], "test@tecnics")
        self.assertEqual(data["to_address"], ["test@tecnics"])
        self.assertEqual(data["subject"], "Test")
        self.assertEqual(data["body"], "TestLog")

    def test_mailing(self):
        self.logger.warning("TestLog")
