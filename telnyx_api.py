import os

import json
import requests
from dotenv import load_dotenv

# from logging_config import logger
import logging
from datetime import datetime
import utils.utils as utils
import ghl_api

load_dotenv()
logger = logging.getLogger("ghl_logger")

# [{"message": "",
# "telnyx_sent": false,
# "telnyx_delivered": false,
# "telnyx_message_id": "null",
# "twilio_sent": false,
# "twilio_delivered": false,
# "twilio_message_id": false,
# "ghl_sent": false,
# "ghl_delivered": false,
# "sms_delivered": false,
# "sms_sent_at": "null"}]


API_KEY = os.getenv("TELNYX_API_KEY")
PUBLIC_KEY = os.getenv("TELNYX_PUBLIC_KEY")
failed_contacts = []
phone_numbers = ["+19099221711", "+19097688545", "+19097688030", "+19097688020", "+19096796336"]


def phone_number_generator(phone_numbers):
    index = 0
    while True:
        yield phone_numbers[index]
        index = (index + 1) % len(phone_numbers)


def check_telnyx_delivery_status(message_id):
    logger.info(f"{check_telnyx_delivery_status.__name__} -- CHECKING TELNYX DELIVERY STATUS FOR - {message_id}")

    response = requests.get(
        url=f"https://api.telnyx.com/v2/messages/{message_id}",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
    )

    status_code = response.status_code
    delivery_status = None
    logger.info(f"{check_telnyx_delivery_status.__name__} -- TELNYX STATUS CODE -- {status_code}")

    try:
        response_data = response.json()
        logger.info(f"{check_telnyx_delivery_status.__name__} -- TELNYX RESPONSE DATA -- {response_data}")

        delivery_status = response_data["data"]["to"][-1]["status"]
    except Exception as ex:
        logger.error(f"{check_telnyx_delivery_status.__name__} -- !!! TELNYX ERROR -- {ex}")

    return True if delivery_status == "delivered" else False, response.json()


def send_telnyx_sms(phone_number, sms_message: str, from_number):
    """
    sends single SMS message with Telnyx
    """
    phone_number_validated = utils.format_phone_number(phone_number)

    logger.info(f"{send_telnyx_sms.__name__} -- TELNYX - SENDING SMS TO - {phone_number} FROM - {from_number}")

    response = requests.post(
        url="https://api.telnyx.com/v2/messages",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={"type": "SMS", "text": f"{sms_message}", "from": from_number, "to": phone_number_validated},
    )

    status_code = response.status_code
    logger.info(f"{send_telnyx_sms.__name__} -- TELNYX - STATUS CODE -- {status_code}")

    result = {"success": True if status_code == 200 else False, "data": None, "message_id": None}

    try:
        response_data = response.json()
        logger.info(f"{send_telnyx_sms.__name__} -- TELNYX - RESPONSE DATA -- {response_data}")

        result["data"] = response_data["data"]
        result["message_id"] = response_data["data"]["id"]
    except Exception as ex:
        logger.error(f"{send_telnyx_sms.__name__} -- !!! TELNYX ERROR -- {ex}")

    return result["success"], result["message_id"]


def update_contacts(input_file):
    with open(input_file, "r") as f:
        data = json.load(f)
    for contact in data:
        contact["telnyx_sent"] = False
        contact["telnyx_sent_at"] = 0
        contact["telnyx_message_id"] = None
        contact["ghl_sent"] = False
        contact["ghl_sent_at"] = 0
        contact["ghl_conversation_id"] = None
    return data


def format_message(contact_name):
    sms_message = "Hi, how is your day?"
    if contact_name:
        sms_message = sms_message.replace(")", f" {contact_name}")
    else:
        sms_message = sms_message.replace(")", "")
    return sms_message


# def check_telnyx_delivery_status(message_id):
#     logger.info(f"{check_telnyx_delivery_status.__name__} -- CHECKING TELNYX DELIVERY STATUS FOR - {message_id}")
#
#     response = requests.get(
#         url=f"https://api.telnyx.com/v2/messages/{message_id}",
#         headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
#     )
#     status_code = response.status_code
#     delivery_status = None
#     logger.info(f"{check_telnyx_delivery_status.__name__} -- TELNYX STATUS CODE -- {status_code}")
#
#     try:
#         response_data = response.json()
#         logger.info(f"{check_telnyx_delivery_status.__name__} -- TELNYX RESPONSE DATA -- {response_data}")
#
#         delivery_status = response_data["data"]["to"][-1]["status"]
#     except Exception as ex:
#         logger.error(f"{check_telnyx_delivery_status.__name__} -- !!! TELNYX ERROR -- {ex}")
#
#     # return True if delivery_status == "delivered" else False
#     return response.json()


def main(input_file, output_file):
    phone_number_iterator = phone_number_generator(phone_numbers)
    raw_data = update_contacts(input_file)
    initial_contacts_count = len(raw_data)
    processed_contacts_count = 0

    with open(output_file, "w") as f:
        json.dump(raw_data, f, indent=4)

    for contact in raw_data:
        contact_id = contact.get("id", "")
        contact_name = contact.get("firstName", "")
        contact_phone = contact.get("phone")
        msg = format_message(contact_name)
        from_phone_number = next(phone_number_iterator)
        telnyx_sent_status, message_id = send_telnyx_sms(contact_phone, msg, from_phone_number)
        if telnyx_sent_status:
            contact["telnyx_sent"] = True
            contact["telnyx_sent_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            contact["telnyx_message_id"] = message_id

            ghl_sent_status, ghl_conversation_id = ghl_api.modify_ghl_conversation(contact_id, msg, "outbound")

            if ghl_sent_status:
                contact["ghl_sent"] = True
                contact["ghl_sent_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                contact["ghl_conversation_id"] = ghl_conversation_id

            processed_contacts_count += 1
            with open(output_file, "w") as f:
                json.dump(raw_data, f, indent=4)
                logger.info(f"{main.__name__} -- DATA DUMPED SUCCESSFULLY")

        else:
            failed_contacts.append(contact)

    with open("contacts/failed_contact.json", "w") as f:
        json.dump(failed_contacts, f, indent=4)

    end_info = {
        "initial_contacts_count": initial_contacts_count,
        "processed_contacts_count": processed_contacts_count,
        "failed_contacts_count": len(failed_contacts),
    }
    with open("contacts/processing_info.json", "w") as f:
        json.dump(end_info, f, indent=4)


if __name__ == "__main__":
    # main("contacts/data.json", "contacts/output_file")
    check_telnyx_delivery_status("40318f1a-b5a4-4515-8a01-dd85c7b23a46")
