from locawise.lockfile import hash_key_value_pair


def retrieve_nom_source_keys(key_value_hashes: set[str], source_dict: dict[str, str]) -> set[str]:
    """nom stands for new or modified"""
    nom_keys = set()
    for k, v in source_dict.items():
        _hash = hash_key_value_pair(k, v)
        if _hash not in key_value_hashes:
            nom_keys.add(k)

    return nom_keys


def retrieve_keys_to_be_localized(source_dict: dict[str, str],
                                  target_dict: dict[str, str],
                                  nom_keys: set[str]) -> set[str]:
    missing_target_keys = source_dict.keys() - target_dict.keys()
    return missing_target_keys | nom_keys
