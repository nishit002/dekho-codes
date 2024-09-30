import streamlit as st
import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

# Function to load the files
def load_file(file):
    return pd.read_csv(file)

# Function to calculate fuzzy similarity score
def fuzzy_match(college_name, college_list):
    return process.extractOne(college_name, college_list, scorer=fuzz.token_sort_ratio)

# Function to apply TF-IDF vectorizer and cosine similarity for college names
def match_using_tfidf(college_name_a, college_list_b):
    vectorizer = T
