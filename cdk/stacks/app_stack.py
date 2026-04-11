import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_autoscaling as autoscaling,
    aws_elasticloadbalancingv2 as elbv2,
    aws_iam as iam,
    aws_s3 as s3,
    aws_dynamodb as dynamodb,
    aws_secretsmanager as secretsmanager,
)
from constructs import Construct


class AppStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc: ec2.IVpc,
        uploads_bucket: s3.IBucket,
        metadata_table: dynamodb.ITable,
        app_secret: secretsmanager.ISecret,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Security groups
        alb_sg = ec2.SecurityGroup(
            self,
            "AlbSG",
            vpc=vpc,
            allow_all_outbound=True,
            description="ALB security group",
        )
        alb_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80), "HTTP from internet")

        ec2_sg = ec2.SecurityGroup(
            self,
            "Ec2SG",
            vpc=vpc,
            allow_all_outbound=True,
            description="App instances security group",
        )
        ec2_sg.add_ingress_rule(alb_sg, ec2.Port.tcp(80), "HTTP from ALB")

        # IAM role for EC2
        role = iam.Role(
            self,
            "AppRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
        )

        uploads_bucket.grant_read_write(role)
        metadata_table.grant_read_write_data(role)
        app_secret.grant_read(role)

        role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore")
        )

        # User data
        repo_url = "https://github.com/Mogeskebede/aws-three-tier-app.git"  # change this
        user_data = ec2.UserData.for_linux()
        user_data.add_commands(
            "yum update -y",
            "yum install -y python3 git",
            "pip3 install --upgrade pip",
            "cd /home/ec2-user",
            f"git clone {repo_url} app",
            "cd app/webapp",
            "pip3 install -r requirements.txt",
            f"export AWS_REGION={self.region}",
            f"export UPLOADS_BUCKET={uploads_bucket.bucket_name}",
            f"export METADATA_TABLE={metadata_table.table_name}",
            f"export APP_SECRET_ID={app_secret.secret_name}",
            "uvicorn app:app --host 0.0.0.0 --port 80 &",
        )

        # Launch template
        launch_template = ec2.LaunchTemplate(
            self,
            "AppLaunchTemplate",
            instance_type=ec2.InstanceType("t3.micro"),
            machine_image=ec2.MachineImage.latest_amazon_linux2(),
            security_group=ec2_sg,
            role=role,
            user_data=user_data,
        )

        # Auto Scaling Group
        asg = autoscaling.AutoScalingGroup(
            self,
            "AppASG",
            vpc=vpc,
            launch_template=launch_template,
            min_capacity=2,
            desired_capacity=2,
            max_capacity=4,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
        )

        # ALB
        alb = elbv2.ApplicationLoadBalancer(
            self,
            "AppALB",
            vpc=vpc,
            internet_facing=True,
            security_group=alb_sg,
        )

        listener = alb.add_listener("HttpListener", port=80)

        listener.add_targets(
            "AppFleet",
            port=80,
            targets=[asg],
            health_check=elbv2.HealthCheck(
                path="/health",
                interval=cdk.Duration.seconds(30),
                timeout=cdk.Duration.seconds(5),
                healthy_threshold_count=2,
                unhealthy_threshold_count=5,
            ),
        )

        cdk.CfnOutput(self, "AlbDnsName", value=alb.load_balancer_dns_name)