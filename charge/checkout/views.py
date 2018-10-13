from flask import Blueprint, abort, render_template, make_response
import qrcode

from charge.models import Invoice
from charge.invoicing.resources import InvoiceSchema

blueprint = Blueprint('checkout', __name__)

invoice_schema = InvoiceSchema()
invoices_schema = InvoiceSchema(many=True)


@blueprint.route('/checkout/<int:invoice_id>')
def checkout_invoice(invoice_id):
    invoice = Invoice.query.get(invoice_id)
    return render_template('checkout', invoice)


@blueprint.route('/checkout/<int:invoice_id>/wait')
def checkout_wait(invoice_id):
    """
    like invoice_wait but no auth required, user accessible, hides private fields
    """
    invoice = Invoice.get(invoice_id)
    if invoice.status == 'paid':
        return invoice_schema.jsonify(invoice)
    if invoice.status == 'expired':
        abort(410)
    # TODO long-polling for c-lightning status with timeout


@blueprint.route('/checkout/<int:invoice_id>/qr.png')
def invoice_qr(invoice_id):
    invoice = Invoice.query.get(invoice_id)
    qr = qrcode.make(f"lightning:{invoice.payreq}".uppercase())
    response = make_response(qr)
    response.headers.set('Content-Type', 'image/png')
    return response
