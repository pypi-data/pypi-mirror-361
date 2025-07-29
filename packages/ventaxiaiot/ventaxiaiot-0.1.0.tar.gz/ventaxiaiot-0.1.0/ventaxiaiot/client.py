# File: ventaxiaiot/client.py
import asyncio
import ssl
import sys

has_native_psk = sys.version_info >= (3, 13)

if not has_native_psk:
    raise RuntimeError("Native PSK requires Python 3.13+")

class AsyncNativePskClient:
    def __init__(self, wifi_device_id, identity, psk_key, host, port, loop=None):
        self.identity = identity
        self.psk_key = psk_key.encode('utf-8')
        self.host = host
        self.port = port
        self.wifi_device_id = wifi_device_id
        self.loop = loop or asyncio.get_event_loop()
        self.reader = None
        self.writer = None

    def psk_callback(self, hint):
        return self.identity, self.psk_key

    async def connect(self, timeout=30.0):
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.set_ciphers("PSK-AES128-CBC-SHA")
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        context.set_psk_client_callback(self.psk_callback)

        try:
            self.reader, self.writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port, ssl=context),
                timeout=timeout,
            )
        except Exception as e:
            raise ConnectionError(f"Failed to connect: {e}")

    async def send(self, message):
        if self.writer is None:
            raise ConnectionError("Not connected")
        self.writer.write((message + '\0').encode('utf-8'))
        await self.writer.drain()

    async def receive_messages(self, handler):
        buffer = b""
        try:
            while not self.reader.at_eof(): # type: ignore
                chunk = await self.reader.read(1024) # type: ignore
                if not chunk:
                    break
                buffer += chunk
                while b'\0' in buffer:
                    msg_bytes, buffer = buffer.split(b'\0', 1)
                    try:
                        await handler(msg_bytes.decode('utf-8').strip())
                    except Exception:
                        continue
        except asyncio.CancelledError:
            pass

    async def close(self):
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()