#!/usr/bin/env python
# coding=utf-8

import os, sys, csv, json, re

DATA_FOLDER         = 'data/'
INPUT_FILE          = '/input.csv'
OUTPUT_FILE         = '/output.json'

#better format: ref,terminal-1,terminal-2,opening-hours,duration,frequency (one line for each direction!)

CSV_IDX_REF         = 0
CSV_IDX_TERMINALS   = 1
CSV_IDX_HOURS       = 3
CSV_IDX_DURATION    = 4
CSV_IDX_FREQUENCY   = 5


CSV_NETWORK         = 'mock' # TODO: add command parameter
MODE_PER_HOUR		= False

def main():

    inputfile = DATA_FOLDER+CSV_NETWORK+INPUT_FILE

    # Load input csv file
    if os.path.exists(inputfile):
        try:
            with open(inputfile, newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                input_data = list(reader)

        except ValueError as e:
            sys.stderr.write('Error: I got a problem reading your csv. Is it in a good format?\n')
            print(e)
            sys.exit(0)
    else:
        sys.stderr.write("Error: No input csv file found at '%s'.\n" % DATA_FOLDER+CSV_NETWORK+INPUT_FILE)
        sys.exit(0)

    # add header information (network etc.)

    output = {"lines": dict()}
    header_line = True
    headers = {}
    days = ['Mo','Tu','We','Th','Fr','Sa','Su']

    # Loop through bus lines
    for data in input_data:

		#Ignore header line
        if header_line is True:
            header_line = False
            continue

        ref = data[CSV_IDX_REF]
        if ref not in output["lines"]:
            output["lines"][ref] = []
        fr = data[CSV_IDX_TERMINALS]
        to = data[CSV_IDX_TERMINALS+1]
        
        # Prepare schedule
        opening_hours = data[CSV_IDX_HOURS].split(";")
        opening_services = {}

        for i, d in enumerate(opening_hours):

            # Convert into understandable service schedules
            (opening_service, opening_hour) = opening_hours[i].strip().split(' ')

            if opening_service in opening_services:
                opening_services[opening_service].append(opening_hour)
            else:
                opening_services[opening_service] = [opening_hour]
            
            
        for opening_service in opening_services.keys():
            
            #search for already existing service
            existing = -1
            for i, service in enumerate(output["lines"][ref]):
                if (service["from"] == fr
					and service["to"] == to
					and service["services"][0] == opening_service): #TODO: loop through services? AND add from/to check!!
                    existing = i
                    break
            
            # output for services
            for opening_hour in opening_services[opening_service]:
                # output timetable information            
                if existing != -1:
                    print("yeah")
                    output["lines"][ref][existing]["times"] = output["lines"][ref][existing]["times"] + generate_times(data, opening_hour)
                else:
                    output["lines"][ref].append({
                        "from": fr,
                        "to": to,
                        "services": [opening_service],
                        "stations": [data[CSV_IDX_TERMINALS], data[CSV_IDX_TERMINALS+1]],
                        "times": generate_times(data, opening_hour)
                    })
                    existing = len(output["lines"][ref])-1


    # Write output json file
    with open(DATA_FOLDER+CSV_NETWORK+OUTPUT_FILE, 'w', encoding='utf8') as outfile:
        json.dump(output, outfile, sort_keys=True, indent=4, ensure_ascii=False)

    # End program
    sys.exit()


def generate_times(data, hour):

    data_index = int()
    schedule = dict()
    times = list()
    duration = int(data[4])

    (start_hour, start_min, end_hour, end_min) = re.search(r"([0-9]+):([0-9]+)-([0-9]+):([0-9]+)" , hour).groups()
    (start_hour, start_min, end_hour, end_min) = (int(start_hour), int(start_min), int(end_hour), int(end_min))

    next_min = 0
    for current_hour in range(start_hour,end_hour+1,1):

        # get standard frequency for current hour
        frequency = float(data[CSV_IDX_FREQUENCY])
        
        if frequency is not 0:
            if MODE_PER_HOUR:
                minutes = 60 // frequency
            else:
                minutes = frequency
            
            # first service leaves at opening_hour {start_hour}:{start_min}
            if current_hour == start_hour:
                next_min = start_min
            
            until = 59
            # in the last hour, only services until {end_hour}:{end_min}
            if current_hour == end_hour:
                until = end_min

            # calculate times for the {current_hour} until (59 or {end_min})
            while next_min <= until:
                times.append(calculate_times(current_hour, int(next_min), duration))
                next_min = next_min + minutes
            
            # prepare next_min for next hour
            next_min = next_min % 60
    
    return times

def calculate_times(hour, start_time, duration):

    calculated_time = list()

    calculated_time.append("%02d:%02d" % (hour,start_time))

    # Calculate end_time
    end_time = start_time + duration
    
    if end_time >= 60:
        hour = hour + (end_time // 60)
        end_time = end_time % 60

    calculated_time.append("%02d:%02d" % (hour,end_time))

    return calculated_time

if __name__ == "__main__":
    main()
