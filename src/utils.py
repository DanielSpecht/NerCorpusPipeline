from Token import Token
import nltk

def get_word_tokens(text, tag = 'word'):
    return create_tokens_from_slices(text = text,
                                            tag = tag,
                                            ordered_slices = nltk.word_tokenize(text, language = "portuguese"))

def get_sentence_tokens(text, tag = 'sentence'):
    return create_tokens_from_slices(text = text,
                                            tag = tag,
                                            ordered_slices = nltk.sent_tokenize(text, language = "portuguese"))

def sort_tokens(tokens):
    tokens.sort(key = lambda x: x._init_index)
    return tokens

def create_tokens_from_slices(text, ordered_slices, tag, offset_step = 0):
    tokens = []
    offset = 0
    for part in ordered_slices:
        offset = text.find(part, offset)
        tokens.append(Token(text = part, init_index = offset + offset_step, end_index = offset + len(part) - 1 + offset_step, tag = tag))
        offset += len(part)

    return sort_tokens(tokens)