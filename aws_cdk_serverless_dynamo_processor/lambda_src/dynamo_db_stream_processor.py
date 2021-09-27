
# -*- coding: utf-8 -*-
""""""
import json
import logging
import os

import boto3

class global_args:
    """ Global statics """
    OWNER = "Hui"
    ENVIRONMENT = "production"
    MODULE_NAME = "Dynamodb-Stream-Processor"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


def set_logging(lv=global_args.LOG_LEVEL):
    """ Helper to enable logging """
    logging.basicConfig(level=lv)
    logger = logging.getLogger()
    logger.setLevel(lv)
    return logger


# Initialize Logger
logger = set_logging()


def lambda_handler(event, context):

    resp = {"status": False, "resp": ""}
    logger.info(f"Event: {json.dumps(event)}")

    resp = {"status": False, "TotalItems": {}, "Items": []}

    if not "Records" in event:
        resp = {"status": False, "error_message": "No Records found in Event"}
        return resp

    logger.debug(f"Event:{event}")
    for r in event.get("Records"):
        if r.get("eventName") == "INSERT":
            resp["Items"].append(r)

    if resp.get("Items"):
        resp["status"] = True
        resp["TotalItems"] = {"Received": len(
            event.get("Records")), "Processed": len(resp.get("Items"))}

    logger.info(f"resp: {json.dumps(resp)}")

    return resp


if __name__ == "__main__":
    lambda_handler({}, {})
