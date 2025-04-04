def find_network_module(data, keyword, path=None, output_dict=None):
    if path is None:
        path = []
    if output_dict is None:
        output_dict = {}
    try:
        for k, v in data.items():
            current_path = path + [k]
            if isinstance(v, dict):
                find_network_module(v, keyword, current_path, output_dict)
            elif k == "name" and isinstance(v, str):  # Check if key is 'name'
                if keyword.lower() in v.lower():
                    parent_dict = data
                    if "name" in parent_dict and "pid" in parent_dict:
                        # path_str = "_".join(path) if path else k # create path string
                        current_output = output_dict
                        for key in path[
                            :-1
                        ]:  # Exclude the last key (which is 'name') from path traversal
                            if key not in current_output:
                                current_output[key] = {}
                            current_output = current_output[key]

                        if (
                            path and path[-2] == "rp"
                        ):  # Check if the key before 'name' is 'rp'
                            current_output[parent_dict["pid"]] = (
                                {  # Directly assign to 'rp' key
                                    "name": parent_dict["name"],
                                    "descr": parent_dict["descr"],
                                    "pid": parent_dict["pid"],
                                    "sn": parent_dict["sn"],
                                }
                            )
                        else:
                            current_output[path[-2]] = (
                                {  # Use the key before 'name' as key in output
                                    parent_dict[
                                        "pid"
                                    ]: {  # Keep pid level if not under 'rp' - although this might not be needed based on 'remove 2 levels after rp' which is likely simplification to remove 1 level
                                        "name": parent_dict["name"],
                                        "descr": parent_dict["descr"],
                                        "pid": parent_dict["pid"],
                                        "sn": parent_dict["sn"],
                                    }
                                }
                            )
    except:
        pass
    
    finally:
        if len(output_dict) == 0:
            return None
        return output_dict
