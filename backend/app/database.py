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


def get_connection():
    """
    Create a PostgreSQL connection using the
    credentials stored in backend/.env.

    No database credentials or business values
    are hardcoded here.
    """

    host = os.getenv("DATABASE_HOST")
    port = os.getenv("DATABASE_PORT", "5432")
    database = os.getenv(
        "DATABASE_NAME",
        "postgres"
    )
    user = os.getenv(
        "DATABASE_USER"
    )
    password = os.getenv(
        "DATABASE_PASSWORD"
    )

    if not host:
        raise RuntimeError(
            "DATABASE_HOST is missing from backend/.env"
        )

    if not user:
        raise RuntimeError(
            "DATABASE_USER is missing from backend/.env"
        )

    if not password:
        raise RuntimeError(
            "DATABASE_PASSWORD is missing from backend/.env"
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