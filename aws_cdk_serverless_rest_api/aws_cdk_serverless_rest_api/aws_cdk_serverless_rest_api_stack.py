from aws_cdk import core as cdk
from aws_cdk import (
    core,
    aws_dynamodb as _dynamodb,
    aws_lambda as _lambda,
    aws_logs as _logs,
    aws_apigateway as _apigateway
)
from jsii._kernel import _handle_callback


class AwsCdkServerlessRestApiStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        # Create dynamodb
        hui_dynamo =_dynamodb.Table(
            self,
            "apiDynamodbTable",
            partition_key = _dynamodb.Attribute(
                name = "_id",
                type = _dynamodb.AttributeType.STRING
            ),
            removal_policy = core.RemovalPolicy.DESTROY
        )

        #read lambda code
        try:
            with open("/Users/huiyeeleong/Desktop/aws-cdk-serverless/aws_cdk_serverless_rest_api/aws_cdk_serverless_rest_api/lambda_src/rest_api.py", 
            mode="r") as f: hui_fn_code = f.read()       
        except OSError:
            print("Unable to read the lambda function code")


        #deploy the lambda function
        hui_api_fn = _lambda.Function(
            self,
            "huiApiFunction",
            function_name = "hui_api_function",
            description = "Process Api event from API gatewat and ingest into dynamo db",
            runtime = _lambda.Runtime.PYTHON_3_7,
            handler = "index.lambda_handler",
            code = _lambda.InlineCode(
                hui_fn_code
            ),
            timeout = core.Duration.seconds(3),
            reserved_concurrent_executions = 1,
            environment = {
                "LOG_LEVEL" : "INFO",
                "DDB_TABLE_NAME" : f"{hui_dynamo.table_name}"
            }
        )


        #Add DynamoDb write permission to lambda function
        hui_dynamo.grant_read_write_data(hui_api_fn)

        #Create custom loggroup
        hui_log_group = _logs.LogGroup(
            self,
            "huiLogGroup",
            log_group_name=f"/aws/lamda/{hui_api_fn.function_name}",
            removal_policy=core.RemovalPolicy.DESTROY,
            retention=_logs.RetentionDays.ONE_DAY

        )

        #create API gateway fronted on lambda
        hui_api = _apigateway.LambdaRestApi(
            self,
            "huiapifrontend",
            rest_api_name = "api-frontend",
            handler = hui_api_fn,
            proxy = False
        )


        user_name = hui_api.root.add_resource("{user_name}")
        add_user_likes = user_name.add_resource("{likes}")
        add_user_likes.add_method("GET")


        #output api gateway url
        output = core.CfnOutput(
            self,
            "API_url",
            value=f"{add_user_likes.url}",
            description="User browser to access this url, Replace {user_name} and {likes} with your own value"
        )


