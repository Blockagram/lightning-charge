from charge.models import Invoice
from charge.extensions import ma, db


class InvoiceSchema(ma.Schema):
    class Meta:
        model = Invoice
        # fields = ('status', 'msatoshi', 'metadata')
        sqla_session = db.session
