# About
A pipeline for structuring text from various sources as a dataset for NER models.

The outputs are in the form of IOB files

# Description and examples

The dataset is built from 2 inputs:
 - The raw text
 - The known tokens in the text

``` python
# text example
text = 'Texto para teste. Este texto contém 3 frases. 3a frase.'

# known token example
token_text = 'para teste'
init = text.find(token_text)
end = init + len(token_text) - 1

known_token = Token(token_text, init, end, "PER")
```

The is created and the rules applied:
``` python
pipeline.apply_processing_rules()
```

To save the processed text:
``` python
pipeline.save_conll_file('file.iob')
```

The system employs a few rules for structuring the text:
1. The text sentences are tokenized utilizing the nltk library

2. The sentences words are tokenized utilizing the nltk library

3. **If** the tokenized sentences do not contain the known token token, all the sentences is between the beggining and end of the token are merged.

4. **If** the tokenized words do not contain the known token, the parts of the words the contain the word are extracted and attributed to the known token.

5. The known tokens are splitted trough a simple space tokenizer

# Other
  - For future improvments some comments starting with TODO are present in the code describing the proposed change
  - The functions responsible for  tokenizing sentences and words are in the utils 