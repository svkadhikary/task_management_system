import pandas as pd
import numpy as np
import warnings
from logger_n_exception.logger import logging
warnings.filterwarnings("ignore")

import pickle
import spacy

if not spacy.util.is_package('en_core_web_md'):
    logging.info("Downloading the medium-sized English model for spaCy...")
    spacy.cli.download('en_core_web_md')
# Load the medium-sized English model
spacy_nlp = spacy.load('en_core_web_md')


def preprocess_with_spacy(text, return_vector=False):
    """Returns both cleaned text and vector (or just one)"""
    text = text.strip().lower()
    doc = spacy_nlp(text)
    
    # Text preprocessing (same as before)
    tokens = [token.lemma_ for token in doc 
              if not token.is_stop 
              and not token.is_punct 
              and not token.like_num]
    clean_text = " ".join(tokens)
    
    # Vectorization
    if return_vector:
        return clean_text, doc.vector  # returns tuple (text, vector)
    return clean_text  # or just text if vectors not needed

def predict_task_category(task_desc):
    try:    
        with open('nlp/tfidf_vect.pkl', 'rb') as f:
            tfidf_vect = pickle.load(f)

        with open('nlp/lbl_enc_cat.pkl', 'rb') as f:
            lbl_enc_cat = pickle.load(f)
        
        with open('nlp/category_predict.pkl', 'rb') as f:
            cat_predict = pickle.load(f)
    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
        return "Model not found"
    
    task_desc_cleaned = preprocess_with_spacy(task_desc)
    task_desc_vectorized = tfidf_vect.transform([task_desc_cleaned])

    predicted_category = lbl_enc_cat.inverse_transform(cat_predict.predict(task_desc_vectorized))[0]
    
    return predicted_category


def predict_task_type(task_desc):

    try:    
        with open('nlp/tfidf_vect.pkl', 'rb') as f:
            tfidf_vect = pickle.load(f)

        with open('nlp/lbl_enc.pkl', 'rb') as f:
            lbl_enc = pickle.load(f)
        
        with open('nlp/type_predict.pkl', 'rb') as f:
            cat_predict = pickle.load(f)
    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
        return "Model not found"
    
    task_desc_cleaned = preprocess_with_spacy(task_desc)
    task_desc_vectorized = tfidf_vect.transform([task_desc_cleaned])

    predicted_type = lbl_enc.inverse_transform(cat_predict.predict(task_desc_vectorized))[0]
    
    return predicted_type

def predict_task_info(task_desc):
    """Predicts both category and type of the task"""
    try:
        category = predict_task_category(task_desc)
        task_type = predict_task_type(task_desc)
        logging.info(f"Predicted category: {category}, type: {task_type} for task description.")
    except Exception as e:
        logging.error(f"Error during task info prediction: {e}")
        return None, None
    
    return category, task_type




