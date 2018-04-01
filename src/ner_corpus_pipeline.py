import nltk
from Token import Token
from utils import get_word_tokens, get_sentence_tokens, sort_tokens, create_tokens_from_slices

class NerCorpusPipeline(object):
    
    def __init__(self, text, known_tokens):
        self._text = text
        # TODO: Guarantee that all known tokens do not intersect
        self.known_tokens = known_tokens
        self.sentences_tokens = get_sentence_tokens(text)
        self.word_tokens = get_word_tokens(text, 'O')

    def apply_processing_rules(self):
        self._ensure_sentence_enclosing()
        self._split_known_tokens()
        self._fit_known_tokens()

    def _ensure_sentence_enclosing(self):
        for token in self.known_tokens:
            sentence_start = [sentence for sentence in self.sentences_tokens if sentence.enclosing(token._init_index)]
            sentence_end = [sentence for sentence in self.sentences_tokens if sentence.enclosing(token._end_index)]

            # TODO: Create exceptions for asserts
            assert(len(sentence_start) == 1)
            assert(len(sentence_end) == 1)

            sentence_start = sentence_start[0]
            sentence_end = sentence_end[0]

            # Ends in the same sentence it started?
            if sentence_start is sentence_end:
                continue

            # Merge sentences
            merged_sentence = Token(self._text[sentence_start._init_index : sentence_end._end_index + 1],sentence_start._init_index, sentence_end._end_index, tag = 'sentence')

            inside_flag = False
            sentences = []
            for sentence in self.sentences_tokens:
                # Jump sentences in between start - end
                if sentence is sentence_start:
                    inside_flag = True
                elif sentence is sentence_end:
                    inside_flag = False
                elif not inside_flag:
                    sentences.append(sentence)

            sentences.append(merged_sentence)
            self.sentences_tokens = sort_tokens(sentences)

    def _split_known_tokens(self):
        
        # TODO: Remove the IOB functionalities, make optional
        known_tokens = []
        for k_token in self.known_tokens:
            sliced_text = k_token._text.split()
            
            if len(sliced_text) == 1:
                k_token.tag = "B-" + k_token.tag
                known_tokens.append(k_token)
                continue

            # Split token
            splitted_token = create_tokens_from_slices(text = k_token._text,
                                                       tag = k_token.tag,
                                                       ordered_slices = sliced_text,
                                                       offset_step = k_token._init_index)

            splitted_token[0].tag = "B-" + splitted_token[0].tag
            for t in splitted_token[1:]:
                t.tag = "I-" + t.tag
            
            known_tokens += splitted_token

        self.known_tokens = sort_tokens(known_tokens)
                        
    def _fit_known_tokens(self):
        """
        Reserves the space of the known tokens by trimming out their regions in the words.
        E.i. if a word occupies the space of a known token 
        """

        for k_token in self.known_tokens:

            inside_flag = False
            token_span = []

            # TODO: Create an utilitary function for finding all the tokens in a specified span - apply to all points of the code where it occurs
            for w_token in self.word_tokens:
                if w_token.enclosing(k_token._init_index):
                    inside_flag = True
                    token_span.append(w_token)
                    # The end and init of the token are inside the same token
                    if w_token.enclosing(k_token._end_index):
                        break
        
                elif w_token.enclosing(k_token._end_index):
                    inside_flag = False
                    token_span.append(w_token)                    

                elif inside_flag:
                    token_span.append(w_token)

            for token in [self._trim_token(token, k_token._init_index, k_token._end_index) for token in token_span]:
                if token:
                    self.word_tokens += token

            # TODO: Create an utilitary function for deleting all the tokens in a specified span - apply to all points of the code where it occurs
            for token in token_span:
                self.word_tokens.remove(token)
            
            self.word_tokens = sort_tokens(self.word_tokens)

    def _trim_token(self, token, init, end):
        """
        Trim out the region defined by init and end.
        Returns the subtokens if any is produced, an empty list if none is.
        """
        tokens = []        
        if token.enclosing(init) and init != token._init_index:
            
            left_token_start = token._init_index
            left_token_end = init #- 1

            if left_token_end != left_token_start:
                # TODO: Create auxiliary function to build a token in the specified segment - apply to all points of the code where it occurs
                left_token = Token(text = self._text[left_token_start:left_token_end],
                                    init_index = left_token_start,
                                    end_index = left_token_end - 1,
                                    tag = token.tag)

                tokens.append(left_token)
        
        if token.enclosing(end) and end != token._end_index:
            
            rigth_token_start = end #+ 1
            rigth_token_end = token._end_index

            if rigth_token_end != rigth_token_start:
                rigth_token = Token(text = self._text[rigth_token_start + 1:rigth_token_end + 1],
                                    init_index = rigth_token_start + 1,
                                    end_index = rigth_token_end,
                                    tag = token.tag)

                tokens.append(rigth_token)

        return tokens

    def save_conll_file(self, save_path):
        with open(save_path, "w") as f:
            for i, sentence in enumerate(self.sentences_tokens):
                # TODO: Create property to get the word tokens and known tokens together
                # TODO: Use auxiliary library for conll file manipulation
                # TODO: Build a smarter loop
                # TODO: Ensure all tokens were written - sanity test
                for token in sort_tokens(self.word_tokens + self.known_tokens):
                    if sentence.enclosing(token._init_index):
                        f.write(token._text+" "+token.tag+"\n")
                if i != len(self.sentences_tokens) - 1:
                    f.write("\n")