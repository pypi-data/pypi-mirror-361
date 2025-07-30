from logging import exception


def KmToMeters(arg1):
    if type(arg1) != int and type(arg1) != float:
        raise Exception("Conversion Error: Tried To Use String As Base For Conversion")
    if arg1 == 0:
        raise Exception("Conversion Error: Tried To Divide By 0")
    return arg1 * 1000

def MetersToKm(arg1):
    if type(arg1) != int and type(arg1) != float:
        raise Exception("Conversion Error: Tried To Use String As Base For Conversion")
    if arg1 == 0:
        raise Exception("Conversion Error: Tried To Divide By 0")
    return arg1 / 1000

def MetersToCm(arg1):
    if type(arg1) != int and type(arg1) != float:
        raise Exception("Conversion Error: Tried To Use String As Base For Conversion")
    return arg1 * 100

def MilesToKilometers(arg1):
    if type(arg1) != int and type(arg1) != float:
        raise Exception("Conversion Error: Tried To Use String As Base For Conversion")
    return arg1 * 1,60934

def KilometersToMiles(arg1):
    if type(arg1) != int and type(arg1) != float:
        raise Exception("Conversion Error: Tried To Use String As Base For Conversion")
    if arg1 == 0:
        raise Exception("Conversion Error: Tried To Divide By 0 ")
    return arg1 / 1,60934

def MillimetersToKilometers(arg1):
    if type(arg1) != int and type(arg1) != float:
        raise Exception("Conversion Error: Tried To Use String As Base For Conversion")
    if arg1 == 0:
        raise Exception("Conversion Error: Tried To Divide By 0")
    return arg1 / 1000000

def CentimetersToMillimeters(arg1):
    if type(arg1) != int and type(arg1) != float:
        raise Exception("Conversion Error: Tried To Use String As Base For Conversion")
    if arg1 == 0:
        raise Exception("Conversion Error: Tried To Divide By 0")
    return arg1 * 10

def MillimetersToCentimeters(arg1):
    if type(arg1) != int and type(arg1) != float:
        raise Exception("Conversion Error: Tried To Use String As Base For Conversion")
    if arg1 == 0:
        raise Exception("Conversion Error: Tried To Divide By 0")
    return arg1 * 10

def MilesToCentimeters(arg1):
    if type(arg1) != int and type(arg1) != float:
        raise Exception("Conversion Error: Tried To Use String As Base For Conversion")
    if arg1 == 0:
        raise Exception("Conversion Error: Tried To Divide By 0")
    return arg1 * 160934,4

def MilesToMillimeters(arg1):
    if type(arg1) != int and type(arg1) != float:
        raise Exception("Conversion Error: Tried To Use String As Base For Conversion")
    if arg1 == 0:
        raise Exception("Conversion Error: Tried To Divide By 0")
    return arg1 * 1609344

def MillimetersToMiles(arg1):
    if type(arg1) != int and type(arg1) != float:
        raise Exception("Conversion Error: Tried To Use String As Base For Conversion")
    if arg1 == 0:
        raise Exception("Conversion Error: Tried To Divide By 0")
    return arg1 / 1609344

def CentimetersToMiles(arg1):
    if type(arg1) != int and type(arg1) != float:
        raise Exception("Conversion Error: Tried To Use String As Base For Conversion")
    if arg1 == 0:
        raise Exception("Conversion Error: Tried To Divide By 0")
    return arg1 / 160934,4

