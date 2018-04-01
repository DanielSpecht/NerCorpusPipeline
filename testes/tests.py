import os
import sys
import unittest
sys.path.insert(0, '../src')
import utils
from Token import Token
from ner_corpus_pipeline import NerCorpusPipeline

class test_token_class(unittest.TestCase):
    
    def test_base_case(self):
        text = "text"

        Token(text = text,
              init_index = 0,
              end_index = len(text) - 1,
              tag = "tag")
    
    def test_invalid_annotation(self):
        text = "text"

        with self.assertRaises(Exception):
            Token(text = text,
                  init_index = 0,
                  end_index = 1,
                  tag = "tag")

    def test_contains_method(self):
        text = "text"
        
        token = Token(text = text,
                  init_index = 0,
                  end_index = len(text) - 1,
                  tag = "tag")
        
        # In the middle 
        self.assertTrue(token.enclosing(1))

        # On the borders
        self.assertTrue(token.enclosing(0))
        self.assertFalse(token.enclosing(len(text)))

class test_tokenizers(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls._text = 'Texto para teste. Este texto contém 3 frases. 3a frase.'
    
    def test_sentence_tokenizer(self):
        sentence_tokens = utils.get_sentence_tokens(self._text)
        for token in sentence_tokens:
            self.assertTrue(self._text[token._init_index:token._end_index + 1] == token._text)

    def test_word_tokenizer(self):
        word_tokens = utils.get_word_tokens(self._text)        
        for token in word_tokens:
            self.assertTrue(self._text[token._init_index:token._end_index + 1] == token._text)

class test_corpus_pipeline(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self._text = 'Texto para teste. Este texto contém 3 frases. 3a frase.'
        self._st1, self._st2, self._st3 = utils.get_sentence_tokens('Texto para teste. Este texto contém 3 frases. 3a frase.')
        
        self._st1_words = utils.get_word_tokens(self._st1._text)
        self._st2_words = utils.get_word_tokens(self._st2._text)
        self._st3_words = utils.get_word_tokens(self._st3._text)

        self._created_file_name = "./resources/test.conll"
        self._correct_file_name = "./resources/correct_test.conll"


    def test_merge_2_sentences(self):
        # Create a token positioned between the forst and second sentence
        text = 'teste. Este'
        init = self._text.find(text)
        end = init + len(text) - 1
        known_token = Token(text, init, end, "teste")

        pipeline = NerCorpusPipeline(self._text, [known_token])
        pipeline.apply_processing_rules()

        sentence_tokens = pipeline.sentences_tokens

        # Ensure the sentences have a valid structure
        for token in sentence_tokens:
            self.assertTrue(self._text[token._init_index:token._end_index + 1] == token._text)

        # Ensure sentence was correctlly merged
        self.assertTrue(len(sentence_tokens) == 2)
        # 1 merged
        self.assertTrue([t for t in sentence_tokens if t._text == self._text[self._st1._init_index : self._st2._end_index + 1]][0])
        # 1 untouched
        self.assertTrue([t for t in sentence_tokens if t._text == self._st3._text][0])

    def test_merge_3_sentences(self):
        # Create a token positioned between the forst and second sentence
        text = 'te. Este texto contém 3 frases. 3a'
        init = self._text.find(text)
        end = init + len(text) - 1
        known_token = Token(text, init, end, "teste")

        pipeline = NerCorpusPipeline(self._text, [known_token])
        pipeline.apply_processing_rules()

        sentence_tokens = pipeline.sentences_tokens

        # Ensure the sentences have a valid structure
        for token in sentence_tokens:
            self.assertTrue(self._text[token._init_index:token._end_index + 1] == token._text)

        # Ensure sentence was correctlly merged
        self.assertTrue(len(sentence_tokens) == 1)
        # 1 merged
        self.assertTrue([t for t in sentence_tokens if t._text == self._text[self._st1._init_index : self._st3._end_index + 1]][0])
    
    def split_known_tokens_no_subtokens_test(self):
        pass

    def test_split_known_tokens_create_2_subtokens(self):
        text = 'para teste'
        init = self._text.find(text)
        end = init + len(text) - 1
        known_token = Token(text, init, end, "teste")

        pipeline = NerCorpusPipeline(self._text, [known_token])

        self.assertTrue(len(pipeline.known_tokens) == 1)

        pipeline.apply_processing_rules()

        self.assertTrue(len(pipeline.known_tokens) == 2)

        # Same text
        self.assertTrue(set(['para', 'teste']) == set([t._text for t in pipeline.known_tokens]))
        # Ensure the tokens have a valid structure
        for token in pipeline.known_tokens:
            self.assertTrue(self._text[token._init_index:token._end_index + 1] == token._text)

    def test_fit_known_tokens_create_token_to_the_left(self):
        # Create a token positioned inside the first word
        text = 'to' # Tex-to
        init = self._text.find(text)
        end = init + len(text) - 1
        known_token = Token(text, init, end, "teste")

        # Only the first sentence will be used
        text = self._st1._text
        word_tokens_before = utils.get_word_tokens(text)

        pipeline = NerCorpusPipeline(text, [known_token])
        pipeline.apply_processing_rules()

        word_tokens_after = pipeline.word_tokens

        # Ensure the words have a valid structure
        for token in word_tokens_after:
            self.assertTrue(self._text[token._init_index:token._end_index + 1] == token._text)

        # Ensure the known tokens have a valid structure
        for token in pipeline.known_tokens:
            self.assertTrue(self._text[token._init_index:token._end_index + 1] == token._text)

        self.assertTrue(len(word_tokens_after) == 4)
        self.assertTrue(set(['Tex', 'to', 'para', 'teste', '.']) == set([t._text for t in utils.sort_tokens(pipeline.known_tokens + word_tokens_after)]))

    def test_fit_known_tokens_create_token_to_the_rigth(self):
        # Create a token positioned inside the first word
        text = 'Tex' # Tex-to
        init = self._text.find(text)
        end = init + len(text) - 1
        known_token = Token(text, init, end, "teste")

        # Only the first sentence will be used
        text = self._st1._text

        pipeline = NerCorpusPipeline(text, [known_token])
        pipeline.apply_processing_rules()

        word_tokens_after = pipeline.word_tokens

        # Ensure the words have a valid structure
        for token in word_tokens_after:
            self.assertTrue(self._text[token._init_index:token._end_index + 1] == token._text)

        # Ensure the known tokens have a valid structure
        for token in pipeline.known_tokens:
            self.assertTrue(self._text[token._init_index:token._end_index + 1] == token._text)

        self.assertTrue(len(word_tokens_after) == 4)
        self.assertTrue(set(['Tex', 'to', 'para', 'teste', '.']) == set([t._text for t in utils.sort_tokens(pipeline.known_tokens + word_tokens_after)]))

    def test_fit_known_tokens_create_token_to_the_rigth_and_left(self):
        # Create a token positioned inside the first word
        text = 'ext' # T-ext-o
        init = self._text.find(text)
        end = init + len(text) - 1
        known_token = Token(text, init, end, "teste")

        # Only the first sentence will be used
        text = self._st1._text

        pipeline = NerCorpusPipeline(text, [known_token])
        pipeline.apply_processing_rules()

        word_tokens_after = pipeline.word_tokens

        # Ensure the words have a valid structure
        for token in word_tokens_after:
            self.assertTrue(self._text[token._init_index:token._end_index + 1] == token._text)

        # Ensure the known tokens have a valid structure
        for token in pipeline.known_tokens:
            self.assertTrue(self._text[token._init_index:token._end_index + 1] == token._text)
            
        self.assertTrue(set(['T', 'ext', 'o', 'para', 'teste', '.']) == set([t._text for t in utils.sort_tokens(pipeline.known_tokens + word_tokens_after)]))

    def test_fit_known_tokens_create_token_to_the_rigth_and_left_between_2_tokens(self):
        # Create a token positioned inside the first word
        text = 'xto par' # T-ex-to
        init = self._text.find(text)
        end = init + len(text) - 1
        known_token = Token(text, init, end, "teste")

        # Only the first sentence will be used
        text = self._st1._text

        pipeline = NerCorpusPipeline(text, [known_token])
        pipeline.apply_processing_rules()

        word_tokens_after = pipeline.word_tokens

        # Ensure the words have a valid structure
        for token in word_tokens_after:
            self.assertTrue(self._text[token._init_index:token._end_index + 1] == token._text)

        # Ensure the known tokens have a valid structure
        for token in pipeline.known_tokens:
            self.assertTrue(self._text[token._init_index:token._end_index + 1] ==  token._text)

        #self.assertTrue(len(word_tokens_after) == 4)
        self.assertTrue(set(['Te', 'xto', 'par', 'a', 'teste', '.']) == set([t._text for t in utils.sort_tokens(pipeline.known_tokens + word_tokens_after)]))

    def test_IOB_file_creation(self):

        token_text = 'para teste'
        init = self._text.find(token_text)
        end = init + len(token_text) - 1
        known_token = Token(token_text, init, end, "PER")

        pipeline = NerCorpusPipeline(self._text, [known_token])
        pipeline.apply_processing_rules()


        pipeline.save_conll_file(self._created_file_name)
        self.assertTrue(open(self._created_file_name,"r").read() == open(self._correct_file_name,"r").read())

    @classmethod
    def tearDownClass(self):
        try:
            os.remove(self._created_file_name)
        except:
            pass

if __name__ == '__main__':
    unittest.main()