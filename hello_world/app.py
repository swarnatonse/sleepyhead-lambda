import json


def lambda_handler(event, context):
    print(event)
    print('This works?')

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "hello world, this is a scheduled event test",
            }
        ),
    }
