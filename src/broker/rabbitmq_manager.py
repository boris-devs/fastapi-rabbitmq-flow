import json
from abc import ABC, abstractmethod
from typing import Callable

from fastapi import Request

import aio_pika

from .constants import USER_REGISTRATION_QUEUE


class RabbitMQManagerInterface(ABC):
	"""
	Interface for RabbitMQ management.

	This abstract base class defines the contract for interacting with a
	RabbitMQ message broker. The derived classes must implement all methods
	defined here to establish a connection, close the connection, publish
	messages to a queue, and consume messages from a queue.
	"""

	@abstractmethod
	async def connect(self):
		"""
		An abstract base method that establishes a connection. This method must
		be implemented by all subclasses to define the connection logic specific
		to the subclass's context.
		"""
		pass

	@abstractmethod
	async def close(self):
		"""
		Represents an abstract method that must be implemented to handle the closing of a resource or
		connection. This method is intended to be asynchronous, meaning it should utilize an `async`
		context to perform any necessary operations.

		"""
		pass

	@abstractmethod
	async def publish(self, queue_name: str, message: dict):
		"""
		Publishes a message to the specified queue.

		This method serves as an abstract definition for publishing a message to a
		queue. The implementation of this method should handle the specifics of message
		publishing, such as serialization, queue communication, and error handling.

		:param queue_name: Name of the target queue to which the message should be sent.
		:param message: The content of the message to be published, represented as a dictionary.
		"""
		pass

	@abstractmethod
	async def consume(self, queue_name: str, callback: Callable):
		"""
		An abstract method to consume messages from a specified queue asynchronously.
		"""
		pass


class RabbitMQManager(RabbitMQManagerInterface):
	"""
	Manages RabbitMQ connections, queues, and message publishing/consuming.

	Provides functionality to establish connections to a RabbitMQ server,
	declare queues, publish messages, and consume messages. This class
	serves as an interface between the application and RabbitMQ using
	asynchronous communication.

	:ivar amqp_url: The AMQP URL used for connecting to the RabbitMQ server.
	:type amqp_url: str
	"""

	def __init__(self, amqp_url: str):
		self.amqp_url = amqp_url
		self._connection = None
		self._channel = None

	async def connect(self):
		"""
		Establishes a robust connection to the AMQP broker and declares a durable queue
		for user registrations. Ensures the channel is initialized and ready for use.

		:raises aio_pika.exceptions.ProbableAuthenticationError: If authentication fails.
		:raises aio_pika.exceptions.ProbableAccessDeniedError: If permission to access
		    the specified queue is denied.
		:raises aio_pika.exceptions.AMQPConnectionError: If there are issues in
		    connecting to the AMQP broker.
		:return: None
		"""
		self._connection = await aio_pika.connect_robust(self.amqp_url)
		self._channel = await self._connection.channel()
		await self._channel.declare_queue(USER_REGISTRATION_QUEUE, durable=True)

	async def close(self):
		"""
		Closes the existing connection and channel if it is active.

		This coroutine checks for the presence of an active connection and channel and ensures
		that it is properly closed. If no connection exists, this operation does
		nothing.

		:return: None
		"""
		try:
			if self._channel and not self._channel.is_closed:
				await self._channel.close()
		finally:
			if self._connection and not self._connection.is_closed:
				await self._connection.close()

	async def publish(self, queue_name: str, message: dict):
		"""
		Publishes a message to the specified RabbitMQ queue asynchronously.

		This method takes a queue name and a message, serializes the message into
		JSON format, and publishes it to the RabbitMQ queue via the default exchange.
		It ensures that a RabbitMQ connection is established before publishing.

		:param queue_name: The name of the target RabbitMQ queue to publish the message to.
		:type queue_name: str
		:param message: A dictionary containing the message content to be published.
		:type message: dict
		:return: None
		:raises RuntimeError: If the RabbitMQ connection is not established.
		"""
		if not self._channel:
			raise RuntimeError("RabbitMQ connection is not established")
		body = json.dumps(message).encode()
		await self._channel.default_exchange.publish(aio_pika.Message(body=body), routing_key=queue_name)

	async def consume(self, queue_name: str, callback: Callable):
		"""
		Consumes messages from a specified asynchronous queue and processes each message.

		This method declares the specified queue by name and retrieves messages from it
		using an asynchronous iterator. Each message is processed within the context of
		the message lifecycle, ensuring that the message is acknowledged after
		successful processing.

		:param callback:
		:param queue_name: The name of the queue from which messages are consumed.
		:type queue_name: str
		"""
		queue = await self._channel.declare_queue(queue_name, durable=True)

		async with queue.iterator() as queue_iter:
			async for message in queue_iter:
				async with message.process():
					await callback(message.body)


def get_rmq_manager(request: Request) -> RabbitMQManagerInterface:
	"""
	Retrieve the RabbitMQ manager instance from the application state.

	This function extracts the RabbitMQ manager instance from the application
	state associated with the incoming request. It serves as an accessor for
	the RabbitMQManagerInterface implementation.

	:param request: The HTTP request object containing the application state.
	:type request: Request
	:return: An instance of RabbitMQManagerInterface extracted from the
	    application's state.
	:rtype: RabbitMQManagerInterface
	"""
	rmq_manager = request.app.state.rmq_manager
	return rmq_manager
