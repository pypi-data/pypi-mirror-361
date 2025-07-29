from django.contrib.auth import admin as auth_admin
from impersonate.admin import impersonate_action

auth_admin.UserAdmin.actions.append(impersonate_action)
