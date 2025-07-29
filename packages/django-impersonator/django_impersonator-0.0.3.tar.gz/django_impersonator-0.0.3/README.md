# django-impersonate

This Django app lets admin users impersonate other users, useful when testing and debugging permissions.

**Non superusers are not allowed** to perform this request, even if they have view rights to the `User` model, so that this cannot be used for privilege escalation.

As admin, I can choose the "Impersonate" action:

![image](https://user-images.githubusercontent.com/7786556/228572564-6549367d-3ee4-4b0b-a978-a3467388b654.png)

Impersonations are terminated by closing the bottom left pop-up.

![image](https://user-images.githubusercontent.com/7786556/228573725-9bde3dbd-1df0-4884-a333-95165cac880a.png)


Impersonate is not available for regular users, returning an error for those with view rights to the `User` model.


## Setup

Add middleware to your middleware list and make sure it comes *after* `django.contrib.auth.middleware.AuthenticationMiddleware`:

```python
MIDDLEWARE = [
    ...
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    ...
    'impersonate.middleware.ImpersonateMiddleware',
    ...
]
```

In one of your `admin.py` files, add the action to `UserAdmin` (or the admin model of your custom User)

```python
from impersonate.admin import impersonate_action
from django.contrib.auth import admin


admin.UserAdmin.actions.append(impersonate_action)
```

Or call it from any of your views (if you're not using django-admin)

```python
from django.contrib.auth import models
from impersonate.admin import impersonate_action

def my_view(request, target_username):
    return impersonate_action(None, request, models.User.objects.filter(username=target_username))
```
