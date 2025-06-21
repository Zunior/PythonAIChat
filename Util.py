import ntpath

import nltk


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

    @staticmethod
    def split_text_no_sentence_break(text, chunk_size):
        sentences = nltk.sent_tokenize(text)
        result = []
        current = ""
        for sentence in sentences:
            if len(current) + len(sentence) < chunk_size:
                current += sentence + " "
            else:
                result.append(current.strip())
                current = sentence + " "
        if current:
            result.append(current.strip())
        return result
