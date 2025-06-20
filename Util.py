import ntpath

# nltk.download('punkt')

class Util:
    @staticmethod
    def path_leaf(path):
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)

    @staticmethod
    def create_data_file(full_path, content):
        try:
            with open(full_path, "w", encoding='utf-8') as file:
                file.write(content)
                return "File: " + Util.path_leaf(full_path) + " created successfully."
        except Exception as e:
            return f"An error occurred: {e}"

