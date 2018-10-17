# -*- coding: utf-8 -*-
"""Extensions module. Each extension is initialized in the app factory located
 in main.py."""
import quart.flask_patch
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate


db = SQLAlchemy()
ma = Marshmallow()
migrate = Migrate()
