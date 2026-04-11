import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_s3 as s3,
    aws_dynamodb as dynamodb,
    aws_secretsmanager as secretsmanager,
)
from constructs import Construct


class DataStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, vpc: ec2.IVpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.uploads_bucket = s3.Bucket(
            self,
            "UploadsBucket",
            versioned=False,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        self.metadata_table = dynamodb.Table(
            self,
            "MetadataTable",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING,
            ),
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        # Secret for bearer token (JSON: {"bearer_token": "YOUR_TOKEN"})
        self.app_secret = secretsmanager.Secret(
            self,
            "AppAuthSecret",
            secret_name="three-tier-app/auth",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template='{"bearer_token": "CHANGE_ME"}',
                generate_string_key="ignore_me",
            ),
        )