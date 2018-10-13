# -*- coding: utf-8 -*-
"""The app module, containing the app factory function."""
from flask import Flask, request, abort

from charge import checkout, invoicing, webhook
from charge.extensions import db, migrate, ma

from charge.auth import check_auth
from flask_sse import sse


def create_app(config=None, testing=False, cli=False):
    """Application factory, used to create application
    """
    app = Flask('charge')

    configure_app(app, testing)
    configure_extensions(app, cli)
    register_blueprints(app)

    return app


def configure_app(app, testing=False):
    """set configuration for application
    """
    # default configuration
    app.config.from_object('charge.config')

    if testing is True:
        # override with testing config
        app.config.from_object('charge.configtest')
    else:
        # override with env variable, fail silently if not set
        app.config.from_envvar("CHARGE_CONFIG", silent=True)


def configure_extensions(app, cli):
    """configure flask extensions
    """
    db.init_app(app)
    ma.init_app(app)

    if cli is True:
        migrate.init_app(app, db)


def register_blueprints(app):
    """register all blueprints for application
    """

    app.register_blueprint(sse, url_prefix='/payment-stream')
    app.register_blueprint(checkout.views.blueprint)
    app.register_blueprint(invoicing.views.blueprint)
    app.register_blueprint(webhook.views.blueprint)


@sse.before_request
def check_access():
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        abort(403)


def on_pay(invoice):
    sse.publish(f"id:{invoice.pay_index}\ndata:{invoice_schema.jsonify(invoice)}\n\n", type='payment')
