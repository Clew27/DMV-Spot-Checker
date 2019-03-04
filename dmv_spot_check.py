# CA DMV Locations Check
import json
import urllib.request, urllib.parse
import http.cookiejar
import time
import random
from datetime import datetime

REQUEST_URL = 'https://www.dmv.ca.gov/wasapp/foa/findDriveTest.do'
USER_AGENT  = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:60.0) Gecko/20100101 Firefox/60.0'}
BB_DATE     = datetime(2018, 8, 15)
HOUR        = 60 * 60  # In seconds

def main():
    # Load DMV ids
    with open('dmv_ids.txt', 'r') as file:
        dmv_ids = json.loads(file.read())

    # Form submissions
    form_items = {
        'numberItems'      : '1',
        'mode'             : 'DriveTest',
        'officeId'         : '0',            # Dummy value
        'requestedTask'    : 'DT',
        'firstName'        : 'Christopher',
        'lastName'         : 'Liu',
        'dlNumber'         : 'Y5355637',
        'birthMonth'       : '09',
        'birthDay'         : '27',
        'birthYear'        : '1999',
        'telArea'          : '408',
        'telPrefix'        : '475',
        'telSuffix'        : '3898',
        'resetCheckFields' : 'true'
    }

    with open('locations.txt', 'r') as file:
        check_locations = file.read().split('\n')
    check_locations = sorted(check_locations, key = str.lower)

    while True:
        print_time()
        check_dmv(dmv_ids, form_items, check_locations)
        time.sleep(int(((10 + random.randint(-2, 2)) / 60.0) * HOUR))

def check_dmv(dmv_ids, form_items, check_locations):
    cookie_jar = http.cookiejar.CookieJar()
    opener     = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))

    req = urllib.request.Request(
        url     = REQUEST_URL,
        headers = USER_AGENT
    )
    opener.open(req)  # Get cookies

    dmv_information = dict()
    error_locations = []
    for location in check_locations:
        location = location.upper() # All upper case to match the keys in dictionary
        try:
            officeId = dmv_ids[location]
        except:
            print("Location", location, "does not exist")
            continue
        form_items['officeId'] = officeId

        req = urllib.request.Request(
            url     = REQUEST_URL,
            headers = USER_AGENT,
            data    = urllib.parse.urlencode(form_items).encode()
        )
        req.add_header('Referer', 'https://www.dmv.ca.gov/wasapp/foa/clear.do?goTo=driveTest')

        with opener.open(req) as resp:
            raw = resp.read().decode()

        try:
            _    = get_center(raw, 'The first available appointment for this office is on:',
                          '</td>')
            time = get_center(_, '<strong>', '</strong>')

            # Get date
            space_idx = time.find(' ')
            at_idx    = time.find(' at')
            date      = time[space_idx + 1:at_idx]
            date      = datetime.strptime(date, '%B %d, %Y')

            dmv_information[location] = [time, date]

        except:
            error_locations.append(location)

    print_info = []
    for k, (raw, dt) in dmv_information.items():
        details = [k, raw]
        if dt < BB_DATE:
            details.append('[x]')
        else:
            details.append('[ ]')
        print_info.append(details)

    #col_width = max(len(word) for detail in print_info for word in detail) + 2
    col_width = 42
    for detail in print_info:
        print("".join(word.ljust(col_width) for word in detail))

    if len(error_locations) != 0:
        print("Couldn't find info for", ", ".join(error_locations))

def print_time():
    now = time.localtime()
    print("{}/{}".format(now.tm_mon, now.tm_mday), "   ", "{}:{}".format(now.tm_hour, now.tm_min))

def get_center(string, split1, split2):
    s1 = string.split(split1)[1]
    return s1.split(split2)[0]

if __name__ == '__main__':
    main()
