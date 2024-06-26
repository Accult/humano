import ghl_api
import telnyx_api as send_message
from logging_config import setup_logger

input_file = "contacts/data.json"
output_file = "contacts/processed_data.json"


def main():
    ghl_api.tokens_update()
    ghl_api.fetch_all_contacts()
    send_message.main(input_file, output_file)


if __name__ == "__main__":
    logger = setup_logger("ghl_logger")
    main()
