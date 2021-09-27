#!/usr/bin/env python3
import os

from aws_cdk import core as cdk

from aws_cdk import core

from aws_cdk_serverless_dynamo_processor.aws_cdk_serverless_dynamo_processor_stack import AwsCdkServerlessDynamoProcessorStack


app = core.App()
AwsCdkServerlessDynamoProcessorStack(app, "AwsCdkServerlessDynamoProcessorStack")

app.synth()
