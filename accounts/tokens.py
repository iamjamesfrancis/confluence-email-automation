from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
                six.text_type(user.pk) + six.text_type(timestamp) +
                six.text_type(user.is_active)
        )


class ForgotPasswordTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return six.text_type(user.is_active) + six.text_type(user.pk) + six.text_type(timestamp) + six.text_type(
            user.password) + six.text_type(user.last_login)


account_activation_token = AccountActivationTokenGenerator()
forgot_password_token = ForgotPasswordTokenGenerator()
