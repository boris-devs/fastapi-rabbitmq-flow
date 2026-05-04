import asyncio
import json

from src.notifications.emails import EmailSenderInterface, EmailSender
from src.config import settings
from .constants import USER_REGISTRATION_QUEUE
from .rabbitmq_manager import RabbitMQManagerInterface, RabbitMQManager

amqp_url = settings.RABBITMQ_AMQP_URL


class EmailSenderWorker:
	def __init__(self, rmq: RabbitMQManagerInterface, emails_sender: EmailSenderInterface):
		self.rmq = rmq
		self.emails_sender = emails_sender

	async def processing_message(self, body: bytes):
		message_body = json.loads(body.decode())
		new_user_email = message_body.get("email")
		if not new_user_email:
			print("No email found in message", message_body)
			return
		await self.emails_sender.send_registration_email(new_user_email, "Welcome to our platform!")

	async def send_email(self):
		await self.rmq.connect()
		await self.rmq.consume(USER_REGISTRATION_QUEUE, self.processing_message)


async def start_worker():
	print("Starting worker")
	rmq = RabbitMQManager(amqp_url)
	email_sender = EmailSender(hostname=settings.GMAIL_HOSTNAME,
	                           port=settings.GMAIL_PORT,
	                           username=settings.GMAIL_EMAIL,
	                           password=settings.GMAIL_PASSWORD)

	notification_worker = EmailSenderWorker(rmq, email_sender)

	try:
		await notification_worker.send_email()
	finally:
		await rmq.close()


if __name__ == "__main__":
	try:
		asyncio.run(start_worker())
	except KeyboardInterrupt:
		print("Shutting down worker")
