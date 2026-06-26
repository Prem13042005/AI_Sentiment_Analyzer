import numpy as np
import random
from typing import List, Dict, Tuple, Callable, Any
from sklearn.linear_model import Ridge
import re

class LimeTextExplainer:
    """
    A lightweight, custom implementation of Local Interpretable Model-agnostic Explanations (LIME) for text.
    Fits a local Ridge regression model to calculate word-level sentiment attribution scores.
    """
    def __init__(self, num_samples: int = 250, keep_prob: float = 0.7):
        self.num_samples = num_samples
        self.keep_prob = keep_prob

    def explain(
        self,
        text: str,
        predict_fn: Callable[[List[str]], np.ndarray]
    ) -> Dict[str, Any]:
        """
        Generates word-level explanation weights for a given text.
        
        Args:
            text: Raw input text.
            predict_fn: A function that takes a list of strings and returns an np.ndarray 
                        of shape (N, 2) where col 0 is negative prob and col 1 is positive prob.
                        
        Returns:
            Dictionary containing:
                - "original_text": input text
                - "words": list of words in sequence
                - "positive_contributions": list of dicts {"word": w, "weight": wt}
                - "negative_contributions": list of dicts {"word": w, "weight": wt}
                - "intercept": linear regression base intercept
        """
        # Clean and split into words
        # Keep punctuation separate or keep words clean
        words = text.split()
        num_words = len(words)
        
        if num_words == 0:
            return {
                "original_text": text,
                "words": [],
                "positive_contributions": [],
                "negative_contributions": [],
                "intercept": 0.5
            }

        # Handle very short texts
        if num_words < 2:
            return {
                "original_text": text,
                "words": words,
                "positive_contributions": [{"word": words[0], "weight": 0.0}],
                "negative_contributions": [],
                "intercept": 0.5
            }

        # 1. Generate perturbed samples (binary vectors indicating word presence/absence)
        # The first sample is always the original text (all 1s)
        X_perturbed = np.ones((self.num_samples, num_words), dtype=np.int32)
        perturbed_texts = [text]
        
        for i in range(1, self.num_samples):
            # Decide which words to keep
            mask = np.random.binomial(1, self.keep_prob, num_words)
            # Ensure we don't end up with an empty text
            if np.sum(mask) == 0:
                mask[random.randint(0, num_words - 1)] = 1
                
            X_perturbed[i, :] = mask
            # Join kept words to create the perturbed text
            perturbed_sentence = " ".join([words[j] for j in range(num_words) if mask[j] == 1])
            perturbed_texts.append(perturbed_sentence)
            
        # 2. Get predictions for all perturbed texts
        # probabilities shape: (num_samples, 2) - [Neg_prob, Pos_prob]
        probabilities = predict_fn(perturbed_texts)
        
        # Target is the Positive class probability
        y_perturbed = probabilities[:, 1]
        
        # 3. Apply weights to perturbations based on similarity to original (all 1s)
        # Cosine distance or exponential kernel on distance
        # We can calculate Euclidean distance from the original vector (all 1s)
        distances = np.sqrt(np.sum((X_perturbed - 1.0) ** 2, axis=1))
        # Exponential kernel weight: e^(-d^2 / sigma^2)
        sigma = 0.75 * np.sqrt(num_words)
        weights = np.exp(- (distances ** 2) / (sigma ** 2))
        
        # 4. Fit a weighted Ridge regression model
        reg = Ridge(alpha=1.0, fit_intercept=True)
        reg.fit(X_perturbed, y_perturbed, sample_weight=weights)
        
        # 5. Extract coefficients
        coefficients = reg.coef_
        intercept = float(reg.intercept_)
        
        # Map coefficients to words
        # If words occur multiple times, accumulate their weights
        word_attributions = {}
        for idx, word in enumerate(words):
            # Clean punctuation from word for visualization list
            clean_word = re.sub(r'[^a-zA-Z0-9]', '', word).lower()
            if not clean_word:
                continue
            word_attributions[clean_word] = word_attributions.get(clean_word, 0.0) + float(coefficients[idx])
            
        # Separate positive and negative contributions
        pos_contribs = []
        neg_contribs = []
        
        for w, weight in word_attributions.items():
            if weight > 0:
                pos_contribs.append({"word": w, "weight": round(weight, 5)})
            elif weight < 0:
                neg_contribs.append({"word": w, "weight": round(abs(weight), 5)}) # positive magnitude of neg contrib
                
        # Sort by weight descending
        pos_contribs = sorted(pos_contribs, key=lambda x: x["weight"], reverse=True)
        neg_contribs = sorted(neg_contribs, key=lambda x: x["weight"], reverse=True)
        
        # Also return sequence attribution map (ordered by input words)
        sequence_attributions = []
        for idx, word in enumerate(words):
            sequence_attributions.append({
                "word": word,
                "weight": float(coefficients[idx])
            })
            
        return {
            "original_text": text,
            "words": words,
            "positive_contributions": pos_contribs,
            "negative_contributions": neg_contribs,
            "sequence_attributions": sequence_attributions,
            "intercept": round(intercept, 4)
        }
