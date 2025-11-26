from datetime import datetime, timezone

import pyotp
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(256), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    otp_secret = db.Column(db.String(32))
    has_2fa_enabled = db.Column(db.Boolean, default=False, nullable=False)

    data_sets = db.relationship("DataSet", backref="user", lazy=True)
    profile = db.relationship("UserProfile", backref="user", uselist=False)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if "password" in kwargs:
            self.set_password(kwargs["password"])
        if self.otp_secret is None:
            self.otp_secret = pyotp.random_base32()

    def __repr__(self):
        return f"<User {self.email}>"

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_totp_uri(self):
        return pyotp.totp.TOTP(self.otp_secret).provisioning_uri(
            name=self.email,
            issuer_name='tennishub'
        )

    def verify_totp(self, token):
        """
        Verifies the TOTP token.
        The valid_window parameter allows for a tolerance of 1 step (30 seconds)
        before or after the current time to account for clock drift.
        """
        return pyotp.TOTP(self.otp_secret).verify(token, valid_window=1)

    def temp_folder(self) -> str:
        from app.modules.auth.services import AuthenticationService

        return AuthenticationService().temp_folder_by_user(self)
