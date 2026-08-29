# ============= Health check servers =============
#
# Two lightweight servers used by orchestrators (Docker, k8s, load balancers)
# to probe liveness:
#
#   - HTTP: responds "200 OK" with a small JSON body on any request.
#   - UDP:  echoes back whatever datagram it receives, on a separate port.

import asyncio
import contextlib
import json
import logging

logger = logging.getLogger(__name__)


class _HealthUDPProtocol(asyncio.DatagramProtocol):
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        # Echo the payload straight back to the sender.
        self.transport.sendto(data, addr)


async def _handle_http(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    try:
        # Drain the request line/headers so the client can write without blocking.
        with contextlib.suppress(asyncio.TimeoutError):
            while True:
                line = await asyncio.wait_for(reader.readline(), timeout=1)
                if line in (b"\r\n", b"\n", b""):
                    break

        body = json.dumps({"status": "ok"}).encode()
        response = (
            b"HTTP/1.1 200 OK\r\n"
            b"Content-Type: application/json\r\n"
            b"Content-Length: " + str(len(body)).encode() + b"\r\n"
            b"Connection: close\r\n"
            b"\r\n" + body
        )
        writer.write(response)
        await writer.drain()
    finally:
        writer.close()
        with contextlib.suppress(Exception):
            await writer.wait_closed()


@contextlib.asynccontextmanager
async def serve_health_checks(http_host: str, http_port: int, udp_host: str, udp_port: int):
    loop = asyncio.get_running_loop()

    http_server = await asyncio.start_server(_handle_http, http_host, http_port)
    logger.info("Starting HTTP health check on %s:%d", http_host, http_port)

    udp_transport, _ = await loop.create_datagram_endpoint(
        _HealthUDPProtocol, local_addr=(udp_host, udp_port)
    )
    logger.info("Starting UDP echo health check on %s:%d", udp_host, udp_port)

    try:
        async with http_server:
            yield
    finally:
        udp_transport.close()
        logger.info("Health check servers are closed")
