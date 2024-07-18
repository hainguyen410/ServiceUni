import datetime

import requests
from config.settings import GATEWAY_URL


def make_request(method, url, json_data=None):
    url = GATEWAY_URL + url
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


def combine_data(data_list1, data_list2, key, data_list1_key=(), data_list2_key=()):
    session_enrollment_list = []
    if data_list1:
        for item1 in data_list1:
            for item2 in data_list2:
                if key in item1:
                    if item1[key] == item2["id"]:
                        new_data_list = {}
                        for i in range(0, len(data_list1_key)):
                            new_data_list[data_list1_key[i]] = item2[data_list1_key[i]]
                        for k in range(0, len(data_list2_key)):
                            new_data_list[data_list2_key[k]] = item1[data_list2_key[k]]
                        session_enrollment_list.append(
                            new_data_list
                        )
    return session_enrollment_list


def combine_data_inclusive(data_list1, data_list2, key, data_list1_key=(), data_list2_key=()):
    session_enrollment_list_updated = []
    if data_list1:
        for item1 in data_list1:
            for item2 in data_list2:
                if key in item1:
                    if item1[key] == item2["id"]:
                        for i in range(0, len(data_list1_key)):
                            item1[data_list1_key[i]] = item2[data_list1_key[i]]
                        for k in range(0, len(data_list2_key)):
                            item1[data_list2_key[k]] = item1[data_list2_key[k]]
                        session_enrollment_list_updated.append(
                            item1
                        )
    return session_enrollment_list_updated


def combine_data_with_dict(data_list1, data_list2, list_key, user_key_map, new_data_list1=(), new_data_list2=()):
    user_enrollment = []
    for item in data_list1:
        new_record = {}
        for i in item.keys():
            new_record[i] = item[i]

        for item2 in new_data_list1:
            if item2 in user_key_map:
                new_record[item2] = user_key_map[item2]

        for item3 in data_list2:
            if item3["id"] == item[list_key]:
                for i in range(0, len(new_data_list2)):
                    new_record[new_data_list2[i]] = item3[new_data_list2[i]]
                        # item[new_data_list2[i]] = item3[new_data_list2[i]]

        user_enrollment.append(new_record)

    return user_enrollment


def user_subject_program_combine(user_detail, program_list, subject_list):
    new_data = user_detail
    user_program_id = user_detail["program_id"]

    course_handling = new_data["current_course_handling"]
    course_enrolled = new_data["current_enrolled_courses"]
    if course_handling:
        user_subject_list = [int(item) for item in new_data["current_course_handling"]]
    else:
        user_subject_list = []
    if course_enrolled:
        user_subject_list2 = [int(item) for item in new_data["current_enrolled_courses"]]
    else:
        user_subject_list2 = []

    print(program_list, "asaaaa", flush=True)
    # Inject the Program
    if user_program_id:
        for item in program_list:
            if int(item["id"]) == int(user_program_id):
                new_data["program_name"] = item["name"]
                new_data["program_code"] = item["code"]

    # Inject the Subjects

    for item in subject_list:
        if "id" in item:
            if item["id"] in user_subject_list:
                subject_list1 = {
                    "subject_name": item["name"],
                    "subject_code": item["code"]
                }
                new_data["current_course_handling"].pop(new_data["current_course_handling"].index(int(item["id"])))
                new_data["current_course_handling"].append(subject_list1)
        if "id" in item:
            if item["id"] in user_subject_list2:
                subject_list2 = {
                    "subject_name": item["name"],
                    "subject_code": item["code"]
                }
                new_data["current_enrolled_courses"].pop(new_data["current_enrolled_courses"].index(int(item["id"])))
                new_data["current_enrolled_courses"].append(subject_list2)

    return new_data


def confirm_coe(coe, student_type, program_code, u_id):
    coe_split = coe.split('/')

    student_type_rv = coe_split[0]
    program_rv = coe_split[3]
    u_id_rv = coe_split[4]
    if student_type_rv == student_type and program_rv == program_code and u_id_rv == u_id:
        return True
    return False


def parse_response(status, response_data):
    error_list = []
    data = None
    if status in [200, 201]:
        status_code = response_data["status_code"]
        if status_code in [200, 201]:
            data = response_data["data"]
        else:
            error_list.append(f"Error {status_code} - {response_data}")
    else:
        error_list.append(f"Error {status} - {response_data}")
    return error_list, data


def update_record(left_list, right_list, key="id"):
    new_list = []
    for item1 in right_list:
        for item2 in left_list:
            item2_programs = item2["programs"]
            for item3 in item2_programs:
                if item1[key] == item3[key]:
                    item1["faculty"] = item2["name"]
        new_list.append(item1)


def get_program_school(program_id, school_list):
    school_data = None
    for school in school_list:
        programs = school['programs']
        if programs:
            school_program_ids = [int(program['id']) for program in school['programs']]
            if int(program_id) in school_program_ids:
                school_data = school
    return school_data


def generate_coe(student_type, program_code, u_id):
    current_time = datetime.datetime.now()
    year = current_time.date().year
    month = current_time.date().month
    coe = f"{student_type}/{year}/{month}/{program_code}/{u_id}"
    return coe


def generate_email(u_id, email_domain):
    email = f"{u_id}@{email_domain}.com"
    return email

#key1="subject_id" , key2="id")
def combine_lists_2(list1, list2, key1, key2):
    combined_list = []

    for item1 in list1:
        item1["ac_id"] = item1[key1]
        for item2 in list2:
            if item1[key1] == item2[key2]:
                combined_item = {**item1, **item2}
                combined_list.append(combined_item)

    return combined_list

def combine_and_remove_keys(listac, subjList, studentList):
    combined_list = []

    subject_mapping = {item['id']: item for item in subjList}
    student_mapping = {item['id']: item for item in studentList}

    for item in listac:
        combined_item = item.copy()
        combined_item["ac_id"] = item["id"]

        subject_info = subject_mapping.get(item['subject_id'])
        if subject_info:
            subject_info["subject_id"] = subject_info["id"]
            combined_item.update(subject_info)

        student_info = student_mapping.get(item['student_id'])
        if student_info:
            student_info["student_id"] = student_info["id"]
            combined_item.update(student_info)

        del combined_item["id"]
        combined_list.append(combined_item)

    return combined_list