#!/usr/bin/env python3
import os

from aws_cdk import core as cdk

from aws_cdk import core

from aws_cdk_serverless_stream_processor.aws_cdk_serverless_stream_processor_stack import AwsCdkServerlessStreamProcessorStack


app = core.App()
AwsCdkServerlessStreamProcessorStack(app, "AwsCdkServerlessStreamProcessorStack")

app.synth()
