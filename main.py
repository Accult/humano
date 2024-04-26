import ghl_api as update_token
import telnyx_api as send_message

input_file = "contacts/data.json"
output_file = "contacts/output_file"


def main():
    update_token.main_data_setup()
    send_message.main(input_file, output_file)


if __name__ == "__main__":
    main()
