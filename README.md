Звичайно, ось англомовна версія README файлу:

# Sms machine


1. Clone the repository from GitHub:

```bash
git clone <repository_url>
cd <project_directory>
```

2. Execute the automation script:

```bash
bash automation_script.sh
```

This will set up the virtual environment, install required packages, create the `.env` using .env-example template

3. After completing the setup, you can run the main script to start sending messages to contacts:

```bash
python main.py
```

4. Additionally, you can run the webhook receiver using the following command:

```bash
python webhook_receiver.py
```

Ensure that you have configured the necessary environment variables in the `.env` file before running the scripts.
