import csv
import datetime


def parser(csvrow, parser_type):
    if parser_type == 1:    # there is no row name
        return tuple(csvrow)
    else:   # parser_type == 2  # there is row name
        return tuple(csvrow[1:])


def data2array(filename, parser_type):   # for basic_data, star_data, sony_data, sony_more_data
    data_array = []
    with open(filename) as csvfile:
        next(csvfile)   # skip header line
        csvreader = csv.reader(csvfile, quoting=csv.QUOTE_NONNUMERIC)   # change contents to floats
        for csvrow in csvreader:   # each row is a list
            tuplerow = parser(csvrow, parser_type)
            data_array.append(tuplerow)
    return data_array


def transform_datetime2minutes(date_time_str, date_time_reference=datetime.datetime(1, 1, 1, 0, 0)):

    if date_time_reference == datetime.datetime(1, 1, 1, 0, 0):    # first date and time in the file

        date_time_obj = datetime.datetime.strptime(date_time_str, '%m-%d-%Y %H:%M')
        date_time_reference = date_time_obj
        time_difference = date_time_obj - date_time_reference
        minutes = time_difference.days*1440 + time_difference.seconds/60

        return minutes, date_time_reference

    else:

        date_time_obj = datetime.datetime.strptime(date_time_str, '%m-%d-%Y %H:%M')
        time_difference = date_time_obj - date_time_reference
        minutes = time_difference.days*1440 + time_difference.seconds/60

        return minutes


def transform_blood_glucose_code(code_str):

    # regular_insulin_code = 33
    # nph_insulin_code = 34
    # ultralente_insuline_code = 35

    blood_glucose_code_list = ['48', '57', '58', '59', '60', '61', '62', '63', '64']
    if code_str in blood_glucose_code_list:
        code_str = '01'

    return code_str


def diabetesdata_format_transformation(filename, newfilename):
    # This function transforms every code regarding blood glucose into a single code
    # and delete several entries in order to have 4 variables: blood glucose,
    # regular insuline dose, NPH insuline dose and ultralente insuline dose.

    file = open(filename, 'r')
    newfile = open(newfilename, 'w')
    newfile.write('Time(minutes),Code,Value\n')

    firstline_bool = True

    for line in file.readlines():

        linelist = line.strip().split("\t")
        date_time = linelist[0] + ' ' + linelist[1]
        code = linelist[2]
        value = linelist[3]

        if firstline_bool:

            minutes, datetime_reference = transform_datetime2minutes(date_time_str=date_time)
            firstline_bool = False

        else:

            minutes = transform_datetime2minutes(date_time_str=date_time,
                                                 date_time_reference=datetime_reference)

        newcode = transform_blood_glucose_code(code)

        accepted_code_list = ['01', '33', '34', '35']
        if newcode in accepted_code_list:
            newline_list = [str(minutes), newcode, value]
            newline = ','.join(newline_list) + '\n'
            newfile.write(newline)

    file.close()
    newfile.close()


def time_block2single_time(time_block):

    time = time_block[0][0]
    single_time = [time, 'nan', 'nan', 'nan', 'nan']
    for time_list in time_block:
        code = time_list[1]
        value = time_list[2]
        if code == '01':
            single_time[1] = value
        elif code == '33':
            single_time[2] = value
        elif code == '34':
            single_time[3] = value
        elif code == '35':
            single_time[4] = value
        else:
            raise ValueError("Unexpected code:", code)

    return single_time


def diabetesdata_time_block(filename, newfilename):
    # This function transforms every code regarding blood glucose into a single code
    # and delete several entries in order to have 4 variables: blood glucose,
    # regular insuline dose, NPH insuline dose and ultralente insuline dose.

    file = open(filename, 'r')
    file.readline()    # read the first line which contains column names
    newfile = open(newfilename, 'w')
    newfile.write('Time(minutes),code 01,code 33,code 34,code 35\n')

    time_block = []
    firstline_bool = True
    for line in file.readlines():

        linelist = line.strip().split(",")

        time = linelist[0]

        if firstline_bool:

            time_block.append(linelist)
            previous_time = time
            firstline_bool = False

        else:

            if time != previous_time:

                newline_list = time_block2single_time(time_block)
                newline = ','.join(newline_list) + '\n'
                newfile.write(newline)

                time_block = []

            time_block.append(linelist)
            previous_time = time

    newline_list = time_block2single_time(time_block)
    newline = ','.join(newline_list) + '\n'
    newfile.write(newline)

    file.close()
    newfile.close()