import json

import boto3
from django.conf import settings
from django_vite.core.asset_loader import DjangoViteAppClient, ManifestClient


class S3ManifestClient(ManifestClient):
    # This is a custom manifest client that loads the manifest from an S3/R2 bucket
    def load_manifest(self):
        s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        )
        res = s3.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key="static/manifest.json")
        manifest_content = res["Body"].read()
        return json.loads(manifest_content)


class S3DjangoViteAppClient(DjangoViteAppClient):
    ManifestClient = S3ManifestClient
