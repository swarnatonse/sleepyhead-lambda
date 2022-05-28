import json
import csv
import boto3

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

def lambda_handler(event, context):
    sd_rows = construct_objects()
    sd_headers = ddb_S_fields + ddb_N_fields
    
    with open('sleep_data.csv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = sd_headers)
        writer.writerows(sd_rows)
        
    s3.upload_file('sleep_data.csv', 'sleep-data-swarnatonse', 'data/sleep_data.csv')
    

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "success",
            }
        ),
    }
    
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
                
    print(json.dumps(sd_rows))
    return sd_rows

        
def scan_ddb():
    ddb_response = ddb.scan(
            TableName='SleepData'
        )
    return ddb_response.get('Items')