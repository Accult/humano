from flask import Flask, request
import ghl_api

app = Flask(__name__)


#
# {'contacts': [{'id': 'qgptsVHCfguGnBub8GLk', 'locationId': 'Yj0B8PqpPjBZBwD91Lgq', 'contactName': 'egor yasinetskiy',
#                'firstName': 'egor', 'lastName': 'yasinetskiy', 'companyName': None, 'email': 'kkk@example.com',
#                'phone': '+19012375438', 'dnd': False, 'dndSettings': {}, 'type': 'lead', 'source': None,
#                'assignedTo': None, 'city': None, 'state': None, 'postalCode': None, 'address1': None,
#                'dateAdded': '2024-04-25T10:39:15.383Z', 'dateUpdated': '2024-04-25T14:09:11.176Z', 'dateOfBirth': None,
#                'businessId': None, 'tags': [], 'followers': [], 'country': 'US', 'website': None,
#                'additionalEmails': [],
#                'attributions': [{'utmSessionSource': 'CRM UI', 'isFirst': True, 'medium': 'manual'}],
#                'customFields': []}], 'meta': {'total': 1,
#                                               'nextPageUrl': 'https://services.leadconnectorhq.com/contacts/?query=%2B19012375438&locationId=Yj0B8PqpPjBZBwD91Lgq&startAfter=1714041555383&startAfterId=qgptsVHCfguGnBub8GLk',
#                                               'startAfterId': 'qgptsVHCfguGnBub8GLk', 'startAfter': 1714041555383,
#                                               'currentPage': 1, 'nextPage': '', 'prevPage': None},
#  'traceId': '02571e21-808a-4fea-947c-1e041984749a'}


@app.route("/api/v1/telnyx-response", methods=["POST"])
def webhook():
    # Отримуємо дані з вебхуку
    data = request.json
    data = [
        {
            "data": {
                "event_type": "message.finalized",
                "id": "e8b33d68-e65c-4394-852d-bc495d87d005",
                "occurred_at": "2024-04-29T10:17:42.574+00:00",
                "payload": {
                    "cc": [],
                    "completed_at": "2024-04-29T10:17:42.574+00:00",
                    "cost": {"amount": "0.0040", "currency": "USD"},
                    "direction": "outbound",
                    "encoding": "GSM-7",
                    "errors": [],
                    "from": {"carrier": "Telnyx", "line_type": "Wireless", "phone_number": "+19012375438"},
                    "id": "40318f29-5c3f-4689-aa8a-4f41c6d49178",
                    "media": [],
                    "messaging_profile_id": "40018f15-e2f3-4ec6-8390-c9ed22cb5605",
                    "organization_id": "2ea3868b-fef8-452f-8d8b-fb5ceb0e4c78",
                    "parts": 1,
                    "received_at": "2024-04-29T10:17:42.515+00:00",
                    "record_type": "message",
                    "sent_at": "2024-04-29T10:17:42.552+00:00",
                    "tags": [],
                    "text": "Lol",
                    "to": [
                        {
                            "carrier": "TELNYX LLC",
                            "line_type": "Pre-Paid Wireless",
                            "phone_number": "+19097688030",
                            "status": "delivered",
                        }
                    ],
                    "type": "SMS",
                    "valid_until": "2024-04-29T11:17:42.515+00:00",
                    "webhook_failover_url": "https://hook.us1.make.com/f77apspzg119xvp7cyb9tv4v0m1tdd8n",
                    "webhook_url": "",
                },
                "record_type": "event",
            },
            "meta": {"attempt": 1, "delivered_to": "https://hook.us1.make.com/f77apspzg119xvp7cyb9tv4v0m1tdd8n"},
        }
    ]

    sender_phone = data[0]["data"]["payload"]["from"]["phone_number"]
    message = data[0]["data"]["payload"]["text"]
    ghl_api.tokens_update()
    ghl_contact_id = ghl_api.get_contact_by_number(sender_phone)
    if ghl_contact_id:
        ghl_api.modify_ghl_conversation(ghl_contact_id, message)
        return "OK", 200

    return "ERROR"


if __name__ == "__main__":
    app.run(debug=True)
