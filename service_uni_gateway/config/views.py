import requests
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from requests import HTTPError
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def api_home(request):
    context = {
        "user": "/user/api/",
        "institution": "/institution/api/",
        "enrollment": "/enrollment/api/",
        "academic_consideration": "/academic_consideration/api/",
    }
    return Response(context, status=status.HTTP_200_OK)


def make_request(method, url, json_data=None):
    try:
        print(f"json_data: {json_data}", flush=True)
        response = requests.request(method, url, json=json_data)
        response.raise_for_status()  # Raises HTTPError for bad responses (4xx and 5xx)

        # If the response is JSON, you can access it using response.json()
        return response.status_code, response.json() if 'json' in response.headers.get('content-type',
                                                                                       '').lower() else response.text
    except requests.exceptions.HTTPError as errh:
        return response.status_code, f"HTTP Error: {errh}"
    except requests.exceptions.RequestException as err:
        return None, f"Request Exception: {err}"
    except Exception as err:
        return None, f"An error occurred: {err}"


@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def gateway(request):

    # analyse request
    request_path = request.get_full_path()
    split_path = request_path.split("/")
    service_name = split_path[1]
    request_path_part = '/'.join(split_path[2:])

    if service_name == "user":
        api_url = 'http://service_uni_user_api:8001/'

        if 'docs' in split_path:
            return redirect('http://localhost:8001/api/docs/')
        request_path = api_url + request_path_part
    elif service_name == "institution":
        api_url = 'http://service_uni_institution_api:8002/'
        if 'docs' in split_path:
            return redirect('http://localhost:8002/api/docs/')
        request_path = api_url + request_path_part
    elif service_name == "enrollment":
        api_url = 'http://service_uni_enrollment_api:8003/'
        if 'docs' in split_path:
            return redirect('http://localhost:8003/api/docs/')
        request_path = api_url + request_path_part
    elif service_name == "academic_consideration":
        api_url = 'http://service_uni_acadcons_api:8006/'
        if 'docs' in split_path:
            return redirect('http://localhost:8006/api/docs/')
        request_path = api_url + request_path_part
    else:
        request_path = ""

    if request_path:
        if request_path[-1] != "/":
            request_path += "/"
        status_code, data = make_request(request.method, request_path, request.data)

        if status_code is not None:
            return Response({"status_code": status_code, "data": data})
        else:
            return Response({"error": data}, status=500)
    else:
        Response('Bad request: No Service Definition', status=status.HTTP_400_BAD_REQUEST)
