from datetime import datetime
from flask import Blueprint, request, abort

from charge.models import Invoice
from charge.invoicing.resources import InvoiceSchema
from charge.auth import requires_auth

blueprint = Blueprint('invoicing', __name__)

invoice_schema = InvoiceSchema()
invoices_schema = InvoiceSchema(many=True)


@blueprint.route('/invoices', methods=('GET',))
@requires_auth
def get_invoices():
    invoices = Invoice.query.all()
    return invoices_schema.jsonify(invoices)


@blueprint.route('/invoice/<int:invoice_id>', methods=('GET',))
@requires_auth
def get_invoice(invoice_id):
    invoice = Invoice.get(invoice_id)
    return invoice_schema.jsonify(invoice)


@blueprint.route('/invoice', methods=('POST',))
@requires_auth
def create_invoice():
    invoice = Invoice(
        msatoshi=request.POST.get('msatoshi'),
        expires_at=datetime.now())
    invoice.save()
    return invoice_schema.jsonify(invoice)


@blueprint.route('/invoice/<int:invoice_id>/wait', methods=('GET',))
@requires_auth
def invoice_wait(invoice_id):
    invoice = Invoice.get(invoice_id)
    if invoice.status == 'paid':
        return invoice_schema.jsonify(invoice)
    if invoice.status == 'expired':
        abort(410)
    # TODO long-polling for c-lightning status with timeout
