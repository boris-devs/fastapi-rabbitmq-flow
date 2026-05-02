from email.message import EmailMessage

import aiosmtplib


class EmailSender:
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
