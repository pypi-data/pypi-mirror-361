
from django.contrib import admin
from knox import models as knox_models

from . import models


@admin.register(models.Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ('truncated_digest', 'user', 'created', 'expiry', 'notes')
    list_filter = ('user',)
    fields = ()

    def truncated_digest(self, obj):
        return f'{obj.digest[:6]}...{obj.digest[-6:]}'

    truncated_digest.short_description = 'Digest'

    def get_exclude(self, request, obj=None):
        r = super().get_exclude(request, obj)
        if obj is None:
            # token_key and digest are not meant to be chosen
            return tuple(r or ()) + ('token_key', 'digest')
        return r

    def save_model(self, request, obj, form, change):
        token = obj.save()
        if token is not None:
            self.message_user(request, token, extra_tags='token')


@admin.register(models.MyToken)
class MyTokenAdmin(TokenAdmin):
    list_display = ('truncated_digest', 'created', 'expiry', 'notes')
    list_filter = ()
    fields = ()
    exclude = ('user',)

    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True

    def get_queryset(self, request):
        return super().get_queryset(request).filter(user=request.user)

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super().save_model(request, obj, form, change)


admin.site.unregister(knox_models.AuthToken)
