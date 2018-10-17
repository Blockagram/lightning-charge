import asyncio
import json
from lightning import LightningRpc

from blinker import Namespace
from charge.models import Invoice

my_signals = Namespace()
payment_signal = my_signals.signal("payment")
paid_signal = my_signals.signal("paid")


class AsyncLightningRpc(LightningRpc):
    @staticmethod
    async def _writeobj(sock, obj):
        s = json.dumps(obj)
        loop = asyncio.get_event_loop()
        sock.setBlocking(False)
        await loop.sock_sendall(sock, bytearray(s, "UTF-8"))

    async def _readobj(self, sock):
        buff = b""
        loop = asyncio.get_event_loop()
        sock.setBlocking(False)
        while True:
            try:
                b = await loop.sock_recv(sock, 1024)
                buff += b
                if len(b) == 0:
                    return {"error": "Connection to RPC server lost."}

                if buff[-3:] != b" }\n":
                    continue

                # Convert late to UTF-8 so glyphs split across recvs do not
                # impact us
                objs, _ = self.decoder.raw_decode(buff.decode("UTF-8"))
                return objs
            except ValueError:
                # Probably didn't read enough
                pass


async def watch_lightning_task():
    ln = AsyncLightningRpc("SOMEthING")
    last_index = None
    while True:
        last_index = await poll_lightning(ln, last_index)
        await asyncio.sleep(1)


async def poll_lightning(ln, last_index):
    ln_invoice = ln.waitanyinvoice(last_index)
    if Invoice.mark_paid(
        ln_invoice.label,
        ln_invoice.pay_index,
        ln_invoice.paid_at,
        ln_invoice.msatoshi_received,
    ):
        invoice = Invoice.get(ln_invoice.label)
        payment_signal.send(invoice)


# class PaymentListener:
#     def __init__(self, rpc_path):
#         self.ln = LightningRpc(rpc_path)
#         loop = asyncio.get_event_loop()
#         loop.create_task(self.poll_next())

#     async def poll(self):
#         await self.poll_next(last_index)
#         await asyncio.sleep(1)

#     async def poll_next(self, last_index):
#         ln_invoice = self.ln.waitanyinvoice(last_index)
#         if Invoice.mark_paid(
#             ln_invoice.label,
#             ln_invoice.pay_index,
#             ln_invoice.paid_at,
#             ln_invoice.msatoshi_received,
#         ):
#             invoice = Invoice.get(ln_invoice.label)
#             payment_signal.send(invoice)
