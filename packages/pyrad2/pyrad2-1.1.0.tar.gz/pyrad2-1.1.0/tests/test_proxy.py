import select
import socket
import unittest
from .mock import MockFd
from .mock import MockPoll
from .mock import MockSocket
from .mock import MockClassMethod
from .mock import UnmockClassMethods
from pyrad2.proxy import Proxy
from pyrad2.constants import PacketType
from pyrad2.server import ServerPacketError
from pyrad2.server import Server


class TrivialObject:
    """dummy object"""


class SocketTests(unittest.TestCase):
    def setUp(self):
        self.orgsocket = socket.socket
        socket.socket = MockSocket
        self.proxy = Proxy()
        self.proxy._fdmap = {}

    def tearDown(self):
        socket.socket = self.orgsocket

    def testProxyFd(self):
        self.proxy._poll = MockPoll()
        self.proxy._PrepareSockets()
        self.assertTrue(isinstance(self.proxy._proxyfd, MockSocket))
        self.assertEqual(list(self.proxy._fdmap.keys()), [1])
        self.assertEqual(
            self.proxy._poll.registry,
            {1: select.POLLIN | select.POLLPRI | select.POLLERR},
        )


class ProxyPacketHandlingTests(unittest.TestCase):
    def setUp(self):
        self.proxy = Proxy()
        self.proxy.hosts["host"] = TrivialObject()
        self.proxy.hosts["host"].secret = "supersecret"
        self.packet = TrivialObject()
        self.packet.code = PacketType.AccessAccept
        self.packet.source = ("host", "port")

    def testHandleProxyPacketUnknownHost(self):
        self.packet.source = ("stranger", "port")
        try:
            self.proxy._HandleProxyPacket(self.packet)
        except ServerPacketError as e:
            self.assertTrue("unknown host" in str(e))
        else:
            self.fail()

    def testHandleProxyPacketSetsSecret(self):
        self.proxy._HandleProxyPacket(self.packet)
        self.assertEqual(self.packet.secret, "supersecret")

    def testHandleProxyPacketHandlesWrongPacket(self):
        self.packet.code = PacketType.AccessRequest
        try:
            self.proxy._HandleProxyPacket(self.packet)
        except ServerPacketError as e:
            self.assertTrue("non-response" in str(e))
        else:
            self.fail()


class OtherTests(unittest.TestCase):
    def setUp(self):
        self.proxy = Proxy()
        self.proxy._proxyfd = MockFd()

    def tearDown(self):
        UnmockClassMethods(Proxy)
        UnmockClassMethods(Server)

    def testProcessInputNonProxyPort(self):
        fd = MockFd(fd=111)
        MockClassMethod(Server, "_ProcessInput")
        self.proxy._ProcessInput(fd)
        self.assertEqual(self.proxy.called, [("_ProcessInput", (fd,), {})])

    def testProcessInput(self):
        MockClassMethod(Proxy, "_GrabPacket")
        MockClassMethod(Proxy, "_HandleProxyPacket")
        self.proxy._ProcessInput(self.proxy._proxyfd)
        self.assertEqual(
            [x[0] for x in self.proxy.called], ["_GrabPacket", "_HandleProxyPacket"]
        )


if not hasattr(select, "poll"):
    del SocketTests
