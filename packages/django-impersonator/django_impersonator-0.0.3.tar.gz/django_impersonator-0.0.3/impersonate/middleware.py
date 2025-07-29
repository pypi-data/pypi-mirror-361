import re

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.template.loader import render_to_string

COOKIE_NAME = 'impersonate_user'
_HTML_TYPES = ("text/html", "application/xhtml+xml")


class ImpersonateMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        new_username = request.COOKIES.get(COOKIE_NAME)
        new_user = None
        if new_username:
            if not request.user.is_superuser:
                raise PermissionDenied
            new_user = get_user_model().objects.filter(username=new_username).first()
            if new_user:
                request.user = new_user
        response = self.get_response(request)
        if new_username:
            # Check for responses where the toolbar can't be inserted.
            content_encoding = response.get("Content-Encoding", "")
            content_type = response.get("Content-Type", "").split(";")[0]
            if getattr(response, "streaming", False) or content_encoding != "" or content_type not in _HTML_TYPES:
                return response

            # Insert the toolbar in the response.
            content = response.content.decode(response.charset)
            insert_before = '</body>'
            pattern = re.escape(insert_before)
            bits = re.split(pattern, content, flags=re.IGNORECASE)
            if len(bits) > 1:
                bits[-2] += render_to_string(
                    'impersonate/popup.html',
                    {
                        'new_user': new_user,
                        'new_username': new_username,
                        'cookie_name': COOKIE_NAME,
                    },
                )
                response.content = insert_before.join(bits)
                if "Content-Length" in response:
                    response["Content-Length"] = len(response.content)

        return response
