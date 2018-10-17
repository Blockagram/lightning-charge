# -*- coding: utf-8 -*-
"""The app module, containing the app factory function."""
import asyncio
import quart.flask_patch
from quart import Quart, request, abort

from charge import checkout, invoicing, webhook, config
from charge.extensions import db, migrate, ma
from charge.payment_listener import watch_lightning_task

# from charge.auth import check_auth

# from flask_sse import sse


def create_app(config=None, testing=False, cli=False):
    """Application factory, used to create application
    """
    app = Quart("charge")

    configure_app(app, testing)
    configure_extensions(app, cli)
    register_blueprints(app)

    loop = asyncio.get_event_loop()
    loop.create_task(watch_lightning_task())

    return app


def configure_app(app, testing=False):
    """set configuration for application
    """
    # default configuration
    app.config.from_object(config)

    if testing is True:
        # override with testing config
        app.config.from_object("charge.configtest")
    else:
        # override with env variable, fail silently if not set
        # app.config.from_envvar("CHARGE_CONFIG", silent=True)
        pass


def configure_extensions(app, cli):
    """configure extensions
    """
    db.init_app(app)
    ma.init_app(app)

    if cli is True:
        migrate.init_app(app, db)


def register_blueprints(app):
    """register all blueprints for application
    """

    #     app.register_blueprint(sse, url_prefix="/payment-stream")
    app.register_blueprint(checkout.views.blueprint)
    app.register_blueprint(invoicing.views.blueprint)
    app.register_blueprint(webhook.views.blueprint)


# @sse.before_request
# def check_access():
#     auth = request.authorization
#     if not auth or not check_auth(auth.username, auth.password):
#         abort(403)


def on_pay(invoice):
    sse.publish(
        f"id:{invoice.pay_index}\ndata:{invoice_schema.jsonify(invoice)}\n\n",
        type="payment",
    )
