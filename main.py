import ghl_api
import telnyx_api as send_message

input_file = "contacts/data.json"
output_file = "contacts/processed_data.json"


def main():
    ghl_api.tokens_update()
    ghl_api.fetch_all_contacts()
    send_message.main(input_file, output_file)


if __name__ == "__main__":
    main()
