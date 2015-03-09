from django.contrib.auth import get_user_model
from django.core.management import BaseCommand


class Command(BaseCommand):

    help = 'Assign admin by email for exist user in system'

    def handle(self, *args, **options):

        User = get_user_model()

        for email in args:
            try:
                user = User.objects.get(email=email)
                user.is_staff = True
                user.is_superuser = True
                user.set_password(email)
                user.save()
            except User.DoesNotExist:
                print '%s does not exist' % email
