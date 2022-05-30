import json
import csv
import boto3
import base64
from constants import ddb_S_fields, ddb_N_fields, sleep_report_fields
from operator import itemgetter
from datetime import datetime

s3 = boto3.client('s3')
ddb = boto3.client('dynamodb')


def lambda_handler(event, context):
    response = {
        "message": "success"
    }
    if event.get("source") and event.get("source") == "aws.events":
        print("Updating sleep data csv")
        upload_sleep_data()
    if event.get("body"):
        print("Updating sleep report")
        request_input = json.loads(base64.b64decode(event.get("body")))
        report_key = upload_sleep_report(request_input)
        response['report_key'] = report_key

    return {
        "statusCode": 200,
        "body": json.dumps(response),
    }
    
def upload_sleep_data():
    items = scan_ddb()
    sd_rows = construct_objects(items)
    sd_headers = ddb_S_fields + ddb_N_fields
    
    with open('/tmp/sleep_data.csv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = sd_headers)
        writer.writerows(sd_rows)
        
    s3.upload_file('/tmp/sleep_data.csv', 'sleep-data-swarnatonse', 'data/sleep_data.csv')
    
def construct_objects(items):
    sd_rows = []
    for item in items:
        sd_row = dict()
        for ddb_s_field in ddb_S_fields:
            if item.get(ddb_s_field):
                sd_row[ddb_s_field] = item.get(ddb_s_field).get('S').replace(',', ';') 
        for ddb_n_field in ddb_N_fields:
            if item.get(ddb_n_field):
                sd_row[ddb_n_field] = item.get(ddb_n_field).get('N')
        sd_rows.append(sd_row)

    return sd_rows
    
def upload_sleep_report(request_input):
    items = scan_ddb_filtered(request_input)
    sd_objs = construct_objects(items)
    sorted_sd_objs = sorted(sd_objs, key=itemgetter('DayId')) 
    sr_rows = []
    
    for field, value in sleep_report_fields.items():
        row = [value]
        for sd_obj in sorted_sd_objs:
            if sd_obj.get(field):
                if field == "DayId":
                    dateobj = datetime.strptime(sd_obj.get(field), "%Y-%m-%d")
                    row.append(dateobj.strftime("%A | %d-%m-%Y"))
                else:
                    row.append(sd_obj.get(field))
            else:
                row.append("-")
        sr_rows.append(row)
        
    filename = 'sleep_report_' + request_input.get('startdate') + '_to_' + request_input.get('enddate') + '.csv'
        
    with open('/tmp/sleep_report.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(sr_rows)
    s3.upload_file('/tmp/sleep_report.csv', 'sleep-data-swarnatonse', 'reports/' + filename)
    
    return filename
        
def scan_ddb():
    ddb_response = ddb.scan(
            TableName='SleepData'
        )
    return ddb_response.get('Items')
    
def scan_ddb_filtered(request_input):
    filter_expression = "#d between :d1 and :d2"
    expression_attribute_names = { "#d": "DayId" }
    expression_attribute_values = {":d1":{"S":request_input.get("startdate")},
                                    ":d2":{"S":request_input.get("enddate")}}
    ddb_response = ddb.scan(
            TableName='SleepData',
            FilterExpression=filter_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values
        )
    return ddb_response.get('Items')