# import libraries
import spacy
import itertools
import re
import json

from spacy import displacy
from spacy.matcher import PhraseMatcher
from assets.columns import Columns
from assets.entities import Entities
from assets.db_model import DBModel
from assets.type_converter import get_value, get_token_child_len, get_neighbour_tokens, get_type, replace_string, replace_entities
from assets.sql_model import SQLGenerator
from assets.matcher import Matcher
from configuration.config import Configuration

#load the configuration
config = Configuration()
# load the DB Model
db_model = DBModel()
# remove unneccesary words
stan_stop_words = [line.rstrip('\n') for line in open("stopwords.txt")]
# load spacy's english model
nlp = spacy.load('en_core_web_sm')

exceptions = ["between", "more", "than"]
lemma_exceptions = ["greater", "less", "than", "more"]

custom_matcher = Matcher()
custom_matcher = db_model.get_custom_matcher(custom_matcher, nlp)


def process_sentence(sentence):

    sentence = sentence.replace("total number", "count")
    sentence = sentence.replace("total", "sum")

    new_sentence = ""
    for word in sentence.split():
        if word not in stan_stop_words:
            new_sentence += word + " "
    sentence = new_sentence.lstrip()

    for loaded_entity in db_model.loaded_entities:
        for loaded_entity_value in loaded_entity[1]:
            if loaded_entity_value.lower() in sentence:
                sentence = replace_entities(sentence, loaded_entity_value, loaded_entity_value)

    doc = nlp(sentence)

    identified_spans = []
    identified_entities = []

    for chunk in doc.noun_chunks:
        identified_spans.append(chunk.text)

    for ent in doc.ents:
        identified_entities.append(ent.text)

    lemmatizedSentence = ''
    for token in doc:
        lemmatizedSentence = lemmatizedSentence + (token.text if token.text in lemma_exceptions else token.lemma_) + " "
    lemmatizedSentence = lemmatizedSentence.lstrip()

    spacy_stopwords = spacy.lang.en.stop_words.STOP_WORDS

    matches = custom_matcher.find(lemmatizedSentence)
    matched_entities = []
    matched_columns = []
    for match in matches:
        if match[0].endswith("TABLE"):
            matched_entities.append(Entities(match[0].replace("_TABLE","")))
            lemmatizedSentence = replace_string(lemmatizedSentence, str(match[1]), match[0].replace("_TABLE",""))
        if match[0].endswith("COLUMN"):
            columnType = [c.type_ for c in db_model.columns if c.name == match[0].replace("_COLUMN","").lower()]
            if len(columnType) > 0:
                columnType = columnType[0]
            matched_columns.append(Columns(match[0].replace("_COLUMN",""), columnType))
            lemmatizedSentence = replace_string(lemmatizedSentence, str(match[1]), match[0].replace("_COLUMN",""))

    docLemmatized = nlp(lemmatizedSentence)

    for token in docLemmatized:

        if token.text.upper() in [m.name for m in matched_entities]:
            matched_entity = next(me for me in matched_entities if me.name == token.text.upper())

            contextual_span = get_neighbour_tokens(token)
            span_ranges = re.split(config.get_phrase_splitter(), contextual_span)
            for span in span_ranges:
                if matched_entity.name.lower() in span:
                    matched_entity.condition = "="
                    if "average" in span:
                        matched_entity.isAverage = True
                    if "avg" in span:
                        matched_entity.isAverage = True
                    if "maximum" in span:
                        matched_entity.isMax = True
                    if "max" in span:
                        matched_entity.isMax = True
                    if "minimum" in span:
                        matched_entity.isMin = True
                    if "min" in span:
                        matched_entity.isMin = True
                    if "count" in span:
                        matched_entity.isCount = True
                    if "sum" in span:
                        matched_entity.isSum = True
                    if "total" in span:
                        matched_entity.isSum = True

                    trimmed_span = span \
                        .replace("average", "") \
                        .replace("maximum", "") \
                        .replace("minimum", "") \
                        .replace("greater than", "") \
                        .replace("less than", "") \
                        .replace("more than", "") \
                        .replace("min", "") \
                        .replace("max", "") \
                        .replace("count", "") \
                        .replace("sum", "")
                    trimmed_span = ' '.join(trimmed_span.split())
                    doc_span = nlp(trimmed_span)

                    for span_token in doc_span:

                        if span_token.text.lower() == matched_entity.name.lower():

                            if get_token_child_len(span_token) > 0:
                                span_token_child = next(itertools.islice(span_token.children, 1))
                                ent = next(en for en in db_model.entities if en.name.lower() == matched_entity.name.lower())
                                default_column = next(col for col in ent.columns if col.name.lower() == ent.defaultColumn.lower())
                                value = get_value(span_token_child.text, default_column.type_)

                                identified_entity_exists = False
                                for identified_entity in identified_entities:
                                    if identified_entity in trimmed_span and str(value) in identified_entity:
                                        identified_entity_exists = True
                                        value = identified_entity
                                matched_entity.value_ = value


                    
            matched_entities = [me for me in matched_entities if me.name != token.text.upper()]
            matched_entities.append(matched_entity)
        
        if token.text.upper() in [m.name for m in matched_columns]:
            matched_column = next(mc for mc in matched_columns if mc.name == token.text.upper())

            contextual_span = get_neighbour_tokens(token)
            span_ranges = re.split(config.get_phrase_splitter(), contextual_span)
            for span in span_ranges:
                # print("column : ", span)
                if matched_column.name.lower() in span:
                    matched_column.condition = "="
                    if "average" in span:
                        matched_column.isAverage = True
                    if "avg" in span:
                        matched_column.isAverage = True
                    if "maximum" in span:
                        matched_column.isMax = True
                    if "max" in span:
                        matched_column.isMax = True
                    if "minimum" in span:
                        matched_column.isMin = True
                    if "min" in span:
                        matched_column.isMin = True
                    if "greater than" in span:
                        matched_column.condition = ">"
                    if "more than" in span:
                        matched_column.condition = ">"
                    if "less than" in span:
                        matched_column.condition = "<"
                    if "count" in span:
                        matched_column.isCount = True
                    if "sum" in span:
                        matched_column.isSum = True
                    if "total" in span:
                        matched_column.isSum = True
                    
                    trimmed_span = span \
                        .replace("average", "") \
                        .replace("maximum", "") \
                        .replace("minimum", "") \
                        .replace("greater than", "") \
                        .replace("less than", "") \
                        .replace("more than", "") \
                        .replace("min", "") \
                        .replace("max", "") \
                        .replace("count", "") \
                        .replace("sum", "")
                    trimmed_span = ' '.join(trimmed_span.split())
                    
                    doc_span = nlp(trimmed_span)

                    for span_token in doc_span:
                        if span_token.text.lower() == matched_column.name.lower():
                            if get_token_child_len(span_token) > 0:
                                span_token_child = next(itertools.islice(span_token.children, 1))
                                value = get_value(span_token_child.text, matched_column.type_)

                                identified_entity_exists = False
                                for identified_entity in identified_entities:
                                    if identified_entity in trimmed_span and str(value) in identified_entity and get_value(identified_entity, matched_column.type_) != "NoValue":
                                        identified_entity_exists = True
                                        value = identified_entity
                                matched_column.value_ = value
                                

            matched_columns = [mc for mc in matched_columns if mc.name != token.text.upper()]
            matched_columns.append(matched_column)

    for loaded_entity in db_model.loaded_entities:
        entity_name = loaded_entity[0]
        for loaded_entity_value in loaded_entity[1]:
            if loaded_entity_value.lower() in lemmatizedSentence.lower():
                if entity_name.lower() in [me.name.lower() for me in matched_entities]:
                    print("entity already processed")
                else:
                    en_def_col = next(col for en in db_model.entities if en.name.lower() == entity_name.lower() for col in en.columns if col.name.lower() == en.defaultColumn.lower())
                    if get_value(loaded_entity_value, en_def_col.type_) != "NoValue":
                        ent = Entities(entity_name.upper())
                        ent.condition = "="
                        ent.value_ = get_value(loaded_entity_value, en_def_col.type_)
                        matched_entities.append(ent)

    sql_generator = SQLGenerator(matched_entities, matched_columns, db_model)
    print("=================================================================================")
    result = sql_generator.get_sql()
    response = {}
    response['sql'] = sql_generator.query
    response['result'] = result[0]
    response['columns'] = result[1]
    return response




#########################

from tkinter import *
from tkinter import scrolledtext

window = Tk()
window.title('Convert Text to SQL')
window.geometry('475x400')

# Main Heading

main_heading = Label(window, text='Enter a query in natural language', font=('Arial Bold', 24))
main_heading.grid(column = 0, row = 0)

# Text Input
txt = Entry(window,width=50)
txt.grid(column = 0, row = 1)
txt.focus()

# Output Query
qury = Label(window, text='Project by 17BCE2189 & 16BCB0137', font=('Ubuntu Mono Bold', 18))
qury.grid(column=0, row = 2)
gen = scrolledtext.ScrolledText(window,width=40,height=20)
gen.grid(column=0, row=3)

def clicked():
    q = json.dumps(process_sentence(txt.get()),indent=2)
    gen.insert(INSERT,q)

btn = Button(window, text='Convert to SQL', bg='white', fg='black', command=clicked)
btn.grid(column = 0, row = 4)
window.mainloop()


