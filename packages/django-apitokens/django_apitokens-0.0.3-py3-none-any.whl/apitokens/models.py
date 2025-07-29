from django.db import models
from knox import crypto
from knox.models import AuthToken
from knox.settings import CONSTANTS


class Token(AuthToken):
    """
    django-rest-knox does not allow swapping AuthToken model used (PR or fork!)
    BUT as it only creates tokens in the LoginView, if we are not using it, we're safe to subclass it
    and only create it ourselves.
    Everything *should* work!
    """

    notes = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        """
        do it the same way as DRK AuthToken, not Knox:
        - custom save() over object manager, so it's also used by admin
        """
        token = None
        if not self.digest:
            token = crypto.create_token_string()
            self.digest = crypto.hash_token(token)
            self.token_key = token[: CONSTANTS.TOKEN_KEY_LENGTH]
        super().save(*args, **kwargs)
        return token


class MyToken(Token):
    class Meta:
        proxy = True
