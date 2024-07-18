import json

from django.shortcuts import redirect

from helpers.helper_functions import make_request


def watch_login(refresh_token):
    return_value = False
    if refresh_token:
        # Make a call to verify identity
        token_verify_url = "user/api/token/verify/"
        json_data = json.dumps({'token': refresh_token})
        status, token_details = make_request('post', token_verify_url, json_data)

        if status in [200, 201]:
            status_code = token_details["status_code"]
            if status_code in [200, 201]:
                token_data = token_details["data"]

                if token_data:
                    # Token valid redirect to dashboard page
                    return_value = False
                else:
                    return_value = True
    return return_value


def must_authenticate(view):
    def _wrapped_view(request, *args, **kwargs):
        refresh_token = request.session.get("refresh_token", None)

        token_verify_url = "user/api/token/verify/"
        status, token_details = make_request('post', token_verify_url, {'token': refresh_token})

        if status in [200, 201]:
            status_code = token_details["status_code"]
            if status_code in [200, 201]:
                token_data = token_details["data"]

                if not token_data:
                    # Empty dict is returned
                    return view(request, *args, **kwargs)
                else:
                    return redirect('/')
            else:
                return redirect('/')
        else:
            return redirect('/')
    return _wrapped_view
