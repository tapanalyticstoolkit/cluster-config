import sys

import cluster_config as cc


def nest(nested, keys, value):
    """
    turns a list of keys into a nested dictionary with the last key getting value assigned to it.
    given
    temp = {}
    split = [ "one", "two", "three" ]
    value = 3
    you will end up with
    temp["one"]["two"]["three"] = 3
    :param nested: some dictionary
    :param keys: the key list
    :param value: the value of the last split element
    """
    if keys and len(keys) > 0:
        if keys[0] not in nested:
            nested[keys[0]] = {}

        if len(keys) == 1:
            nested[keys[0]] = value
        elif len(keys) > 1:
            nest(nested[keys[0]], keys[1:], value)


def merge_dicts(first_dictionary, second_dictionary, conflict_resolution_preference="first"):
    """
    Takes to dictionaries and does a nested merge. Key conflicts are resolved either by defaulting to
    first or second dictionary or interactively.


    :param first_dictionary: The first dictionary to merge
    :param second_dictionary: the second dictionary to merge
    :param conflict_resolution_preference: The conflict resolution preference[ "first", "second", "interactive"]
        "first" defaults the value of any conflict to the first dictionary
        "second" defaults the value of any conflict to the second dictionary
        "interactive" no defaults you are asked at runtime
    :return: merged dictionary with resolved conflicts
    """
    if first_dictionary is None or second_dictionary is None:
        return None

    conflicts = find_dict_conflicts(first_dictionary, second_dictionary)

    resolved = resolve_conflicts(conflicts, first_dictionary, second_dictionary, conflict_resolution_preference)

    temp = _merge_dicts(first_dictionary, second_dictionary)

    set_resolved(resolved, temp)

    return temp


def _recurse_type_check(dictionary, key):
    """
    Checks of the dictionary key is a list or another dictionary
    :param dictionary: The dictionary that has the key
    :param key: the key we are checking
    :return: Boolean
    """

    return isinstance(dictionary[key], dict) if dictionary and key else False



def _merge_dicts(first_dictionary, second_dictionary):
    """
    merge two nested dictionaries. Non dictionary types will be ignored. Conflicting keys are ignored.
    We want a merged dictionary with all the same keys. Conflicting dictionary values will be dealt with later.

    given
    dict1 = { "frog" : 1 }
    dict2 = { "frog" : 2, "toad" : 2 }

    return
    temp = { "frog" : 2, "toad" : 2 }

    :param first_dictionary: first dictionary to merge
    :param second_dictionary: second dictionary to merge
    :return: merged dictionary
    """
    temp = {}
    if isinstance(first_dictionary, dict) and isinstance(second_dictionary,dict):

        temp = first_dictionary.copy()

        for key in second_dictionary:

            if _recurse_type_check(second_dictionary, key) and key in first_dictionary:

                temp[key] = _merge_dicts(first_dictionary[key], second_dictionary[key])
            elif key not in first_dictionary:

                temp[key] = second_dictionary[key]

    return temp


def find_dict_conflicts(first_dictionary, second_dictionary, config_key=[]):
    """
    find key conflicts between two dictionaries.
    A key is not considered conflicting if it's the same value in both dictionaries

     given
    dict1 = { "frog" : 1, "kermit" : 1}
    dict2 = { "frog" : 2, "kermit" : 2, "toad" : 2 }

    return
    temp = [ ["frog"], ["kermit"] ]

    :param first_dictionary:
    :param second_dictionary:
    :param config_key: list of of our current nested key [ [lvl0, lvl1, lvl3], ...]
    :return:
    """

    conflict_keys = []

    for key in first_dictionary:
        #if the value of the key type is dict and the key exists in auto_generated recurse
        if _recurse_type_check(first_dictionary, key) and key in second_dictionary:
            config_key.append(key)
            for add_key in find_dict_conflicts(first_dictionary[key], second_dictionary[key], config_key):
                conflict_keys.append(add_key)
            config_key.pop()
        elif key not in second_dictionary or second_dictionary.get(key) is None or second_dictionary.get(key) == first_dictionary.get(key):
            continue
        else:
            temp = [key]
            conflict_keys.append(config_key + temp)
    return conflict_keys


def user_input(msg):
    """
    prompts for user input. broken out to it's own function call to make it mockable
    :param msg: string message for the user prompt
    :return: user input
    """
    return raw_input(msg)


def resolve_conflict(conflict, user_configs, auto_configs, keep=None):
    """
    resolve conflicts either by asking or going forward with defaults form command line

    :param conflict: conflicting key
    :param user_configs: value for first conflicting key
    :param auto_configs: value for second conflicting key
    :param keep: answer for subsequent request
    :return: tuple(user input,resolved value for key)
    """
    print("\nKey merge conflict: {0}".format('.'.join(conflict)))
    user_value = get_value(conflict, user_configs)

    print("[{0}]User value: {1}".format(cc.USER.single, user_value))
    auto_value = get_value(conflict, auto_configs)
    print("[{0}]Auto generated value: {1}".format(cc.GENENERATED.single, auto_value))
    print("Optionally you can accept [{0}] all user values or [{1}] all auto generated values.".format(cc.USER.persistent, cc.GENENERATED.persistent))
    while keep is None:
        if cc.RETRY <= 0:
            print("Too many retries no valid entry.")
            sys.exit(1)

        keep = user_input("Would you like to keep the user value or the auto generated value?[[{0}|{1}][{2}|{3}]]: ".format(cc.USER.single, cc.USER.persistent, cc.GENENERATED.single, cc.GENENERATED.persistent)).strip()
        print "your answer: ", keep
        if keep != cc.USER.single and keep != cc.USER.persistent and keep != cc.GENENERATED.single and keep != cc.GENENERATED.persistent:
            print("Not a valid answer please try again.")
            keep = None
            cc.RETRY -= 1

    if keep == cc.USER.single or keep == cc.GENENERATED.single:
        return None, user_value if keep == cc.USER.single else auto_value
    else:
        cc.log.info("Auto resolving conflicts. Defaulting to {0} value".format("user" if keep == cc.USER.persistent else "auto generated"))
        return keep, user_value if keep == cc.USER.persistent else auto_value


def resolve_conflicts(conflicts, first_dictionary, second_dictionary, conflict_resolution_preference):
    """
    iterate through all the conflicts and save resolution

    given
    dict1 = { "frog" : 1, "kermit" : 1}
    dict2 = { "frog" : 2, "kermit" : 2, "toad" : 2 }

    return - assuming you default to second dictionaries value
    [(["frog"], 2), (["kermit"], 2)]

    :param conflicts: list of list with the inner list being the key path
        [[u'YARN', u'GATEWAY', u'GATEWAY_BASE', u'MAPREDUCE_MAP_JAVA_OPTS_MAX_HEAP'], ...]
    :param first_dictionary:
    :param second_dictionary:
    :param conflict_resolution_preference: 3 possible values first, second , interactive
    :return: list of tuples with conflicting key and the resolved value
    """
    resolved = []
    if conflict_resolution_preference == "first":
        keep = cc.USER.persistent
    elif conflict_resolution_preference == "second":
        keep = cc.GENENERATED.persistent
    else:
        keep = None

    if conflicts and first_dictionary and second_dictionary:
        for conflict in conflicts:
            keep, value = resolve_conflict(conflict, first_dictionary, second_dictionary, keep)
            resolved.append((conflict, value))

    return resolved


def set_value(value, config_keys, dictionary):
    """
    set the value for a given key in the dictionary
    :param value: value to set
    :param config_keys: list with the config key ["lvl1", "lvl2", ...]
    :param dictionary: the dictionary to update
    """
    if value and config_keys and dictionary:
        for key in config_keys:
            if key in dictionary and _recurse_type_check(dictionary, key):
                return set_value(value, config_keys[1:], dictionary[key])
            elif key in dictionary:
                dictionary[key] = value


def get_value(config_keys, dictionary):
    """
    get the value inside the dictionary for the config_key
    :param config_keys: config key path ["lvl1", "lvl2", "some_key"]
    :param dictionary:
    :return: the value of the key
    """
    for key in config_keys:
        if key in dictionary and _recurse_type_check(dictionary, key):
            return get_value(config_keys[1:], dictionary[key])
        elif dictionary[key]:
            return dictionary[key]


def set_resolved(resolved, dictionary):
    for key, value in resolved:
        set_value(value, key, dictionary)


