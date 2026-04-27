from abc import ABC, abstractmethod

import aio_pika


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
	async def publish(self, queue_name: str, message: str):
		"""
		Publishes a message to the specified queue asynchronously.

		The `publish` method is an abstract method that must be implemented
		in subclasses. It is used to send a message to a given queue. This is
		an asynchronous operation.
		"""
		pass

	@abstractmethod
	async def consume(self, queue_name: str):
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
		await self._channel.declare_queue("user_registrations_queue", durable=True)

	async def close(self):
		"""
		Closes the existing connection if it is active.

		This coroutine checks for the presence of an active connection and ensures
		that it is properly closed. If no connection exists, this operation does
		nothing.

		:return: None
		"""
		if self._connection:
			await self._connection.close()

	async def publish(self, queue_name: str, message: str):
		"""
		Publishes a message to the specified queue in a RabbitMQ broker.

		This asynchronous method sends a given message to a queue identified
		by its name using the default exchange of the RabbitMQ channel. It
		requires an established connection to RabbitMQ. If the connection
		is not established, an error is raised.

		:param queue_name: The name of the queue to which the message will
		                   be published.
		:type queue_name: str
		:param message: The message content to be sent to the queue.
		:type message: str
		"""
		if not self._channel:
			raise RuntimeError("RabbitMQ connection is not established")
		await self._channel.default_exchange.publish(message, routing_key=queue_name)

	async def consume(self, queue_name: str):
		"""
		Consumes messages from a specified asynchronous queue and processes each message.

		This method declares the specified queue by name and retrieves messages from it
		using an asynchronous iterator. Each message is processed within the context of
		the message lifecycle, ensuring that the message is acknowledged after
		successful processing.

		:param queue_name: The name of the queue from which messages are consumed.
		:type queue_name: str
		"""
		queue = await self._channel.declare_queue(queue_name)

		async with queue.iterator() as queue_iter:
			async for message in queue_iter:
				async with message.process():
					print(message.body)
