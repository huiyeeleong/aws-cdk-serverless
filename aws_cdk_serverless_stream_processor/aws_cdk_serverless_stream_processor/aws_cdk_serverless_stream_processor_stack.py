from typing_extensions import runtime
from aws_cdk import core as cdk
from aws_cdk import (
    core,
    aws_kinesis as _kinesis,
    aws_s3 as _s3,
    aws_lambda as _lambda,
    aws_iam as _iam,
    aws_lambda_event_sources as _lambda_event_sources,
    aws_logs as _logs
)
from jsii._kernel import _handle_callback


class AwsCdkServerlessStreamProcessorStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        #Create kinesis data stream
        stream_data_pipe = _kinesis.Stream(
            self,
            "streamDataPipe",
            retention_period = core.Duration.hours(24),
            shard_count = 1,
            stream_name = "data_pipe"
        )

        #create s3 bucket to store steaming events
        stream_data_store = _s3.Bucket(
            self,
            "streamDataLake",
            removal_policy = core.RemovalPolicy.DESTROY
        )

        #read lambda function for stream
        try:
            with open("/Users/huiyeeleong/Desktop/aws-cdk-serverless/aws_cdk_serverless_stream_processor/lambda_src/stream_record_consumer.py", 
            mode="r") as f: stream_consumer_fn_code = f.read()
        except OSError:
            print("Unable to read lambda function code")

        #create lambda function for stream
        stream_consumer_fn = _lambda.Function(
            self,
            "streamConsumerFn",
            function_name = "stream_consumer_fn",
            description = "Process streaming data events from kinesis and store in s3",
            runtime = _lambda.Runtime.PYTHON_3_7,
            handler = "index.lambda_handler",
            code = _lambda.InlineCode(
                stream_consumer_fn_code
            ),
            timeout = core.Duration.seconds(3),
            reserved_concurrent_executions = 1,
            environment = {
                "LOG_LEVEL": "INFO",
                "BUCKET_NAME" : f"{stream_data_store.bucket_name}"
            }
        )

        #Update lambda permission to use the stream
        stream_data_pipe.grant_read(stream_consumer_fn)

        #Add permission to lambda to write to s3
        rolestatement1 = _iam.PolicyStatement(
            effect = _iam.Effect.ALLOW,
            resources= [
                f"{stream_data_store.bucket_arn}"
            ],
            actions =[
                "s3:PutObject"
            ]
        )
        #Add the policy to role
        rolestatement1.sid = "AllowLambdaToWriteToS3"
        stream_consumer_fn.add_to_role_policy(rolestatement1)

        #Create custom loggroup for consumer
        stream_consumer_log = _logs.LogGroup(
            self,
            "streamConsumerLogGroup",
            log_group_name = f"/aws/lambda/{stream_consumer_fn.function_name}",
            removal_policy = core.RemovalPolicy.DESTROY,
            retention = _logs.RetentionDays.ONE_DAY
        )

        # Create New Kinesis Event Source
        stream_data_pipe_event_source = _lambda_event_sources.KinesisEventSource(
            stream=stream_data_pipe,
            starting_position=_lambda.StartingPosition.LATEST,
            batch_size=1
        )


        # Attach Kinesis Event Source To Lambda
        stream_consumer_fn.add_event_source(stream_data_pipe_event_source)

        
        # Read Lambda Code for producer
        try:
            with open("/Users/huiyeeleong/Desktop/aws-cdk-serverless/aws_cdk_serverless_stream_processor/lambda_src/stream_data_producer.py", 
            mode="r") as f: data_producer_fn_code = f.read()
        except OSError:
            print("Unable to read lambda function code")

        # Deploy the lambda function producer
        data_producer_fn = _lambda.Function(
            self,
            "streamDataProducerFn",
            function_name="data_producer_fn",
            description="Produce streaming data events and push to Kinesis stream",
            runtime=_lambda.Runtime.PYTHON_3_7,
            handler="index.lambda_handler",
            code=_lambda.InlineCode(
                data_producer_fn_code
            ),
            timeout=core.Duration.seconds(60),
            reserved_concurrent_executions=1,
            environment={
                "LOG_LEVEL":"INFO",
                "STREAM_NAME":f"{stream_data_pipe.stream_name}"
            }
        )


        # Grant our Lambda Producer privileges to write to Kinesis Data Stream
        stream_data_pipe.grant_read_write(data_producer_fn)


        # Create Custom Loggroup for Producer
        data_producer_lg = _logs.LogGroup(
            self,
            "dataProducerLogGroup",
            log_group_name=f"/aws/lambda/{data_producer_fn.function_name}",
            removal_policy=core.RemovalPolicy.DESTROY,
            retention=_logs.RetentionDays.ONE_DAY
        )



