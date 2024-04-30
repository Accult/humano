# Sms machine


1. Clone the repository from GitHub:

```bash
git clone <repository_url>
cd <project_directory>
```

2. Create virtual environment and install all required packages:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

This will set up the virtual environment, now create the `.env` using .env-example template

3. After completing the setup, you can run the main script to start sending messages to contacts:

```bash
python main.py
```

4. Additionally, you can run the webhook receiver using the following command:

```bash
python webhook_receiver.py
```

Ensure that you have configured the necessary environment variables in the `.env` file before running the scripts.
