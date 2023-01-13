import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import nltk
import spacy
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

import streamlit as st
import pickle


def main():
    class TextProcessor:

        lemma = WordNetLemmatizer()
        nlp = spacy.load("en_core_web_sm")
        swds_set = set(stopwords.words('english'))
        swds_set.update(('bofa', 'nsf', 'boa', 'synchrony', 'amerisave', 'america', 'bank', 'chime', 
            'bb', 'mr', 'mrs', 'ms', 'ocwen', 'sls', 'rushmore', 'robinhood', 'llc', 'would', 'could',
            'please', 'will', 'can'))

        def fit(self, X, y=None):
            pass

        def transform(self, X, y=None):
            results = self.clean_text(X) 
            return results

        def fit_transform(self, X, y=None):
            self.fit(X)
            return self.transform(X)

        def get_ners(self, x):
            ners = {}
            doc = TextProcessor.nlp(x)
            for ent in doc.ents:
                ners[ent.text] = ners.get(ent.text, 0) + 1
            return ners

        def clean_text(self, x):
            # replace punctuation with space
            x = re.sub(r'[^\w\s]', ' ', x)
            # replace number with space
            x = "".join(
                [char for char in x if char.isalpha() or char == " "]
            )
            # replace Xx, Yy, Zz at least appear twice with space 
            x = re.sub('[Xx|Yy|Zz]{2,}', ' ', x)
            #remove more than one space between words
            x = ' '.join(x.split())

            ners = self.get_ners(x)
            for ner in ners:
                x = re.sub(ner, ' ', x)

            # remove stopwords
            x = " ".join(
                [
                    word for word in x.lower().split()
                    if word not in TextProcessor.swds_set
                ]
            )
            # tokenize
            x = nltk.word_tokenize(x)
            # lemmatization
            x = [TextProcessor.lemma.lemmatize(word, "v") for word in x]
            x = " ".join(x)
            return x
    
    
    # streamlit webapp
    st.write("""
    # Bank Complaint Loss Detector
    
    This app predicts whether a given bank complaint requires monetary compensation
    
    """)
    
    tp = TextProcessor()
    model = pickle.load(open('model.pck','rb'))

    
    
   # singal complaint
    st.subheader("Single Complaint Analyzer")
    complaint = st.text_area('',"""
    """)
    if complaint and st.button('Submit'):
        df = pd.DataFrame({'complaint': [complaint]})
        text = df.complaint.map(tp.clean_text)
        single_pred = model.predict(text)
        if single_pred == 1:
            st.write("monetary loss")
        else:
            st.write("low probability of monetary loss")
    
    # Batch complaint csvs
    st.subheader("Complaint Batch Processor")
    uploaded_file = st.file_uploader('Upload your csv file here')
    if uploaded_file:
        df = pd.read_csv(uploaded_file, header = 0, names = ['id', 'complaint'])
        st.write(df.head())

    batch_pred = st.button('Predict', key = 'batch')
    if batch_pred:
        if isinstance(df, pd.DataFrame):
            with st.spinner(text="In progress..."):
                time.sleep(5)

                text = df.complaint.map(tp.clean_text)

                y_pred = pd.DataFrame(model.predict(text), columns = ['Loss'])
                y_pred_prob = pd.DataFrame(model.predict_proba(text)[:, 1], columns = ['Probability of Loss'])
                output = pd.concat([df, y_pred], axis = 1)
        else:
            st.write('Please upload data first.')

    if not output.empty:
        st.write('Results:')
        AgGrid(output)
        st.download_button('Download results', data = output.to_csv(), file_name= 'results.csv', mime = 'text/csv')
                  
if __name__ == '__main__':
    main()