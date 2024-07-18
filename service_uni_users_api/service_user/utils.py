from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from rest_framework.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from .models import ServiceUser
from .tokens import user_tokenizer


def validate_token(uidb64, token):
    is_valid = False

    try:
        user_id = force_str(urlsafe_base64_decode(uidb64))
        user = ServiceUser.objects.get(id=user_id)
    except (TypeError, ValueError, OverflowError, ServiceUser.DoesNotExist):
        user = None

    if user and user_tokenizer.check_token(user, token):
        is_valid = True

    return user, is_valid


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def jwt_token(user):
    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

    payload = jwt_payload_handler(user)
    token = jwt_encode_handler(payload)
    return token
