#!/usr/bin/env python3
import os

from aws_cdk import core as cdk
from aws_cdk import core

from aws_cdk_serverless_containerize_microservice.aws_cdk_serverless_containerize_microservice_stack import AwsCdkServerlessContainerizeMicroserviceStack


app = core.App()
AwsCdkServerlessContainerizeMicroserviceStack(app, "AwsCdkServerlessContainerizeMicroserviceStack")

app.synth()
