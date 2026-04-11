#!/usr/bin/env python3
import aws_cdk as cdk

from stacks.network_stack import NetworkStack
from stacks.data_stack import DataStack
from stacks.app_stack import AppStack

app = cdk.App()

network = NetworkStack(app, "ThreeTierNetwork")
data = DataStack(app, "ThreeTierData", vpc=network.vpc)

app_stack = AppStack(
    app,
    "ThreeTierApp",
    vpc=network.vpc,
    uploads_bucket=data.uploads_bucket,
    metadata_table=data.metadata_table,
    app_secret=data.app_secret,
)

cdk.Tags.of(app_stack).add("Project", "ThreeTierDemo")

app.synth()