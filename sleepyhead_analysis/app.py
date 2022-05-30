import json
import boto3
from datetime import datetime, timedelta

athena = boto3.client('athena')

def lambda_handler(event, context):
    print(event)
    
    query_execution_id = run_query()
    resultSet = get_query_result(query_execution_id)

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "success",
            }
        ),
    }
    
def run_query():
    query_string = "select * from sleepyhead.sleepdata where dayid > \'2022-05-22\'"
    response = athena.start_query_execution(
            QueryString=query_string,
            ResultConfiguration={
                'OutputLocation': 's3://sleep-data-swarnatonse/query_results/',
                'EncryptionConfiguration': {
                    'EncryptionOption': 'SSE_S3'
                }
            },
            WorkGroup='primary'
        )
    return response.get('QueryExecutionId')

def get_query_result(query_execution_id):
    query_exec_info = athena.get_query_execution(
            QueryExecutionId=query_execution_id
        )
    query_exec_state = query_exec_info.get('QueryExecution').get('Status').get('State')
        
    while query_exec_state in ['QUEUED', 'RUNNING']:
        query_exec_info = athena.get_query_execution(
            QueryExecutionId=query_execution_id
        )
        query_exec_state = query_exec_info.get('QueryExecution').get('Status').get('State')
        
    if query_exec_state in ['FAILED', 'CANCELLED']:
        print("Query %s unsuccessful" % query_execution_id)
        return None
    else:
        response = athena.get_query_results(
                        QueryExecutionId=query_execution_id,
                        MaxResults=365
                    )
        return response.get('ResultSet').get('Rows')
