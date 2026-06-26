import re
import json
import os
from typing import List, Dict, Any, Tuple
import numpy as np

# Standard hardcoded English stopwords list as a fallback to avoid NLTK download errors
STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as", "at",
    "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't", "cannot", "could",
    "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", "each", "few", "for",
    "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's",
    "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm",
    "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't",
    "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours",
    "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't",
    "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there",
    "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too",
    "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "weren't", "what",
    "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with",
    "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"
}

class TextPreprocessor:
    """
    Handles text cleaning, tokenization, padding, and word mapping for deep learning models.
    """
    def __init__(self, max_words: int = 10000, max_len: int = 100):
        self.max_words = max_words
        self.max_len = max_len
        self.word_index = {}
        self.index_word = {}

    def clean_text(self, text: str) -> str:
        """
        Cleans the input text by removing HTML tags, URLs, special characters, and converting to lowercase.
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove HTML tags
        text = re.sub(r'<[^>]*>', ' ', text)
        
        # Remove URLs
        text = re.sub(r'https?://\S+|www\.\S+', ' ', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', ' ', text)
        
        # Keep only letters, digits, spaces and basic punctuation
        text = re.sub(r'[^a-zA-Z0-9\s\'!\?\.]', ' ', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    def tokenize_and_remove_stopwords(self, text: str) -> List[str]:
        """
        Tokenizes text and filters out common stopwords.
        """
        cleaned = self.clean_text(text)
        tokens = cleaned.split()
        return [word for word in tokens if word not in STOPWORDS]

    def fit_on_texts(self, texts: List[str]):
        """
        Fits the tokenizer on a list of texts.
        """
        word_counts = {}
        for text in texts:
            cleaned = self.clean_text(text)
            for word in cleaned.split():
                if word:
                    word_counts[word] = word_counts.get(word, 0) + 1
        
        # Sort words by frequency
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Build index, reserve 0 for padding and 1 for OOV (Out Of Vocabulary)
        self.word_index = {"<PAD>": 0, "<OOV>": 1}
        for i, (word, _) in enumerate(sorted_words[:self.max_words - 2]):
            self.word_index[word] = i + 2
            
        self.index_word = {v: k for k, v in self.word_index.items()}

    def texts_to_sequences(self, texts: List[str]) -> List[List[int]]:
        """
        Converts text list to integer sequence representations.
        """
        sequences = []
        for text in texts:
            cleaned = self.clean_text(text)
            seq = []
            for word in cleaned.split():
                if word:
                    # Look up word, default to OOV (1)
                    seq.append(self.word_index.get(word, 1))
            sequences.append(seq)
        return sequences

    def pad_sequences(self, sequences: List[List[int]], max_len: int = None) -> np.ndarray:
        """
        Pads sequences to max_len (post-padding and post-truncating by default).
        """
        if max_len is None:
            max_len = self.max_len
            
        padded = np.zeros((len(sequences), max_len), dtype=np.int32)
        for i, seq in enumerate(sequences):
            if not seq:
                continue
            if len(seq) > max_len:
                padded[i, :] = seq[:max_len]  # Truncate
            else:
                padded[i, :len(seq)] = seq    # Pad with zeros (trailing)
        return padded

    def save(self, filepath: str):
        """
        Saves tokenizer dictionary to a JSON file.
        """
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        data = {
            "max_words": self.max_words,
            "max_len": self.max_len,
            "word_index": self.word_index
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, filepath: str) -> 'TextPreprocessor':
        """
        Loads tokenizer dictionary from a JSON file.
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        preprocessor = cls(max_words=data["max_words"], max_len=data["max_len"])
        preprocessor.word_index = data["word_index"]
        preprocessor.index_word = {v: k for k, v in preprocessor.word_index.items()}
        return preprocessor
