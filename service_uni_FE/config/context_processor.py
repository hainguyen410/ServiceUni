def base_context_view(request):

    current_user_id = request.session.get('user_id', None)
    access_token = request.session.get('access_token', None)
    refresh_token = request.session.get('refresh_token', None)
    user_type = request.session.get('user_type', None)

    context = {
        'current_user_id': current_user_id,
        'user_type': user_type,
        'access_token': access_token,
        'refresh_token': refresh_token,
    }
    return context
