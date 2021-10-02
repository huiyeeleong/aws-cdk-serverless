from aws_cdk import core as cdk
from aws_cdk import (
    core,
     aws_ec2 as _ec2,
     aws_ecs as _ecs,
     aws_ecs_patterns as _ecs_patterns
)


class AwsCdkServerlessContainerFargateStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        # Create VPC for hosting the micro service
        vpc = _ec2.Vpc(
            self,
            "microServiceVpc",
            max_azs=2,
            nat_gateways=1
        )

        # Create Fargate Cluster inside the VPC
        micro_service_cluster = _ecs.Cluster(
            self,
            "microServiceCluster",
            vpc=vpc
        )

        # Deploy Container in the micro Service with an Application Load Balancer
        serverless_web_service = _ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "webService",
            cluster=micro_service_cluster,
            memory_limit_mib=1024,
            cpu=512,
            #docker image open source
            task_image_options={
                "image": _ecs.ContainerImage.from_registry("mystique/web-server"),
                "environment": {
                    "ENVIRONMENT": "PROD"
                }
            },
            desired_count=2
        )

        # Server Health Checks
        serverless_web_service.target_group.configure_health_check(path="/")

        # Output Web Service Url
        output_1 = core.CfnOutput(
            self,
            "webServiceUrl",
            value=f"{serverless_web_service.load_balancer.load_balancer_dns_name}",
            description="Access the web service url from your browser"
        )

