from math import sin, cos, sqrt, atan2, radians
import uuid
import os
from django.contrib import messages
from django.contrib.messages import constants

def show_message(request, message, type="success"):
    print("type", type)
    if type=='error':
        messages.add_message(request, constants.ERROR, "Error : "+message)
    else:
        messages.add_message(request, constants.SUCCESS, message)

def nvl(v1, v2, v3=None, v4=None, v5=None):
    if v1 == None:
        return v2
    elif v2 == None:
        return v3
    elif v3 == None:
        return v4
    elif v4 == None:
        return v5
    elif v5 == None:
        None

class LocationUtils:
    @staticmethod
    def get_distance(lat1, lon1, lat2, lon2):
        R = 6373.0
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c
        print("Result:", distance)
        print("Should be:", 278.546, "km")
        return distance

class FileUtils:
    @staticmethod
    def get_app_filename(instance, filename):
        print("instance.directory_string_var"+filename)
        ext = filename.split('.')[-1]
        filename = "%s.%s" % (uuid.uuid4(), ext)
        return os.path.join("uploads", filename)
