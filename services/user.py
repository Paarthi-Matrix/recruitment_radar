import logging

logger = logging.getLogger("log")


class User:
    @staticmethod
    def create_user(user_name: str, email: str):
        # Add logic to create here
        logger.info(f"user_name: {user_name}...email: {email}")
        return user_name, email

