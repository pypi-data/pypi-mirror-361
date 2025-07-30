# Copyright 2023-2025 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of AccidentallyTheCables Utility Kit,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###
import datetime
import re
import logging
import typing

def create_object_logger(obj:object) -> logging.Logger:
    """Create logging.Logger with Specified object Class Name
    @param object \c obj Object to Create Logger for
    @retval logging.Logger Logger Instance
    """
    classname:str = str(obj.__class__.__qualname__)
    return logging.getLogger(classname)

def create_static_logger(classname:str) -> logging.Logger:
    """Create logging.Logger with Specified Name
    @param str \c classname Name of Logger to Create
    @retval logging.Logger Logger Instance
    """
    return logging.getLogger(classname)

def deltatime_str(time:str) -> datetime.timedelta:
    """Create datetime.timedelta from Time string
    @param str \c time Time String
    @throws ValueError Invalid Format
    @retval datetime.timedelta timedelta object

    Format: `0Y0M0w0d0h0m0s0ms`

    Not all entries are required, ex: `1d4h20m` is acceptable
    """
    time_match:typing.Union[re.Match,None] = re.search(r'^(\d+Y)?(\d+M)?(\d+w)?(\d+d)?(\d+h)?(\d+m)?(\d+s)?(\d+ms)?$',time)
    if time_match is None:
        raise ValueError("Invalid Format. Expects some part of: 0Y0M0w0d0h0m0s0ms")
    values:list[int] = [ 0, 0, 0, 0, 0, 0, 0, 0 ]
    i:int = 0
    for value in time_match.groups():
        if value is not None:
            v:int = int(re.sub(r'[YMwdhms]{1,2}$','',value))
            if re.match(r'.*Y$',value):
                values[0] += 365 * v
            elif re.match(r'.*M$',value):
                values[0] += 30 * v
            elif re.match(r'.*w$',value):
                values[0] += 7 * v
            elif re.match(r'.*d$',value):
                values[0] += v
            elif re.match(r'.*[hms]$',value):
                values[i] += v
        i += 1
    return datetime.timedelta(days=values[0],hours=values[4],minutes=values[5],seconds=values[6],milliseconds=values[7])

def deep_sort(input:dict[str,typing.Any]) -> dict[str,typing.Any]:
    """Deep Sort Dictionaries of varying data
    @param dict[str,typing.Any] \c input Input Dictionary
    @retval dict[str,typing.Any] New Sorted Dictionary
    """
    new_dict:dict[str,typing.Any] = {}
    for k,v in input.items():
        if isinstance(v,dict):
            new_dict[k] = dict(sorted(v.items()))
        elif isinstance(v,list):
            new_list:list[typing.Any] = []
            for i in v:
                if isinstance(i,dict):
                    new_list.append(deep_sort(i))
                else:
                    new_list.append(i)
            new_dict[k] = new_list
        else:
            new_dict[k] = v
    return new_dict

#### CHECKSUM c7b3b4593fc6dd35d8d14ffd102bde3f4fdacd18732ab64a810495ab3b371f26
