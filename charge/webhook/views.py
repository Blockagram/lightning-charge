from quart import Blueprint, request, abort

from charge.models import Invoice, InvoiceWebhook
from charge.invoicing.resources import InvoiceSchema
from charge.auth import requires_auth

blueprint = Blueprint("webhook", __name__)

invoice_schema = InvoiceSchema()
invoices_schema = InvoiceSchema(many=True)


@blueprint.route("/invoice/<int:invoice_id>/webhook", methods=("POST",))
@requires_auth
def invoice_webhook(invoice_id):
    invoice = Invoice.get_by_id(invoice_id)
    if invoice is None:
        abort(404)
    if invoice.status == "paid":
        abort(405)
    if invoice.status == "expired":
        abort(410)
    hook = InvoiceWebhook(invoice_id=invoice_id, url=request.POST.get("url"))
    hook.save()
    return "OK", 201
