import datetime
import requests


def get_my_u_id(name_list, existing_users):

    u_id = ""
    for name in name_list:
        if name:
            u_id += name[0].lower()

    for user in existing_users:
        if user.u_id == u_id:
            numbers = ""
            letters = ""
            for i in user.u_id:
                try:
                    num_ = int(i)
                    numbers += str(num_)
                except ValueError:
                    letters += i
            if numbers:
                u_id = letters + str(int(numbers) + 1)
            else:
                u_id = letters + str(1)

    return u_id


def generate_coe(student_type, program_code, u_id):
    current_time = datetime.datetime.now()
    year = current_time.date().year
    month = current_time.date().month
    coe = f"{student_type}/{year}/{month}/{program_code}/{u_id}"
    return coe


def generate_email(u_id, email_domain):
    email = f"{u_id}@{email_domain}.com"
    return email


def make_request(method, url, json_data=None):
    try:
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