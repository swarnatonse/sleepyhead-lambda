import json
import boto3
from datetime import datetime, timedelta

ddb_client = boto3.client('dynamodb')


def lambda_handler(event, context):
    if event.get("Records"):
        process_ddb_records(event)
    else: 
        process_scheduled_event(event)
        

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "success",
            }
        ),
    }
    
def process_ddb_records(event):
    print("This is a ddb record")
    records = event.get("Records")
    for record in records:
        eventName = record.get("eventName")
        ddb = record.get("dynamodb")
        key = ddb.get("Keys").get("DayId").get("S")
        if eventName == "INSERT" or eventName == "MODIFY":
            sleep_duration = None
            idle_wakeup_duration = None
            average_energy_score = None
            newImage = ddb.get("NewImage")
            if is_sleep_duration_update_required(ddb):
                print("Sleep duration update required for key " + key)
                sleep_duration = update_total_sleep_duration(newImage)
            if is_idle_wakeup_duration_update_required(ddb):
                print("Idle wakeup time update required for key " + key)
                idle_wakeup_duration = update_idle_wakeup_duration(newImage)
            if is_energy_score_update_required(ddb):
                print("Average energy score update required for key " + key)
                average_energy_score = update_average_energy_score(newImage)
            if sleep_duration or idle_wakeup_duration or average_energy_score:
                update_ddb_item(key, sleep_duration, idle_wakeup_duration, average_energy_score)
            else:
                print("No update required for key " + key)
                
def process_scheduled_event(event):
    print("This is a scheduled event")
    items = scan_ddb();
    
    for item in items:
        key = item.get("DayId").get("S")
        sleep_duration = None
        idle_wakeup_duration = None
        average_energy_score = None
        if not item.get("SleepDurationInMinutes") and is_sleep_duration_update_required(item):
            print("Sleep duration update required for key " + key)
            sleep_duration = update_total_sleep_duration(item)
        if not item.get("IdleWakeupDurationInMinutes") and is_idle_wakeup_duration_update_required(item):
            print("Idle wakeup time update required for key " + key)
            idle_wakeup_duration = update_idle_wakeup_duration(item)
        if not item.get("AverageEnergyScore") and is_energy_score_update_required(item):
            print("Average energy score update required for key " + key)
            average_energy_score = update_average_energy_score(item)
        if sleep_duration or idle_wakeup_duration or average_energy_score:
            update_ddb_item(key, sleep_duration, idle_wakeup_duration, average_energy_score)
        else:
            print("No update required for key " + key)
                
        
def is_sleep_duration_update_required(ddb):
    if ddb.get("NewImage"):
        newImage = ddb.get("NewImage")
    else:
        newImage = ddb
    
    if not newImage.get("Bedtime") or not newImage.get("FinalWakeUpTime"):
        return False
        
    if ddb.get("OldImage"):
        oldImage = ddb.get("OldImage")
        if newImage.get("Bedtime") and (newImage.get("Bedtime") != oldImage.get("Bedtime")):
            return True
        if newImage.get("FinalWakeUpTime") and (newImage.get("FinalWakeUpTime") != oldImage.get("FinalWakeUpTime")):
            return True
        if newImage.get("HowLongToSleep") and (newImage.get("HowLongToSleep") != oldImage.get("HowLongToSleep")):
            return True
        if newImage.get("WakeUpDuration") and (newImage.get("WakeUpDuration") != oldImage.get("WakeUpDuration")):
            return True
        return False
        
    return True
    
def update_total_sleep_duration(newImage):
    entry_date = datetime.strptime(newImage.get("DayId").get("S"), "%Y-%m-%d")
    
    bedtime_time = datetime.strptime(newImage.get("Bedtime").get("S"), "%H:%M").time()
    sleep_start_time = datetime.combine(entry_date-timedelta(days=1), bedtime_time)
    
    wakeup_time = datetime.strptime(newImage.get("FinalWakeUpTime").get("S"), "%H:%M").time()
    sleep_end_time = datetime.combine(entry_date, wakeup_time)
    
    sleep_duration_in_seconds = (sleep_end_time - sleep_start_time).total_seconds()
    sleep_duration = int(sleep_duration_in_seconds // 60)
    
    if newImage.get("HowLongToSleep"):
        sleep_duration = sleep_duration - int(newImage.get("HowLongToSleep").get("S"))
        
    if newImage.get("WakeUpDuration"):
        sleep_duration = sleep_duration - int(newImage.get("WakeUpDuration").get("S"))
    
    return sleep_duration
    
def is_idle_wakeup_duration_update_required(ddb):
    if ddb.get("NewImage"):
        newImage = ddb.get("NewImage")
    else:
        newImage = ddb
    
    if not newImage.get("FinalWakeUpTime") or not newImage.get("AriseTime"):
        return False
        
    if ddb.get("OldImage"):
        oldImage = ddb.get("OldImage")
        if newImage.get("FinalWakeUpTime") and (newImage.get("FinalWakeUpTime").get("S") != oldImage.get("FinalWakeUpTime").get("S")):
            return True
        if newImage.get("AriseTime") and (newImage.get("AriseTime").get("S") != oldImage.get("AriseTime").get("S")):
            return True
        return False
        
    return True
    
def update_idle_wakeup_duration(newImage):
    wakeup_time = datetime.strptime(newImage.get("FinalWakeUpTime").get("S"), "%H:%M")
    arise_time = datetime.strptime(newImage.get("AriseTime").get("S"), "%H:%M")
    
    idle_wakeup_duration_in_seconds = (arise_time - wakeup_time).total_seconds()
    idle_wakeup_duration = int(idle_wakeup_duration_in_seconds // 60)
    
    return idle_wakeup_duration
    
def is_energy_score_update_required(ddb):
    if ddb.get("NewImage"):
        newImage = ddb.get("NewImage")
    else:
        newImage = ddb
    
    if not (newImage.get("MorningEnergy") or newImage.get("ForenoonEnergy") or newImage.get("AfternoonEnergy") or newImage.get("EveningEnergy")):
        print("No energy scores exist")
        return False
        
    if ddb.get("OldImage"):
        oldImage = ddb.get("OldImage")
        if newImage.get("MorningEnergy") and (newImage.get("MorningEnergy").get("S") != oldImage.get("MorningEnergy").get("S")):
            return True
        if newImage.get("ForenoonEnergy") and (newImage.get("ForenoonEnergy").get("S") != oldImage.get("ForenoonEnergy").get("S")):
            return True
        if newImage.get("AfternoonEnergy") and (newImage.get("AfternoonEnergy").get("S") != oldImage.get("AfternoonEnergy").get("S")):
            return True
        if newImage.get("EveningEnergy") and (newImage.get("EveningEnergy").get("S") != oldImage.get("EveningEnergy").get("S")):
            return True
        return False
    return True
    
def update_average_energy_score(newImage):
    energy_score_list = []
    
    if newImage.get("MorningEnergy"):
        energy_score_list.append(float(newImage.get("MorningEnergy").get("S")))
    if newImage.get("ForenoonEnergy"):
        energy_score_list.append(float(newImage.get("ForenoonEnergy").get("S")))
    if newImage.get("AfternoonEnergy"):
        energy_score_list.append(float(newImage.get("AfternoonEnergy").get("S")))
    if newImage.get("EveningEnergy"):
        energy_score_list.append(float(newImage.get("EveningEnergy").get("S")))

    average_energy_score = sum(energy_score_list)/len(energy_score_list)
    
    return average_energy_score
    
def update_ddb_item(entry_date, sleep_duration, idle_wakeup_duration, average_energy_score):
    ddb_item_key = dict()
    ddb_item_key['DayId'] = { 'S': entry_date }
    
    update_expression = 'SET ' 
    update_expression_list = []
    exp_attr_values = dict()
    
    if sleep_duration:
        update_expression_list.append('SleepDurationInMinutes = :sdm')
        exp_attr_values[':sdm'] = { 'N': str(sleep_duration) }
        
    if idle_wakeup_duration:
        update_expression_list.append('IdleWakeupDurationInMinutes = :iwm')
        exp_attr_values[':iwm'] = { 'N' : str(idle_wakeup_duration) }
        
    if average_energy_score:
        update_expression_list.append('AverageEnergyScore = :aes')
        exp_attr_values[':aes'] = { 'N': str(average_energy_score) }
        
    update_expression = update_expression + ','.join(update_expression_list)
    
    print("Updating with expression attributes " + json.dumps(exp_attr_values))
    
    ddb_client.update_item(
        TableName='SleepData',
        Key=ddb_item_key,
        UpdateExpression=update_expression,
        ExpressionAttributeValues=exp_attr_values
    )
    
def scan_ddb():
    ddb_response = ddb_client.scan(
            TableName='SleepData'
        )
    return ddb_response.get('Items')