import os
import mimetypes
import boto3
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from store.models import Product


class Command(BaseCommand):
    help = 'Upload existing product images to the configured S3-backed storage and refresh their URLs'

    def handle(self, *args, **options):
        client = boto3.client(
            's3',
            region_name=settings.AWS_S3_REGION_NAME,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        )

        for product in Product.objects.exclude(image='').exclude(image__isnull=True):
            if not product.image:
                continue

            name = product.image.name
            local_path = os.path.join('media', name)
            if not os.path.exists(local_path):
                self.stdout.write(self.style.WARNING(f'Skipped missing local file: {name}'))
                continue

            mime_type, _ = mimetypes.guess_type(local_path)
            if mime_type is None:
                mime_type = 'application/octet-stream'

            with open(local_path, 'rb') as f:
                client.put_object(
                    Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                    Key=name,
                    Body=f,
                    ContentType=mime_type,
                    ACL='public-read',
                )

            self.stdout.write(self.style.SUCCESS(f'Uploaded {name}'))
            self.stdout.write(self.style.SUCCESS(f'Available: {settings.MEDIA_URL}{name}'))
