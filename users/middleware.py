import logging
from django.core.mail import send_mail
from django.core import mail

logger = logging.getLogger(__name__)

class EmailDebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Настраиваем логирование в консоль
        logging.basicConfig(level=logging.DEBUG)

    def __call__(self, request):
        # Перехватываем все исходящие email
        old_send_mail = mail.send_mail

        def new_send_mail(*args, **kwargs):
            logger.debug("Attempting to send mail:")
            logger.debug(f"Subject: {args[0]}")
            logger.debug(f"Message: {args[1]}")
            logger.debug(f"From: {args[2]}")
            logger.debug(f"To: {args[3]}")
            return old_send_mail(*args, **kwargs)

        mail.send_mail = new_send_mail

        response = self.get_response(request)
        
        # Восстанавливаем оригинальную функцию
        mail.send_mail = old_send_mail
        
        return response 