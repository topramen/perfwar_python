import json
import boto3
import botocore
import hashlib
from os import getenv
from aws_lambda_powertools import Logger, Tracer, Metrics
from boto3.dynamodb.conditions import Key
from aws_lambda_powertools import single_metric
from aws_lambda_powertools.metrics import MetricUnit

logger = Logger()
tracer = Tracer()
metrics = Metrics(namespace="PerfWar", service="PythonTest")

table_name = getenv('Table')
resource = boto3.resource('dynamodb')
table = resource.Table(table_name)


@metrics.log_metrics(capture_cold_start_metric=True)
@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def lambda_handler(event, context):
    # with single_metric(name="ColdStart", unit=MetricUnit.Count, value=1, namespace="PerfWar") as metric:
    #     metrics.add_dimension(name="function_name", value=context.function_name)
    #     metrics.add_dimension(name="version", value="50")
    if event['httpMethod'] == 'POST':
        logger.info("Inside POST Handler")
        return post_handler(event, context)
    else:
        logger.info("Inside GET Handler")
        return get_handler(event, context)
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "not much has happened"
        }),
    }

def post_handler(event, context):
    payload = json.loads(event['body'])
    digest = _hashme(payload['document'])
    logger.info(f"The digest is {digest}")
    payload['hash'] = digest

    try:
        table.put_item(Item=payload, ConditionExpression=f"attribute_not_exists(ID)")
    except botocore.exceptions.ClientError as e:
        return {
            # "statusCode": 409,
            "statusCode": 209,
            "body": json.dumps({
                "id": payload['ID'],
                "message": "object already exists"
            }),
        }
    return {
        "statusCode": 201,
        "body": json.dumps({
            "id": payload['ID'],
            "hash": digest
        }),
    }

def get_handler(event, context):
    id = event['queryStringParameters']['id']

    response = table.query(
        KeyConditionExpression=Key('ID').eq(id)
    )
    items = response.get("Items", None)
    logger.info(f"The items are {items}")
    if items:    
        return {
            "statusCode": 200,
            "body": json.dumps(items[0]),
        }
    else:
                return {
            # "statusCode": 404,
            "statusCode": 204,
            "body": json.dumps({
                "id": id,
                "message": "object not found"
            }),
        }

def _hashme(document):
    sha = hashlib.sha256()
    sha.update(document.encode())
    return sha.hexdigest()