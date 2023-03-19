def read_file_list_from_file(file_list_path: str):
    with open(file_list_path, "r") as file_h:
        # TODO: check file
        return file_h.read().strip().split("\n")
