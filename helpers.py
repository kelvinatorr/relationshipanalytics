import re
import datetime

# helper functions
valid_dict = {'username':r"^[\S]+@gmail\.[\S]+$" 
              ,'password':r"^.{6,20}$"          
              }

def valid_username(string_type,target_string):
    regex = re.compile(valid_dict[string_type])
    return regex.match(target_string)

def convert_string_to_date(dateString):
    """
    Converts string date time to Python date object by trying multiple
    formats. Returns None if conversion failed
    """
    test_cases = ['%m/%d/%Y','%m/%d/%y', '%Y-%m-%d']
    res = None
    for f in test_cases:
        try:
            res = datetime.datetime.strptime(dateString, f).date()
            return res
        except:
            pass
    return res

def int_or_null(data):
    if data != '':
        return int(data)
    else:
        return None