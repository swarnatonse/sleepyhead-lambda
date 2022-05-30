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
    
sleep_report_headers = [
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
    
sleep_report_fields = {
    'DayId': 'Date',
    'Bedtime': 'What time did you go to bed?',
    'LightsOutTime': 'What time did you turn the lights out to go to sleep?',
    'HowLongToSleep': 'About how long did it take to fall asleep?',
    'WakeUpCount': 'How many times did you wake up last night?',
    'WakeUpDuration': 'About how long were you awake during the night?',
    'FinalWakeUpTime': 'What was your final wake up time this morning?',
    'AriseTime': 'What time did you get out of bed?',
    'SleepNotes': 'Notes',  
}