import ntpath

# nltk.download('punkt')

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def create_data_file(full_path, content):
    with open(full_path, "w") as file:
        file.write(content)
        return "File: " + path_leaf(full_path) + " created successfully."

