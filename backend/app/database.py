import os
import time

import psycopg
from dotenv import load_dotenv


# Load environment variables from backend/.env
BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

ENV_FILE = os.path.join(
    BASE_DIR,
    "backend",
    ".env"
)

load_dotenv(ENV_FILE)


def get_config_value(name, default=None):
    """
    Get configuration value.

    Priority:
    1. Streamlit Secrets when deployed
    2. Environment variables / .env when running locally
    """

    # Try Streamlit Secrets first
    try:
        import streamlit as st

        if name in st.secrets:
            return st.secrets[name]

    except Exception:
        pass

    # Fall back to .env / system environment
    return os.getenv(name, default)


def get_connection():
    """
    Create a PostgreSQL connection.

    Local development:
        Uses backend/.env

    Streamlit deployment:
        Uses Streamlit Secrets

    No database credentials or business values
    are hardcoded here.
    """

    host = get_config_value("DATABASE_HOST")
    port = get_config_value(
        "DATABASE_PORT",
        "5432"
    )
    database = get_config_value(
        "DATABASE_NAME",
        "postgres"
    )
    user = get_config_value(
        "DATABASE_USER"
    )
    password = get_config_value(
        "DATABASE_PASSWORD"
    )

    if not host:
        raise RuntimeError(
            "DATABASE_HOST is missing. "
            "Configure it in backend/.env "
            "or Streamlit Secrets."
        )

    if not user:
        raise RuntimeError(
            "DATABASE_USER is missing. "
            "Configure it in backend/.env "
            "or Streamlit Secrets."
        )

    if not password:
        raise RuntimeError(
            "DATABASE_PASSWORD is missing. "
            "Configure it in backend/.env "
            "or Streamlit Secrets."
        )

    last_error = None

    for attempt in range(3):

        try:
            return psycopg.connect(
                host=host,
                port=port,
                dbname=database,
                user=user,
                password=password,
                sslmode="require",
                connect_timeout=15,
            )

        except psycopg.OperationalError as error:

            last_error = error

            if attempt < 2:
                time.sleep(2)

    raise last_error