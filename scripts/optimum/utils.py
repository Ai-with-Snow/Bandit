import datetime

def genDatetimeObjFromTimestring(timestring):
    obj = genDatetimeObj(timestring[2], timestring[4], timestring[3], timestring[5], timestring[6], 0)
    return obj

def genDatetimeObj(year, month, day, hour, minute, second):
    return datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))

def genDatetimeObjFromScheduled(timestring):
    parts = timestring.split(" ")
    date = parts[0].split("-")
    time = parts[1]
    return genDatetimeObj("20" + date[2], date[0], date[1], time[:2], time[2:], 0)

def genDatetimeObjFromReleaseDate(release_date):
    parts = release_date.split(" ")
    date = parts[0].split("-")
    time = parts[1].split(":")
    return genDatetimeObj(date[0], date[1], date[2], time[0], time[1], time[2])

def adjustTimeFromGMT(datetime_obj):
    return datetime_obj - datetime.timedelta(hours=4)

def addSeconds(datetime_obj, seconds):
    return datetime_obj + datetime.timedelta(seconds=seconds)

def genRecordRequestTime(datetime_obj):
    return datetime_obj.strftime("%Y%m%d%H%M00")

def genTimestamp():
    return datetime.datetime.now().strftime("%A, %B %-d, %y %-I:%M:00 %p -04:00")

def genEventTimestamp():
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f0-04:00")

def parseSearchTime(string):
    parts = string.split(":")
    obj = datetime.datetime(int(parts[2]), int(parts[4]), int(parts[3]), int(parts[5]), int(parts[6]), 0)
    return (obj, int(parts[7]))
