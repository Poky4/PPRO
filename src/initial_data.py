import logging
from sqlalchemy.orm import Session
from src.core.config import settings
from src.core.database import SessionLocal
from src.domain.models.user import UserRole
from src.schemas.user import UserCreate
from src.services.user_service import UserService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db(db: Session) -> None:
    """Inicializuje výchozího administrátora, pokud ještě v databázi neexistuje."""
    user = UserService.get_by_username(db, settings.FIRST_SUPERUSER_USERNAME)
    if not user:
        logger.info(
            f"Vytvářím výchozího administrátora: {settings.FIRST_SUPERUSER_USERNAME}"
        )
        user_in = UserCreate(
            username=settings.FIRST_SUPERUSER_USERNAME,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            email=settings.FIRST_SUPERUSER_EMAIL,
            full_name=settings.FIRST_SUPERUSER_FULLNAME,
            role=UserRole.ADMIN,
            is_active=True,
        )
        UserService.create(db, user_in)
        logger.info("Výchozí administrátor byl úspěšně vytvořen.")
    else:
        logger.info(
            f"Výchozí administrátor '{settings.FIRST_SUPERUSER_USERNAME}' již existuje. Přeskakuji inicializaci."
        )


def main() -> None:
    logger.info("Zahajuji kontrolu seed dat...")
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()
    logger.info("Kontrola seed dat dokončena.")


if __name__ == "__main__":
    main()
