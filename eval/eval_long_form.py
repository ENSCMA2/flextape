from spacy.pipeline.ner import DEFAULT_NER_MODEL
from spacy.lang.en import English

nlp = English()

config = {
   "moves": None,
   "update_with_oracle_cut_size": 100,
   "model": DEFAULT_NER_MODEL,
   "incorrect_spans_key": "incorrect_spans",
}
nlp.add_pipe("ner", config=config)