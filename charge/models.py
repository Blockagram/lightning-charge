from datetime import datetime, timedelta
from charge.extensions import db
from charge.database import Model, Column, SurrogatePK


class Invoice(Model, SurrogatePK):
    msatoshi = Column(db.String(50), nullable=True)
    description = Column(db.String(256), nullable=True)
    quoted_currency = Column(db.String(3), nullable=True)
    quoted_amount = Column(db.String(30), nullable=True)
    rhash = Column(db.String(128), unique=True, nullable=False)
    payreq = Column(db.String(256), nullable=False)
    pay_index = Column(db.Integer, nullable=True)

    paid_at = Column(db.Integer, nullable=False)
    msatoshi_received = Column(db.String, nullable=True)
    expires_at = Column(db.Integer, nullable=False)
    created_at = Column(db.Integer, nullable=False)
    meta = Column(db.String(1024), nullable=True)

    @classmethod
    def purge_deleted(cls):
        db_invoices = cls.query.filter_by(pay_index=None).filter(
            Invoice.expires_at < (datetime.now() + timedelta(days=-1))
        )
        ln_invoices = lightning.list_invoices([i.id for i in db_invoices])
        Invoice.query.filter_by(
            id=[i.id for i in db_invoices if i.id not in ln_invoices]
        )  # todo fix

    @classmethod
    def mark_paid(cls, id, pay_index, paid_at, msatoshi_received):
        return Invoice.query.filter_by(id=id, pay_index=None).update(
            pay_index=pay_index, paid_at=paid_at, msatoshi_received=msatoshi_received
        )

    @property
    def status(self):
        if self.pay_index:
            return "paid"
        elif self.expires_at > datetime.now():
            return "unpaid"
        else:
            return "expired"

    def __repr__(self):
        return "<User %r>" % self.username


class InvoiceWebhook(Model, SurrogatePK):
    invoice_id = Column(db.ForeignKey("invoice.id"), nullable=False)
    url = Column(db.String(256), nullable=False)
    created_at = Column(db.Integer, nullable=False)
    requested_at = Column(db.Integer, nullable=True)
    success = Column(db.Boolean(), nullable=True)
    resp_code = Column(db.Integer(), nullable=True)
    resp_error = Column(db.String, nullable=True)
