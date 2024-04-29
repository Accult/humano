import requests
import json
from dotenv import load_dotenv
from logging_config import logger
import os
import time

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")
LOCATION_ID = os.getenv("LOCATION_ID")
TOKEN = os.getenv("ACCESS_TOKEN")
api_version = "2021-07-28"
API_KEY = os.getenv("API_KEY")
limit_amount_of_users = 100


def get_contact_by_number(phone_number):
    """
    search contact in ghl by phone number
    :param phone_number:
    :return:
    """

    response = requests.get(
        "https://services.leadconnectorhq.com/contacts/",
        params={"query": phone_number, "locationId": LOCATION_ID},
        headers={
            "locationId": LOCATION_ID,
            "Authorization": f"Bearer {TOKEN}",
            # "Authorization": f"Bearer {API_KEY}",
            "Version": api_version,
        },
    )
    result = response.json()
    print(result)
    if result["contacts"]:
        first_contact = result["contacts"][0]
        if "id" in first_contact:
            return first_contact["id"]
    else:
        return False


def get_conversations(ghl_contact_id):
    """
    searches for Conversations by Contact ID and returns an Conversation object
    """
    logger.info(f"{get_conversations.__name__} -- GHL - GETTING CONVERSATION FOR - {ghl_contact_id}")

    response = requests.get(
        url=f"https://services.leadconnectorhq.com/conversations/search?contactId={ghl_contact_id}",
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Version": "2021-07-28",
        },
    )

    status_code = response.status_code
    logger.info(f"{get_conversations.__name__} -- GHL - STATUS CODE -- {status_code}")

    result = {"success": False, "data": None, "conversation_id": None}

    try:
        response_data = response.json()
        logger.info(f"{get_conversations.__name__} -- GHL RESPONSE - {response_data}")

        if response_data["total"] > 0:
            result["success"] = True
            result["data"] = response_data
            result["conversation_id"] = response_data["conversations"][0]["id"]
    except Exception as ex:
        logger.error(f"{get_conversations.__name__} -- !!! GHL ERROR - {ex}")

    return result


def create_conversation(ghl_contact_id):
    """
    creates conversation for a provided Contact ID
    """
    logger.info(f"{create_conversation.__name__} -- GHL - CREATING CONVERSATION FOR - {ghl_contact_id}")

    response = requests.post(
        url="https://services.leadconnectorhq.com/conversations/",
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Version": "2021-07-28",
        },
        json={"locationId": f"{LOCATION_ID}", "contactId": f"{ghl_contact_id}"},
    )

    status_code = response.status_code
    logger.info(f"{create_conversation.__name__} -- GHL - STATUS CODE -- {status_code}")

    result = {"success": False, "data": None, "conversation_id": None}

    try:
        response_data = response.json()
        logger.info(f"{create_conversation.__name__} -- GHL RESPONSE - {response_data}")

        result["success"] = True if status_code in (201, 200) and response_data["success"] is True else False
        result["data"] = response_data
        result["conversation_id"] = response_data["conversation"]["id"]
    except Exception as ex:
        logger.error(f"{create_conversation.__name__} -- !!! GHL ERROR - {ex}")

    return result


def add_inbound_message(ghl_conversation_id, message_text):
    """
    creates inbound Message in a Conversation for a provided Contact ID
    """
    logger.info(f"{add_inbound_message.__name__} -- GHL - ADDING SMS NOTE TO -- {ghl_conversation_id}")
    response = requests.post(
        url="https://services.leadconnectorhq.com/conversations/messages/inbound",
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Version": "2021-07-28",
        },
        json={
            "type": "SMS",
            "conversationId": f"{ghl_conversation_id}",
            "message": f"{message_text}",
            "direction": "inbound",
        },
    )

    status_code = response.status_code
    logger.info(f"{add_inbound_message.__name__} -- GHL - STATUS CODE -- {status_code}")

    result = False

    try:
        response_data = response.json()
        logger.info(f"{add_inbound_message.__name__} -- GHL RESPONSE - {response_data}")

        result = True if response_data["success"] is True else False
    except Exception as ex:
        logger.error(f"{add_inbound_message.__name__} -- !!! GHL ERROR - {ex}")

    return result, ghl_conversation_id


def modify_ghl_conversation(contact_id, sms_message):
    """
    handles Conversation modification for a provided Contact ID
    by defining whether provided Contact has a Conversation
    """

    logger.info(f"{modify_ghl_conversation.__name__} -- MODIFYING CONTACTs CONVERSATIONS - {contact_id}")

    get_conversation_response = get_conversations(contact_id)
    time.sleep(0.1)

    if get_conversation_response["success"] is True:
        conversation_id = get_conversation_response["conversation_id"]

        # return True if add_inbound_message(conversation_id, sms_message) is True else False
        return add_inbound_message(conversation_id, sms_message)

    else:
        create_conversation_response = create_conversation(contact_id)
        time.sleep(0.1)

        if create_conversation_response["success"] is True:
            conversation_id = create_conversation_response["conversation_id"]

            # return True if add_inbound_message(conversation_id, sms_message) is True else False
            return add_inbound_message(conversation_id, sms_message)


def set_ghl_sms_blast_status(contact_id: str, status: str):
    """
    sets SMS sent result status for provided Contact ID
    """
    BASE_URL = f"https://services.leadconnectorhq.com/contacts/{contact_id}/"
    HEADERS = {
        "Accept": "application/json",
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "Version": "2021-07-28",
    }
    PAYLOAD = {
        "customFields": [
            {"id": "KdiQPtxUnTXWEP4k0PW9", "value": status},  # success / failed
            {"id": "t51MQqbEKlCera44Wgmw", "value": 1 if status.lower() == "success" else 0},
        ]
    }
    logger.info(f"{set_ghl_sms_blast_status.__name__} -- GHL - SETTING STATUS - {status} FOR - {contact_id}")

    response = requests.put(url=BASE_URL, headers=HEADERS, json=PAYLOAD)

    status_code = response.status_code
    logger.info(f"{set_ghl_sms_blast_status.__name__} -- GHL - STATUS CODE -- {status_code}")

    result = False

    try:
        response_data = response.json()
        logger.info(f"{set_ghl_sms_blast_status.__name__} -- GHL RESPONSE - {response_data}")

        result = True if response_data["succeded"] is True else False
    except Exception as ex:
        logger.error(f"{set_ghl_sms_blast_status.__name__} -- !!! GHL ERROR - {ex}")

    return result


def send_sms_ghl(contact_id: str, message: str):
    """
    sends single SMS message with GHL
    """
    BASE_URL = "https://services.leadconnectorhq.com/conversations/messages"
    HEADERS = {
        "Accept": "application/json",
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "Version": "2021-04-15",
    }
    PAYLOAD = {"type": "SMS", "contactId": contact_id, "message": message}
    response = requests.post(url=BASE_URL, headers=HEADERS, json=PAYLOAD)

    status_code = response.status_code
    logger.info(f"{send_sms_ghl.__name__} -- GHL - STATUS CODE -- {status_code}")

    result = False

    try:
        response_data = response.json()
        logger.info(f"{send_sms_ghl.__name__} -- GHL RESPONSE - {response_data}")

        result = True if status_code in (201, 200) else False
    except Exception as ex:
        logger.error(f"{send_sms_ghl.__name__} -- !!! GHL ERROR - {ex}")

    return result


def update_env_variables(new_tokens):
    """
    update tokens in .env file after generation new
    :param new_tokens:
    :return:
    """
    env_file = ".env"
    lines = []

    with open(env_file, "r") as f:
        lines = f.readlines()

    for i in range(len(lines)):
        for variable, new_token in new_tokens.items():
            if lines[i].startswith(variable + "="):
                lines[i] = variable + "=" + new_token + "\n"
                break

    with open(env_file, "w") as f:
        f.writelines(lines)


def get_access_token():
    """
    update ghl authorization tokens using api
    :return:
    """
    url = "https://services.leadconnectorhq.com/oauth/token"
    response = requests.post(
        url,
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": REFRESH_TOKEN,
        },
    )
    data = response.json()
    print(response.json())
    new_tokens = {"ACCESS_TOKEN": data["access_token"], "REFRESH_TOKEN": data["refresh_token"]}
    return new_tokens


def fetch_all_contacts():
    """
    get all contacts from ghl
    :return:
    """
    url = "https://services.leadconnectorhq.com/contacts/"
    # url = "https://rest.gohighlevel.com/v1/contacts/"
    headers = {
        "locationId": LOCATION_ID,
        "Authorization": f"Bearer {TOKEN}",
        # "Authorization": f"Bearer {API_KEY}",
        "Version": api_version,
    }

    all_contacts = []

    response = requests.get(url, headers=headers, params={"limit": limit_amount_of_users, "locationId": LOCATION_ID})
    data = response.json()
    all_contacts.extend(data.get("contacts", []))
    next_url = data["meta"]["nextPageUrl"]

    def fetch_page(next_url):
        response = requests.get(next_url, headers=headers, params={})
        data = response.json()
        all_contacts.extend(data.get("contacts", []))
        next_url = data["meta"]["nextPageUrl"]
        if next_url:
            fetch_page(next_url)

    fetch_page(next_url)
    json_string = json.dumps(all_contacts, indent=4)

    with open("contacts/data.json", "w") as json_file:
        json_file.write(json_string)


def tokens_update():
    new_tokens = get_access_token()
    update_env_variables(new_tokens)
