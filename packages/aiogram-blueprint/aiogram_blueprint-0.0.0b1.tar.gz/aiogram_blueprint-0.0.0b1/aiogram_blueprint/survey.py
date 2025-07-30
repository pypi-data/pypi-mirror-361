import typing as t

from InquirerPy import inquirer

QUESTIONS = {
    "run_type": "Select bot launch type:",
    "components": "Select components to include in your project:",
    "db_type": "Select database type:",
    "add_admin": "Do you want to add Web Admin Panel?",
    "admin_auth": "Select authentication type for Web Admin:"
}

CHOICES = {
    "run_type": ["Webhook", "Polling"],
    "components": ["Redis", "Database", "Scheduler"],
    "db_type": ["PostgreSQL", "MySQL", "SQLite"],
    "add_admin": ["Yes", "No"],
    "admin_auth": ["Telegram Auth", "TON Connect"]
}


def ask_run_type() -> t.Optional[str]:
    return inquirer.select(
        message=QUESTIONS["run_type"],
        choices=CHOICES["run_type"]
    ).execute()


def ask_components() -> t.Optional[t.List[str]]:
    return inquirer.checkbox(
        message=QUESTIONS["components"],
        choices=CHOICES["components"],
        instruction="(Use space to select, enter to confirm)",
        transformer=lambda result: ", ".join(result),
        pointer=">",
    ).execute()


def ask_db_type() -> t.Optional[str]:
    return inquirer.select(
        message=QUESTIONS["db_type"],
        choices=CHOICES["db_type"]
    ).execute()


def ask_add_admin() -> t.Optional[str]:
    return inquirer.select(
        message=QUESTIONS["add_admin"],
        choices=CHOICES["add_admin"]
    ).execute()


def ask_admin_auth() -> t.Optional[str]:
    return inquirer.select(
        message=QUESTIONS["admin_auth"],
        choices=CHOICES["admin_auth"]
    ).execute()


def run_survey() -> t.Dict[str, t.Any]:
    config: t.Dict[str, t.Any] = {}

    run_type = ask_run_type()
    config["use_webhook"] = run_type == "Webhook"

    selected_components = ask_components() or []
    config["use_redis"] = "Redis" in selected_components
    config["use_db"] = "Database" in selected_components
    config["use_scheduler"] = "Scheduler" in selected_components
    config["use_admin"] = False

    if config["use_db"]:
        db_type = ask_db_type()
        config["db_type"] = db_type
    else:
        config["db_type"] = None

    if config["use_webhook"] and config["use_db"]:
        add_admin = ask_add_admin()
        config["use_admin"] = add_admin == "Yes"

    if config["use_admin"]:
        admin_auth = ask_admin_auth()
        if admin_auth == "Telegram Auth":
            config["admin_auth"] = "telegram"
        else:
            config["admin_auth"] = "tonconnect"
    else:
        config["admin_auth"] = None

    return config
