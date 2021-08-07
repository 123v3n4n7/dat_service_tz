from trainees_one.celery import celery_app
from django.core.mail import send_mail


@celery_app.task(ignore_result=False)
def send_mail_if_match(email, first_name, last_name):
    send_mail(
        "It's a Match!",
        f'Вы понравились {first_name} {last_name}',
        'from@yourdjangoapp.com',
        [f'{email}'],
        fail_silently=False,
    )
