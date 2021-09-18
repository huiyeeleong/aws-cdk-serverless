from aws_cdk import core as cdk
from aws_cdk import (
    core,
    aws_s3 as _s3,
    aws_dynamodb as _dynamodb,
    aws_lambda as _lambda,
    aws_logs as _logs,
    aws_s3_notifications as _s3_notifications
)

class AwsCdkServerlessEventProcessorStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        #Create s3 bucket
        hui_bucket = _s3.Bucket(
            self,
            "huibucket",
            versioned= True
        )

        #Create dynamodb
        hui_dynamodb_table = _dynamodb.Table(
            self,
            "huiDynamoDBTable",
            table_name= "huiDynamoDbTable",
            partition_key = _dynamodb.Attribute(
                name = "_id",
                type = _dynamodb.AttributeType.STRING
            ),
        removal_policy = core.RemovalPolicy.DESTROY
        )

        #Read lambda function
        try:
            with open ("/Users/huiyeeleong/Desktop/aws-cdk-serverless/aws_cdk_serverless_event_processor/lambda_src/s3_event_processor.py",
            mode="r") as f: hui_processor_fn = f.read()
        except OSError:
            print("Unable to read the lambda code")

        
        #Create lambda function
        hui_processor_lambda_fn = _lambda.Function(
            self,
            "huiProcessorFn",
            function_name= "hui_processor_fn",
            description = "Processor s3 event to store in DynamoDB",
            runtime = _lambda.Runtime.PYTHON_3_7,
            handler = "index.lambda_handler",
            code= _lambda.InlineCode(
                hui_processor_fn
            ),
            timeout = core.Duration.seconds(3),
            reserved_concurrent_executions=1,
            environment={
                "LOG_LEVEL": "INFO",
                "DDB_TABLE_NAME": f"{hui_dynamodb_table.table_name}"
            }
        )

        #Add dynamodb permission to lambda function
        hui_dynamodb_table.grant_read_write_data(hui_processor_lambda_fn)

        #Create custom log group
        hui_processor_log = _logs.LogGroup(
            self,
            "huiprocessorloggroup",
            log_group_name =f"/aws/lambda/{hui_processor_lambda_fn.function_name}",
            removal_policy = core.RemovalPolicy.DESTROY,
            retention = _logs.RetentionDays.ONE_DAY

        )

        #Create s3 notification for lambda function
        hui_lambda_notification = _s3_notifications.LambdaDestination(
            hui_processor_lambda_fn
        )

        #Assign notifcation for the s3 event type (ex:object created)
        hui_bucket.add_event_notification(
            _s3.EventType.OBJECT_CREATED, hui_lambda_notification
        )
    
