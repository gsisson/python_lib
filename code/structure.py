def query(structure, search_path_str, default=None):
    """
    This method provides a way (similar to a very simple 'jq' expression), to
    safely dig into a complex JSON structure (nested python structure of dicts
    and lists) and return an embeded item. This avoids complicated checks to
    validate each layer of the structure. The method simply returns "None" (or
    a user specified value) if the search path into the structure is not found.
    The search path 'search_path_str' is similar to a very simple expression be
    passed to 'jq' and specifies where in the structure is the item to be
    returned.

    Here is an example (see the unit tests for more examples):

        struct = {"first_key" : {'nested_key' : '42'}, "second_key" : [ 10, 20, 30 ] }
        assert query( struct, ".first_key.nested_key" ) == '42'
        assert query( struct, ".second_key[2]" )        ==  30
    """
    # First, let's do some type and value checking
    if not isinstance(search_path_str, str):
        raise TypeError("'search_path_str' argument is not of type 'str'")
    if len(search_path_str) == 0:
        raise ValueError(f"'search_path_str' argument cannot be a zero length string")
    first_search_char = search_path_str[0]
    if first_search_char not in ('.','['):
        raise ValueError(f"'search_path_str' argument not in correct format. Expected to find '.' or '[' but found invalid '{first_search_char}' instead")
    # At this point we know the search_path_str starts correctly (with '.' or '[')
    # So now we need to find the end of the token that follows that '.' or '['
    search_path_remainder = search_path_str[1:]
    next_dot_index = search_path_remainder.find('.')
    next_open_bracket_index = search_path_remainder.find('[')
    next_close_bracket_index = search_path_remainder.find(']')
    if first_search_char == '[':
        # At this point we know that the search path starts with an open-bracket
        # First lets make sure we see a closing-bracket before seeing a '.' or '[' because it is an error if we don't see that
        if next_close_bracket_index == -1:
            raise ValueError(f"'search_path_str' argument not in correct format. No closing bracket found in '{search_path_remainder}'")
        if next_dot_index > -1 and next_close_bracket_index > next_dot_index:
            raise ValueError(f"'search_path_str' argument not in correct format. found '.' before closing bracket ']' in '{search_path_remainder}'")
        if next_open_bracket_index > -1 and next_close_bracket_index > next_open_bracket_index:
            raise ValueError(f"'search_path_str' argument not in correct format. found '[' before closing bracket ']' in '{search_path_remainder}'")
        # the end of the token is right before the closing bracket
        end_of_this_token_index = next_close_bracket_index
        # the remaining search path is after our token
        next_search_path_str = search_path_str[end_of_this_token_index+2:] # +2 since we need to increment the index, plus skip over the closing bracket
    else:
        # At this point we know that the search path starts with a dot
        # So now we need to figure out where our token ends
        if max(next_dot_index, next_open_bracket_index) == -1:
            # not seeing any additional '.' or '[' so our token is the entire rest of the search path string
            end_of_this_token_index = len(search_path_remainder)
        else:
            # the end of the token is right after the next dot or open-bracket
            if next_dot_index == -1:
                end_of_this_token_index = next_open_bracket_index
            elif next_open_bracket_index == -1:
                end_of_this_token_index = next_dot_index
            else:
                end_of_this_token_index = min(next_dot_index, next_open_bracket_index)
        # the remaining search path is after our token
        next_search_path_str = search_path_str[end_of_this_token_index+1:] # +1 since we need to increment the index
    # now we have the full token, which is either our 'key' into a dict, or our 'index' into a list
    dict_key_or_list_index = search_path_remainder[0:end_of_this_token_index]
    if first_search_char == '[':
        # the search path starting with an open-bracket, so we are expecting to see a list type
        if not isinstance(structure, list):
            return default # since we didn't find a list
        if not str.isdigit(dict_key_or_list_index):
            raise ValueError(f"'search_path_str' argument not in correct format. Expected '{dict_key_or_list_index}' to hold a positive integer")
        this_index = int(dict_key_or_list_index)
        if this_index >= len(structure):
            # not finding the structure the search string is specifying (list index is out of bounds) so return the default
            return default
        ret_val = structure[this_index]
    else:
        # the search path starting with a dot, so we are expecting to see a dict type
        if not isinstance(structure, dict):
            return default # since we didn't find a dict
        ret_val = structure.get(dict_key_or_list_index, default)
        # if we can't find dict_key_or_list_index in the dict as a string, try it as an int
        if ret_val == None and str.isdigit(dict_key_or_list_index):
            dict_key_or_list_index = int(dict_key_or_list_index)
            ret_val = structure.get(dict_key_or_list_index, default)
    if len(next_search_path_str) == 0:
        # There is no more search_path_str to search, so we are done. Just return what we have found
        return ret_val
    # There is more search_path_str to search, so we recurse to keep searching
    return query(ret_val, next_search_path_str, default)
