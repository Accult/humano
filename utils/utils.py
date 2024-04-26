import logging

import phonenumbers


def format_phone_number(phone_number: str):
    """
    converts phone numbers to a desired format
    (012) 345-6789 -> +10123456789, etc.
    """
    phone_number_formatted = ""
    try:
        phone_number_formatted = phonenumbers.format_number(
            phonenumbers.parse(phone_number, "US"), phonenumbers.PhoneNumberFormat.E164
        )
        logging.info(
            f"{format_phone_number.__name__} -- FORMATTED PHONE NUMBER -- FROM - {phone_number} - TO - {phone_number_formatted}"
        )
    except Exception as ex:
        logging.warning(f"{format_phone_number.__name__} -- ! FAILED FORMATTING - {phone_number} - {ex}")
    return phone_number_formatted
