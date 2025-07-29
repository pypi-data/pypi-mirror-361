import asyncio
import logging
from collections import namedtuple
from pathlib import Path
from unittest import IsolatedAsyncioTestCase

import grpc

from discordproxy._server import _shutdown_server, run_server
from discordproxy.discord_api_pb2 import (
    SendChannelMessageRequest,
    SendDirectMessageRequest,
)
from discordproxy.discord_api_pb2_grpc import DiscordApiStub
from discordproxy.exceptions import DiscordProxyHttpError, to_discord_proxy_exception

from .stubs import DiscordClientStub

MyArgsStub = namedtuple("MyArgsStub", ["host", "port"])

logging.basicConfig(
    filename=Path(__file__).with_suffix(".log"),
    format="%(asctime)s - %(levelname)s - %(module)s:%(funcName)s - %(message)s",
    filemode="w",
)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class TestEnd2End(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.host = "localhost"
        self.port = 50051
        self.target = f"{self.host}:{self.port}"
        token = "dummy"
        my_args = MyArgsStub(host=self.host, port=self.port)
        self.grpc_server = grpc.aio.server()
        self.discord_client = DiscordClientStub()
        asyncio.create_task(
            run_server(
                token=token,
                my_args=my_args,
                grpc_server=self.grpc_server,
                discord_client=self.discord_client,
            )
        )
        await asyncio.sleep(1)

    async def asyncTearDown(self) -> None:
        await _shutdown_server(
            grpc_server=self.grpc_server, discord_client=self.discord_client
        )

    async def test_should_send_direct_message_to_server(self):
        # given
        async with grpc.aio.insecure_channel(self.target) as grpc_channel:
            client = DiscordApiStub(grpc_channel)
            request = SendDirectMessageRequest(user_id=1001, content="content")
            # when
            response = await client.SendDirectMessage(request, timeout=5)
        # then
        self.assertEqual(response.message.channel_id, 2010)
        self.assertEqual(response.message.content, "content")

    async def test_should_send_direct_message_to_channel(self):
        # given
        async with grpc.aio.insecure_channel(self.target) as grpc_channel:
            client = DiscordApiStub(grpc_channel)
            request = SendChannelMessageRequest(channel_id=2001, content="content")
            # when
            response = await client.SendChannelMessage(request, timeout=5)
        # then
        self.assertEqual(response.message.channel_id, 2001)
        self.assertEqual(response.message.content, "content")

    async def test_should_raise_http_exception_when_not_found(self):
        # given
        async with grpc.aio.insecure_channel(self.target) as grpc_channel:
            client = DiscordApiStub(grpc_channel)
            request = SendDirectMessageRequest(user_id=1234, content="content")
            # when/then
            try:
                await client.SendDirectMessage(request, timeout=5)
            except Exception as ex:
                with self.assertRaises(DiscordProxyHttpError):
                    raise to_discord_proxy_exception(ex) from ex

    async def test_should_raise_http_exception_when_forbidden(self):
        # given
        async with grpc.aio.insecure_channel(self.target) as grpc_channel:
            client = DiscordApiStub(grpc_channel)
            request = SendChannelMessageRequest(channel_id=2100, content="content")
            # when/then
            try:
                await client.SendChannelMessage(request, timeout=5)
            except Exception as ex:
                with self.assertRaises(DiscordProxyHttpError):
                    raise to_discord_proxy_exception(ex) from ex
