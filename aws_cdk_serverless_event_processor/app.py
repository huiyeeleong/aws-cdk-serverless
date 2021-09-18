#!/usr/bin/env python3
import os

from aws_cdk import core as cdk
from aws_cdk import core

from aws_cdk_serverless_event_processor.aws_cdk_serverless_event_processor_stack import AwsCdkServerlessEventProcessorStack


app = core.App()
AwsCdkServerlessEventProcessorStack(app, "AwsCdkServerlessEventProcessorStack",
    )

app.synth()
