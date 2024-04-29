from flask import Flask, request

app = Flask(__name__)


@app.route("/f77apspzg119xvp7cyb9tv4v0m1tdd8n", methods=["POST"])
def webhook():
    # Отримуємо дані з вебхуку
    data = request.json

    print("Отримано дані з вебхуку:")
    print(data)

    return "OK", 200


if __name__ == "__main__":
    app.run(debug=True)
