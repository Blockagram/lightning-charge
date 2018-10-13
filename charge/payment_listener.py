from lightning import LightningRpc

from blinker import Namespace

my_signals = Namespace()
payment_signal = my_signals.signal("payment")
paid_signal = my_signals.signal("paid")


class PaymentListener:
    def __init__(self, rpc_path, model):
        self.ln = LightningRpc(rpc_path)
        self.model = model

    def poll_next(self, last_index):
        ln_invoice = self.ln.waitanyinvoice(last_index)
        if Invoice.mark_paid(
            ln_invoice.label,
            ln_invoice.pay_index,
            ln_invoice.paid_at,
            ln_invoice.msatoshi_received,
        ):
            invoice = Invoice.get(ln_invoice.label)
            model_saved.send(self)
