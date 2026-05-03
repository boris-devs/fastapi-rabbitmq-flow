from abc import ABC, abstractmethod
from email.message import EmailMessage

import aiosmtplib


class EmailSenderInterface(ABC):
	@abstractmethod
	async def send_registration_email(self, to: str, content: str):
		pass


class EmailSender(EmailSenderInterface):
	"""
	Handles sending of emails through an SMTP server.

	This class facilitates sending emails by using an SMTP server. It supports
	secure email delivery with TLS encryption. Primarily, it provides functionality
	to send pre-formatted registration emails, ensuring a streamlined registration
	process for users.

	:ivar _hostname: The hostname of the SMTP server, like 'smtp.gmail.com'.
	:type _hostname: Str
	:ivar _port: The port to be used for connecting to the SMTP server.
	:type _port: Int
	:ivar _username: The username for authenticating with the SMTP server.
	:type _username: Str
	:ivar _password: The password for authenticating with the SMTP server.
	:type _password: Str
	"""
	def __init__(self, hostname: str, port: int, username: str, password: str):
		self._hostname = hostname
		self._port = port
		self._username = username
		self._password = password

	async def _send_email(self, to: str, subject: str, content: str):
		smtp_client = aiosmtplib.SMTP(hostname=self._hostname, port=self._port, use_tls=True)
		async with smtp_client:
			await smtp_client.login(self._username, self._password)
			message = EmailMessage()
			message['Subject'] = subject
			message['From'] = self._username
			message['To'] = to
			message.set_content(content)
			await smtp_client.send_message(message)

	async def send_registration_email(self, to: str, content: str):
		subject = "Successfully Registration. Welcome to our platform!"
		await self._send_email(to, subject, content)
