from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Run deployment tasks including migrations'

    def handle(self, *args, **options):
        self.stdout.write('Starting deployment process...')
        
        try:
            # Check database connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            self.stdout.write(self.style.SUCCESS('Database connection successful'))
            
            # Run migrations
            self.stdout.write('Running database migrations...')
            call_command('migrate', verbosity=1)
            self.stdout.write(self.style.SUCCESS('Migrations completed successfully'))
            
            # Collect static files (if needed)
            self.stdout.write('Collecting static files...')
            call_command('collectstatic', '--noinput', verbosity=1)
            self.stdout.write(self.style.SUCCESS('Static files collected'))
            
            self.stdout.write(self.style.SUCCESS('Deployment completed successfully'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Deployment failed: {str(e)}'))
            logger.error(f'Deployment failed: {str(e)}')
            raise
