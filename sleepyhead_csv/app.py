import json
import csv
import boto3
from operator import itemgetter
from datetime import datetime

s3 = boto3.client('s3')
ddb = boto3.client('dynamodb')

ddb_S_fields = [
    'DayId',
    'PhoneDownTime',
    'Activities',
    'Bedtime',
    'LightsOutTime',
    'HowLongToSleep',
    'WakeUpCount',
    'WakeUpDuration',
    'FinalWakeUpTime',
    'AriseTime',
    'SleepNotes',
    'FitbitHours',
    'FitbitMins',
    'FitbitScore',
    'ExerciseTime',
    'Exercises',
    'Stress',
    'Mood',
    'MorningEnergy',
    'ForenoonEnergy',
    'AfternoonEnergy',
    'EveningEnergy'
    ]
    
ddb_N_fields = [
    'SleepDurationInMinutes',
    'IdleWakeupDurationInMinutes',
    'AverageEnergyScore'
    ]
    
sleep_report_fields = [
    'DayId',
    'Bedtime',
    'LightsOutTime',
    'HowLongToSleep',
    'WakeUpCount',
    'WakeUpDuration',
    'FinalWakeUpTime',
    'AriseTime',
    'SleepNotes',  
    ]

def lambda_handler(event, context):
    
    upload_sleep_data()
    upload_sleep_report()

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "success",
            }
        ),
    }
    
def upload_sleep_data():
    sd_rows = construct_objects()
    sd_headers = ddb_S_fields + ddb_N_fields
    
    with open('/tmp/sleep_data.csv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = sd_headers)
        writer.writerows(sd_rows)
        
    s3.upload_file('/tmp/sleep_data.csv', 'sleep-data-swarnatonse', 'data/sleep_data.csv')
    
def construct_objects():
    items = scan_ddb()
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
    
def upload_sleep_report():
    sd_objs = construct_objects()
    sorted_sd_objs = sorted(sd_objs, key=itemgetter('DayId')) 
    sr_rows = []
    
    for field in sleep_report_fields:
        row = [field]
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
        
    print(json.dumps(sr_rows))
        
    with open('sleep_report.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(sr_rows)
    s3.upload_file('sleep_report.csv', 'sleep-data-swarnatonse', 'reports/sleep_report.csv')
        
def scan_ddb():
    ddb_response = ddb.scan(
            TableName='SleepData'
        )
    return ddb_response.get('Items')