import logging
import time
from sqlalchemy import text
from alembic.config import Config
from alembic import command

from src.core.database import engine, SessionLocal
from src.initial_data import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60
wait_seconds = 2


def wait_for_db() -> None:
    """Čeká na dostupnost relační databáze."""
    logger.info("Čekám na navázání spojení s databází...")
    for attempt in range(1, max_tries + 1):
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            logger.info("Spojení s databází úspěšně navázáno!")
            return
        except Exception as e:
            logger.warning(
                f"Pokus {attempt}/{max_tries}: Databáze ještě není připravena ({e}). Čekám {wait_seconds}s..."
            )
            time.sleep(wait_seconds)
    raise RuntimeError("Nepodařilo se připojit k databázi v časovém limitu.")


def run_migrations() -> None:
    """Spustí všechny čekající Alembic migrace."""
    logger.info("Aplikuji databázové migrace (alembic upgrade head)...")
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    logger.info("Databázové migrace byly úspěšně aplikovány.")


def seed_database() -> None:
    """Zajistí existenci výchozích seed dat."""
    logger.info("Kontroluji výchozí seed data...")
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()
    logger.info("Seed data připravena.")


def main() -> None:
    wait_for_db()
    run_migrations()
    seed_database()
    logger.info("Pre-start inicializace kompletně dokončena.")


if __name__ == "__main__":
    main()
