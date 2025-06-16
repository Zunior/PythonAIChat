import nltk

def split_text_no_sentence_break(text, chunk_size):
    # return [text[i:i+chunk_size]
    #         for i in range(0, len(text), chunk_size)]
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