import io

import qrcode
from flask import redirect, render_template, request, url_for, session, Response, flash, abort
from flask_login import current_user, login_user, logout_user, login_required

from app.modules.auth import auth_bp
from app.modules.auth.forms import LoginForm, SignupForm, TwoFactorForm
from app.modules.auth.services import AuthenticationService
from app.modules.profile.services import UserProfileService
from app import db

authentication_service = AuthenticationService()
user_profile_service = UserProfileService()


@auth_bp.route("/signup/", methods=["GET", "POST"])
def show_signup_form():
    if current_user.is_authenticated:
        return redirect(url_for("public.index"))

    form = SignupForm()
    if form.validate_on_submit():
        email = form.email.data
        if not authentication_service.is_email_available(email):
            return render_template("auth/signup_form.html", form=form, error=f"Email {email} in use")

        try:
            user = authentication_service.create_with_profile(**form.data)
        except Exception as exc:
            return render_template("auth/signup_form.html", form=form, error=f"Error creating user: {exc}")

        # Log user
        login_user(user, remember=True)
        return redirect(url_for("public.index"))

    return render_template("auth/signup_form.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("public.index"))

    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():
        user = authentication_service.get_user_by_email(form.email.data)
        if user and user.check_password(form.password.data):
            if user.has_2fa_enabled:
                # Guardar ID de usuario en sesión y redirigir a la página de 2FA
                session['2fa_user_id'] = user.id
                return redirect(url_for('auth.login_2fa'))
            else:
                # Iniciar sesión directamente si 2FA no está activado
                login_user(user, remember=form.remember_me.data)
                return redirect(url_for("public.index"))

        return render_template("auth/login_form.html", form=form, error="Invalid credentials")

    return render_template("auth/login_form.html", form=form)


@auth_bp.route("/login/2fa", methods=["GET", "POST"])
def login_2fa():
    user_id = session.get('2fa_user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    user = authentication_service.get_user_by_id(user_id)
    if not user:
        return redirect(url_for('auth.login'))

    form = TwoFactorForm()
    if form.validate_on_submit():
        if user.verify_totp(form.token.data):
            session.pop('2fa_user_id', None)
            login_user(user, remember=True)
            return redirect(url_for('public.index'))
        else:
            flash('Invalid 2FA token', 'danger')

    return render_template('auth/login_2fa.html', form=form)


@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("public.index"))


@auth_bp.route('/2fa/qrcode')
@login_required
def qrcode_2fa():
    uri = current_user.get_totp_uri()
    img_buf = io.BytesIO()
    qrcode.make(uri).save(img_buf)
    img_buf.seek(0)
    return Response(img_buf, mimetype='image/png')


@auth_bp.route('/2fa/enable', methods=['GET', 'POST'])
@login_required
def enable_2fa():
    if current_user.has_2fa_enabled:
        flash('Two-factor authentication is already enabled.', 'info')
        return redirect(url_for('profile.edit_profile'))

    if request.method == 'POST':
        # The user has confirmed they want to enable 2FA, show QR code
        return redirect(url_for('auth.verify_2fa'))

    # Show an intermediary page explaining 2FA
    return render_template('auth/enable_2fa.html')


@auth_bp.route('/2fa/verify', methods=['GET', 'POST'])
@login_required
def verify_2fa():
    if current_user.has_2fa_enabled:
        return redirect(url_for('profile.edit_profile'))

    form = TwoFactorForm()
    if form.validate_on_submit():
        if current_user.verify_totp(form.token.data):
            current_user.has_2fa_enabled = True
            db.session.commit()
            flash('Two-factor authentication has been enabled!', 'success')
            return redirect(url_for('profile.edit_profile'))
        else:
            flash('Invalid token. Please try again.', 'danger')

    return render_template('auth/verify_2fa.html', form=form)


@auth_bp.route('/2fa/disable', methods=['POST'])
@login_required
def disable_2fa():
    token = request.form.get('token')
    if not token or not current_user.verify_totp(token):
        flash('Invalid token. 2FA was not disabled.', 'danger')
        return redirect(url_for('profile.edit_profile'))

    current_user.has_2fa_enabled = False
    db.session.commit()
    flash('Two-factor authentication has been disabled.', 'success')
    return redirect(url_for('profile.edit_profile'))
