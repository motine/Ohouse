import traceback
from exceptions import *


# --- deal with the GENI CH API returns
def form_error_return(logger, e):
    """Assembles a GENI compliant return result for faulty methods."""
    if not isinstance(e, GFedv1BaseError): # convert unknown errors into GFedv1ServerError
        e = GFedv1ServerError(str(e))
    # do some logging
    logger.error(e)
    logger.error(traceback.format_exc())
    return { 'code' : e.code, 'output' : str(e) }

    
def form_success_return(result):
    """Assembles a GENI compliant return result for successful methods."""
    return { 'code' : 0, 'value' : result, 'output' : None }


# --- helpers for filtering/selecting stuff
def match_and_filter_and_to_dict(list_of_dicts, key_field, field_filter, field_match):
    """Takes a list of dicts applies the {field_filter} and {field_match} (see match_and_filter).
    Then converts the list into a dict by using the {key_field} as key.
    E.g. match_and_filter_and_to_dict([{"x":1,"y":5}, {"x":2,"y":6}], "x", ...) results in {1:{"y":5}, 2:{"y":6}}
    """
    if field_filter and not key_field in field_filter:
        field_filter += [key_field]
    matched_and_filtered = match_and_filter(list_of_dicts, field_filter, field_match)
    
    for d in matched_and_filtered:
        if not key_field in d:
            raise ValueError("Can not convert to dict because the key_field name (%s) is not in the dictionary (%s)" % (key_field, d))
    return { d[key_field] : dict(filter(lambda (k,v): (k != key_field), d.iteritems())) for d in matched_and_filtered}
    

def match_and_filter(list_of_dicts, field_filter, field_match):
    """
    Takes a list of dicts and applies the given filter and matches the results (please GENI Federation API on how matching and filtering works).
    if field_filter is None the unfiltered list is returned.
    """
    return [filter_fields(d, field_filter) for d in list_of_dicts if does_match_fields(d, field_match)]

def filter_fields(d, field_filter):
    """Takes a dictionary and applies the filter. Returns the unfiltered d if None is given."""
    if not field_filter:
        return d
    result = {}
    for f in field_filter:
        result[f] = d[f]
    return result

def does_match_fields(d, field_match):
    """
    Returns if the given dictionary matches the {field_match}.
    {field_match} may look like: { 'must_be' : 'this', 'and_any_of_' : ['tho', 'se']} """
    if not field_match:
        return True
    for mk, mv in field_match.iteritems(): # each matches must be fulfilled
        val = d[mk]
        if isinstance(mv, list): # any of those values (OR)
            found_any = False;
            for mvv in mv:
                if val == mvv:
                    found_any = True
            if not found_any:
                return False
        else: # or explicitly this one
            if not val == mv:
                return False
    return True
    
