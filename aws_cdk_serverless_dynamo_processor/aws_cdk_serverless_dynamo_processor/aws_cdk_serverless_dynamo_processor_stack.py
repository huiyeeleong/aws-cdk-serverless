from aws_cdk import core as cdk
from aws_cdk import (
    core,
    aws_lambda as _lambda,
    aws_dynamodb as _dynamodb,
    aws_iam as _iam,
    aws_lambda_event_sources as _lambda_event_sources
)


class AwsCdkServerlessDynamoProcessorStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        #Create dynamoDB for backend
        api_db = _dynamodb.Table(
            self,
            "apiDBTable",
            partition_key = _dynamodb.Attribute(
                name = "_id",
                type = _dynamodb.AttributeType.STRING
            ),
            stream = _dynamodb.StreamViewType.NEW_AND_OLD_IMAGES
        )

        #Read local lambda code
        try:
            with open("/Users/huiyeeleong/Desktop/aws-cdk-serverless/aws_cdk_serverless_dynamo_processor/lambda_src/dynamo_db_stream_processor.py", 
            mode="r") as f: db_stream_processor_fn_code = f.read()
        except OSError:
            print("Unable to read lambda function code")

        #Create lambda function
        db_stream_processor_fn = _lambda.Function(
            self,
            "dbStreamProcessorFn",
            function_name="db_stream_processor_fn",
            description="Process DDB Streaming data events",
            runtime=_lambda.Runtime.PYTHON_3_7,
            handler="index.lambda_handler",
            code=_lambda.InlineCode(
                db_stream_processor_fn_code
            ),
            timeout=core.Duration.seconds(3),
            reserved_concurrent_executions=1,
            environment={
                "LOG_LEVEL": "INFO"
            }
        )
        # Create New DDB Stream Event Source
        db_stream_event_source = _lambda_event_sources.DynamoEventSource(
            table=api_db,
            starting_position=_lambda.StartingPosition.TRIM_HORIZON,
            bisect_batch_on_error=True
        )

        # Attach DDB Event Source As Lambda Trigger
        db_stream_processor_fn.add_event_source(db_stream_event_source)

