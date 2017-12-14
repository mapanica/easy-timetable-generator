#!/usr/bin/env python
# coding=utf-8

import os, sys, csv, json, re, datetime, getopt

DATA_FOLDER         = 'data/'
FREQUENCY_FILE      = '/frequencies.csv'
HEADER_FILE		    = '/header.json'
TIMETABLE_FILE      = '/timetable.json'

CSV_IDX_REF                    = 0
CSV_IDX_FROM                   = 1
CSV_IDX_TO                     = 2
CSV_IDX_VIA                    = 3
CSV_IDX_INTERMEDIATES          = 4
CSV_IDX_HOURS                  = 5
CSV_IDX_EXCEPTIONS             = 6
CSV_IDX_DURATION               = 7
CSV_IDX_INTERMEDIATE_DURATIONS = 8
CSV_IDX_FREQUENCY              = 9

# default values for 
MODE_PER_HOUR		= False

def main(argv):
    global MODE_PER_HOUR
    
    folder = ''

    try:
        (opts, args) = getopt.getopt(argv,"f:h",["folder=","per_hour"])
    except getopt.GetoptError:
        sys.stderr.write('convert.py -f | --folder <folder> [-h | --per_hour]\n')
        sys.exit(2)
    for (opt, arg) in opts:
        if opt in ('-f', '--folder'):
            folder = arg
            if not os.path.exists(DATA_FOLDER+folder):
                sys.stderr.write("Error: No folder found at '%s'.\n" % (DATA_FOLDER+folder))
                sys.exit(0)
        elif opt in ('-h','--per_hour'):
            MODE_PER_HOUR = True
    
    if folder == '':
        sys.stderr.write("Error: You have to specify a folder name.\n")
        sys.stderr.write('convert.py -f|--folder <folder> [-h|--per_hour]\n')
        sys.exit(2)
    
    # Load input csv file
    frequency_file = DATA_FOLDER+folder+FREQUENCY_FILE
    
    if os.path.exists(frequency_file):
        try:
            with open(frequency_file, newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                input_data = list(reader)

        except ValueError as e:
            sys.stderr.write("Error: I got a problem reading your csv at '%s'. Is it in a good format?\n" % frequency_file)
            print(e)
            sys.exit(0)
    else:
        sys.stderr.write("Error: No input csv file found at '%s'.\n" % frequency_file)
        sys.exit(0)

    # load header json file
    header_file = DATA_FOLDER+folder+HEADER_FILE
    header_data = None
    
    if os.path.exists(header_file):
        try:
            with open(header_file, newline='', encoding='utf-8') as f:
                header_data = json.load(f)

        except json.JSONDecodeError as e:
            sys.stderr.write("Error: I got a problem reading your header json at '%s'. Is it in a good format?\n" % header_file)
            print(e)
            sys.exit(0)
    else:
        sys.stderr.write("Warning: No header json file found at '%s'.\nYou HAVE TO add it later manually.\n" % header_file)
        # implement questioning

    output = generate_json(input_data, header_data)

    # Write output json file
    with open(DATA_FOLDER+folder+TIMETABLE_FILE, 'w', encoding='utf8') as outfile:
        json.dump(output, outfile, sort_keys=True, indent=4, ensure_ascii=False)

    # End program
    sys.exit()

def generate_json(input_data, header_data):
    
    output = {}
    header_line = True
    
    # add header information
    if header_data is not None:
        header_keys = ['start_date','end_date','excluded_lines','included_lines']
        for key in header_keys:
            if key in header_data:
                output[key] = header_data[key]
            else:
                sys.stderr.write("Warning: The header json file lacks the key '%s'.\nYou HAVE TO add it later manually.\n" % key)

	# add basic json structure
    output['updated'] = datetime.date.today().isoformat()
    output['lines'] = {}

    # Loop through bus lines
    for data in input_data:

		#Ignore header line
        if header_line is True:
            header_line = False
            continue

        ref = data[CSV_IDX_REF]
        if ref not in output["lines"]:
            output["lines"][ref] = []
        fr = data[CSV_IDX_FROM]
        to = data[CSV_IDX_TO]
        via = data[CSV_IDX_VIA]
        
        intermediates = data[CSV_IDX_INTERMEDIATES].split(";")
        if len(intermediates) == 1 and intermediates[0] == '':
            intermediates = []
        intermediate_durations = data[CSV_IDX_INTERMEDIATE_DURATIONS].split(";")
        if len(intermediate_durations) == 1 and intermediate_durations[0] == '':
            intermediate_durations = []
            
        if len(intermediates) != len(intermediate_durations):
            sys.stderr.write("Error: For ref=%s, from='%s', to='%s', via='%s', there weren't the same number of intermediate stops and intermediate times.\nSkipping this line, please check your frequencies.csv.\n" % (ref,fr,to,via))
            continue
        
        exceptions = data[CSV_IDX_EXCEPTIONS].split(";")
        if len(exceptions) == 1 and exceptions[0] == '':
            exceptions = []
        
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
            # output timetable information
            service = {
                "from": fr,
                "to": to,
                "services": [opening_service],
                "exeptions": exceptions,
                "times": []
            }
            
            if len(via) > 0:
                service["via"] = via

            if len(intermediates) > 0:
                stations = list()
                stations.append(fr)
                stations.extend(intermediates)
                stations.append(to)
                service["stations"] = stations
            else:
                service["stations"] = [fr, to]
            
            for opening_hour in opening_services[opening_service]:
                service["times"] += generate_times(opening_hour, int(data[CSV_IDX_DURATION]), intermediate_durations, float(data[CSV_IDX_FREQUENCY]))
            
            output["lines"][ref].append(service)
    
    return output


def generate_times(hour, duration, intermediate_durations, frequency):

    data_index = int()
    schedule = dict()
    times = list()

    regex = re.search(r"([0-9]+):([0-9]+)-([0-9]+):([0-9]+)" , hour)
    if regex is not None:
        (start_hour, start_min, end_hour, end_min) = regex.groups()
    else:
        regex = re.search(r"([0-9]+):([0-9]+)" , hour)
        if regex is None:
            sys.stderr.write("Error: Some format error in the opening_hours. Please check your frequencies.csv.\n")
            sys.exit(0)
        (start_hour, start_min) = regex.groups()
        (end_hour, end_min) = (start_hour, start_min)

    (start_hour, start_min, end_hour, end_min) = (int(start_hour), int(start_min), int(end_hour), int(end_min))

    # get number of minutes between public transport service
    if frequency == 0:
        sys.stderr.write("Error: You can not use the value '0' for frequency. Please check your frequencies.csv.\n")
        sys.exit(0)
    
    if MODE_PER_HOUR:
        minutes = 60 // frequency # exception (frequency = 0) already prevented
    else:
        minutes = frequency
        
    next_min = 0
    current_hour = start_hour
    
    while current_hour <= end_hour:
        
        # first service leaves at opening_hour {start_hour}:{start_min}
        if current_hour == start_hour:
            next_min = start_min
        
        until = 59
        # in the last hour, only services until {end_hour}:{end_min}
        if current_hour == end_hour:
            until = end_min

        # calculate times for the {current_hour} until (59 or {end_min})
        while next_min <= until:
            times.append(calculate_times(current_hour, int(next_min), duration, intermediate_durations))
            next_min = next_min + minutes
        
        # prepare next_min for next hour
        if current_hour == end_hour:
            current_hour += 1
        current_hour +=  (next_min // 60)
        next_min = next_min % 60
        
    
    return times

def calculate_times(hour, start_time, duration, intermediate_durations):

    calculated_time = list()

    # Append start time
    calculated_time.append(calculate_time(hour, start_time, 0))

    # Append intermediate times
    for intermediate_duration in intermediate_durations:
        calculated_time.append(calculate_time(hour, start_time, int(intermediate_duration)))

    # Append end time
    calculated_time.append(calculate_time(hour, start_time, duration))

    return calculated_time

def calculate_time(hour, start_time, duration):
    end_time = start_time + duration
    
    if end_time >= 60:
        hour = hour + (end_time // 60)
        end_time = end_time % 60

    return "%02d:%02d" % (hour,end_time)
    

if __name__ == "__main__":
    main(sys.argv[1:])
