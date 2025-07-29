from django.contrib import admin, messages
from django.shortcuts import HttpResponseRedirect

from .middleware import COOKIE_NAME


@admin.action(description='Impersonate selected user')
def impersonate_action(modeladmin, request, queryset):
    if not request.user.is_superuser:
        modeladmin.message_user(request, 'DENIED! How did you get here???', messages.ERROR)
        return
    # use len() to cache the queryset for next call
    if len(queryset) != 1:
        modeladmin.message_user(request, 'This action requires 1 and only 1 selected item', messages.WARNING)
        return
    response = HttpResponseRedirect('/')
    response.set_cookie(COOKIE_NAME, queryset[0].username)
    return response
