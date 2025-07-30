def string_or_default(primary_value, secondary_value):
    retVal = primary_value
    if retVal is None or retVal.strip() == '':
        retVal = secondary_value
    return retVal
    # return secondary_value if (primary_value is None or primary_value.strip()) == '' else primary_value
