#!/usr/bin/env bash

# Install dependencies
pip install sklearn tqdm pyspellchecker nltk python-Levenshtein pandas matplotlib


## Parsing
cd Parsing
python decoder_1.py
python decoder_12.py
python decoder_17.py
python decoder_18.py

python group_leaders_1.py
python group_leaders_1x.py 12
python group_leaders_1x.py 17
python group_leaders_1x.py 18

cd ..


## Modelling
cd Modelling
python tokenizer.py 1  
python tokenizer.py 12  
python tokenizer.py 17 
python tokenizer.py 18 

python divide_in_parties_1.py 
python divide_in_parties_1x.py 12 
python divide_in_parties_1x.py 17
python divide_in_parties_1x.py 18

#mkdir perplexity_score
python lda_modelling.py 40
python compare.py 40 final_table.png

