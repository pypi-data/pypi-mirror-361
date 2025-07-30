import asyncio

from collections.abc import AsyncIterator, Callable
from typing import ParamSpec

from .base import ClientBase, StreamEvent

from ..errors import ServerError
from ..objects import Notification


P = ParamSpec("P")


class StreamBase(ClientBase):
	async def stream_health(self) -> bool:
		try:
			await self.send("GET", "/api/v1/streaming/health", None)
			return True

		except ServerError as error:
			if error.status >= 500:
				return False

			raise


	def stream_hashtag(self, tag: str, only_local: bool = False) -> AsyncIterator[StreamEvent]:
		params = {"tag": tag}
		path = "/api/v1/streaming/hashtag"

		if only_local:
			path += "/local"

		return self.stream(path, params)


	def stream_home(self) -> AsyncIterator[StreamEvent]:
		return self.stream("/api/v1/streaming/user")


	def stream_direct(self) -> AsyncIterator[StreamEvent]:
		return self.stream("/api/v1/streaming/direct")


	def stream_list(self, list_id: str) -> AsyncIterator[StreamEvent]:
		params = {"list": list_id}
		return self.stream("/api/v1/streaming/list", params)


	def stream_notifications(self) -> AsyncIterator[Notification]:
		return self.stream("/api/v1/streaming/user/notification", cls = Notification)


	def stream_public(self,
					only_media: bool = False,
					only_remote: bool = False,
					only_local: bool = False) -> AsyncIterator[StreamEvent]:

		params = {"only_media": str(only_media).lower()}
		path = "/api/v1/streaming/public"

		if only_remote and only_local:
			raise ValueError("'only_remote' and 'only_local' are mutually exclusive")

		if only_remote:
			path += "/remote"

		elif only_local:
			path += "/local"

		return self.stream(path, params)


	async def stream_with_callback(self,
							iterator: AsyncIterator[StreamEvent],
							callback: Callable[[StreamEvent], None]) -> asyncio.Task[None]:
		"""
			Run a stream iterator in the background and return the associated :class:`asyncio.Task`
			object

			:param iterator: Async iterator from a :meth:`Client.stream` method
			:param callback: Function that gets called for every stream event
		"""

		return asyncio.create_task(self.handle_stream_with_callback(iterator, callback))


	async def handle_stream_with_callback(self,
							iterator: AsyncIterator[StreamEvent],
							callback: Callable[[StreamEvent], None]) -> None:

		try:
			async for event in iterator:
				callback(event)

		except asyncio.CancelledError:
			pass
