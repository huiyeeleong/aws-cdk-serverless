#!/usr/bin/env python3
import os

from aws_cdk import core as cdk
from aws_cdk import core

from aws_cdk_serverless_rest_api.aws_cdk_serverless_rest_api_stack import AwsCdkServerlessRestApiStack


app = core.App()
AwsCdkServerlessRestApiStack(app, "AwsCdkServerlessRestApiStack",
    )

app.synth()
