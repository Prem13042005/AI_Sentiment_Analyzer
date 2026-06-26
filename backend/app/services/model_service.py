import os
import time
import json
import numpy as np
import tensorflow as tf
import torch
from typing import List, Dict, Any, Tuple
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from backend.app.utils.preprocess import TextPreprocessor
from backend.app.utils.train_models import AttentionLayer

class ModelService:
    """
    Singleton service that loads and coordinates predictions for all NLP sentiment models.
    Supports BiLSTM, GRU Attention, CNN-LSTM, DistilBERT, and an Ensemble of all four.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ModelService, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if self.initialized:
            return
            
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        self.models_dir = os.path.join(self.base_dir, "models")
        
        # Load Preprocessor / Tokenizer
        tokenizer_path = os.path.join(self.models_dir, "tokenizer.json")
        if os.path.exists(tokenizer_path):
            self.preprocessor = TextPreprocessor.load(tokenizer_path)
            print("ModelService: Preprocessor loaded successfully.")
        else:
            self.preprocessor = TextPreprocessor(max_words=10000, max_len=100)
            print("ModelService WARNING: Tokenizer not found! Running fallback preprocessor.")

        # Models storage
        self.models = {}
        self.distilbert_tokenizer = None
        self.ensemble_weights = {
            "bilstm": 0.2,
            "gru_attention": 0.25,
            "cnn_lstm": 0.15,
            "distilbert": 0.4
        }
        
        # Load TensorFlow models
        self.load_keras_models()
        # Load DistilBERT model
        self.load_distilbert()
        # Load Ensemble weights
        self.load_ensemble_config()
        
        self.initialized = True

    def load_keras_models(self):
        custom_objects = {"AttentionLayer": AttentionLayer}
        
        # BiLSTM
        bilstm_path = os.path.join(self.models_dir, "bilstm", "model.keras")
        if os.path.exists(bilstm_path):
            try:
                self.models["bilstm"] = tf.keras.models.load_model(bilstm_path)
                print("ModelService: BiLSTM model loaded.")
            except Exception as e:
                print(f"ModelService ERROR: Failed to load BiLSTM model: {e}")
                
        # GRU Attention
        gru_path = os.path.join(self.models_dir, "gru_attention", "model.keras")
        if os.path.exists(gru_path):
            try:
                self.models["gru_attention"] = tf.keras.models.load_model(gru_path, custom_objects=custom_objects)
                print("ModelService: GRU Attention model loaded.")
            except Exception as e:
                print(f"ModelService ERROR: Failed to load GRU Attention model: {e}")
                
        # CNN-LSTM
        cnn_lstm_path = os.path.join(self.models_dir, "cnn_lstm", "model.keras")
        if os.path.exists(cnn_lstm_path):
            try:
                self.models["cnn_lstm"] = tf.keras.models.load_model(cnn_lstm_path)
                print("ModelService: CNN-LSTM model loaded.")
            except Exception as e:
                print(f"ModelService ERROR: Failed to load CNN-LSTM model: {e}")

    def load_distilbert(self):
        distilbert_path = os.path.join(self.models_dir, "distilbert")
        if os.path.exists(os.path.join(distilbert_path, "config.json")):
            try:
                self.distilbert_tokenizer = AutoTokenizer.from_pretrained(distilbert_path)
                self.models["distilbert"] = AutoModelForSequenceClassification.from_pretrained(distilbert_path)
                print("ModelService: DistilBERT model loaded from local cache.")
            except Exception as e:
                print(f"ModelService ERROR: Failed to load cached DistilBERT: {e}")
        else:
            print("ModelService: Local DistilBERT cache not found. Will download dynamically on first call or use mock.")

    def load_ensemble_config(self):
        ensemble_config_path = os.path.join(self.models_dir, "ensemble", "config.json")
        if os.path.exists(ensemble_config_path):
            try:
                with open(ensemble_config_path, 'r') as f:
                    config = json.load(f)
                    self.ensemble_weights = config.get("weights", self.ensemble_weights)
                print("ModelService: Ensemble config loaded.")
            except Exception as e:
                print(f"ModelService ERROR: Failed to load Ensemble config: {e}")

    def get_benchmarks(self) -> Dict[str, Any]:
        """
        Loads pre-compiled performance benchmark metrics.
        """
        benchmarks_path = os.path.join(self.models_dir, "benchmarks.json")
        if os.path.exists(benchmarks_path):
            with open(benchmarks_path, 'r') as f:
                return json.load(f)
        return {}

    def predict_keras_model(self, model_key: str, X_padded: np.ndarray) -> np.ndarray:
        """
        Runs prediction for Keras models and returns positive probability.
        """
        model = self.models.get(model_key)
        if model is None:
            # Fallback if model is not trained yet (predict 0.5)
            return np.full((X_padded.shape[0], 1), 0.5)
            
        pred = model.predict(X_padded, verbose=0)
        return pred

    def predict_distilbert(self, texts: List[str]) -> np.ndarray:
        """
        Runs HuggingFace DistilBERT inference using PyTorch.
        Returns array of shape (N, 2) representing [Negative_prob, Positive_prob].
        """
        if "distilbert" not in self.models:
            # On-the-fly downloader if cache didn't hit
            try:
                model_name = "distilbert-base-uncased-finetuned-sst-2-english"
                self.distilbert_tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.models["distilbert"] = AutoModelForSequenceClassification.from_pretrained(model_name)
            except Exception as e:
                print(f"ModelService ERROR: Dynamic DistilBERT load failed: {e}")
                # Mock output if downloading failed
                mock_out = []
                for text in texts:
                    clean = text.lower()
                    pos_words = ["amazing", "good", "great", "love", "awesome", "excellent", "best", "perfect"]
                    score = 0.5 + 0.05 * sum(1 for w in pos_words if w in clean)
                    score = min(0.99, max(0.01, score))
                    mock_out.append([1.0 - score, score])
                return np.array(mock_out)
                
        inputs = self.distilbert_tokenizer(
            texts, 
            return_tensors="pt", 
            truncation=True, 
            padding=True, 
            max_length=self.preprocessor.max_len
        )
        
        with torch.no_grad():
            outputs = self.models["distilbert"](**inputs)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=1).cpu().numpy()
            
        return probs

    def predict(self, text: str, model_name: str = "ensemble") -> Dict[str, Any]:
        """
        Coordinates prediction for single raw review text.
        """
        start_time = time.time()
        
        # Clean & Preprocess
        cleaned = self.preprocessor.clean_text(text)
        seq = self.preprocessor.texts_to_sequences([cleaned])
        X = self.preprocessor.pad_sequences(seq)
        
        sentiment = "Positive"
        confidence = 0.5
        probabilities = {"positive": 0.5, "negative": 0.5}
        
        norm_model_name = model_name.lower().replace("-", "_")
        
        if norm_model_name == "bilstm":
            pred = float(self.predict_keras_model("bilstm", X)[0, 0])
            probabilities = {"positive": pred, "negative": 1.0 - pred}
            
        elif norm_model_name == "gru_attention":
            pred = float(self.predict_keras_model("gru_attention", X)[0, 0])
            probabilities = {"positive": pred, "negative": 1.0 - pred}
            
        elif norm_model_name == "cnn_lstm":
            pred = float(self.predict_keras_model("cnn_lstm", X)[0, 0])
            probabilities = {"positive": pred, "negative": 1.0 - pred}
            
        elif norm_model_name == "distilbert":
            probs = self.predict_distilbert([text])[0]
            probabilities = {"positive": float(probs[1]), "negative": float(probs[0])}
            
        elif norm_model_name == "ensemble":
            # Predict with all active models
            p_bilstm = float(self.predict_keras_model("bilstm", X)[0, 0])
            p_gru = float(self.predict_keras_model("gru_attention", X)[0, 0])
            p_cnn = float(self.predict_keras_model("cnn_lstm", X)[0, 0])
            p_distil = float(self.predict_distilbert([text])[0][1])
            
            # Weighted average
            w = self.ensemble_weights
            p_pos = (
                w["bilstm"] * p_bilstm +
                w["gru_attention"] * p_gru +
                w["cnn_lstm"] * p_cnn +
                w["distilbert"] * p_distil
            )
            
            probabilities = {"positive": p_pos, "negative": 1.0 - p_pos}
            
        # Determine sentiment & final confidence score
        if probabilities["positive"] >= 0.5:
            sentiment = "Positive"
            confidence = probabilities["positive"]
        else:
            sentiment = "Negative"
            confidence = probabilities["negative"]
            
        execution_time_ms = (time.time() - start_time) * 1000
        
        return {
            "text": text,
            "model_name": model_name,
            "sentiment": sentiment,
            "confidence": round(confidence, 4),
            "probabilities": {k: round(v, 4) for k, v in probabilities.items()},
            "execution_time_ms": round(execution_time_ms, 2)
        }

    def predict_batch(self, texts: List[str], model_name: str = "ensemble") -> List[Dict[str, Any]]:
        """
        Optimized prediction helper for processing reviews in bulk.
        """
        results = []
        # Pre-process all Keras inputs
        cleaned_texts = [self.preprocessor.clean_text(t) for t in texts]
        seqs = self.preprocessor.texts_to_sequences(cleaned_texts)
        X = self.preprocessor.pad_sequences(seqs)
        
        norm_model_name = model_name.lower().replace("-", "_")
        
        if norm_model_name == "distilbert":
            # DistilBERT batch prediction
            start_time = time.time()
            probs = self.predict_distilbert(texts)
            latency = (time.time() - start_time) * 1000 / len(texts)
            for i, text in enumerate(texts):
                p_pos = float(probs[i][1])
                sent = "Positive" if p_pos >= 0.5 else "Negative"
                conf = p_pos if p_pos >= 0.5 else (1.0 - p_pos)
                results.append({
                    "text": text,
                    "model_name": model_name,
                    "sentiment": sent,
                    "confidence": round(conf, 4),
                    "probabilities": {"positive": round(p_pos, 4), "negative": round(1.0 - p_pos, 4)},
                    "execution_time_ms": round(latency, 2)
                })
                
        elif norm_model_name in ["bilstm", "gru_attention", "cnn_lstm"]:
            # Keras batch prediction
            start_time = time.time()
            preds = self.predict_keras_model(norm_model_name, X)
            latency = (time.time() - start_time) * 1000 / len(texts)
            for i, text in enumerate(texts):
                p_pos = float(preds[i, 0])
                sent = "Positive" if p_pos >= 0.5 else "Negative"
                conf = p_pos if p_pos >= 0.5 else (1.0 - p_pos)
                results.append({
                    "text": text,
                    "model_name": model_name,
                    "sentiment": sent,
                    "confidence": round(conf, 4),
                    "probabilities": {"positive": round(p_pos, 4), "negative": round(1.0 - p_pos, 4)},
                    "execution_time_ms": round(latency, 2)
                })
                
        else: # Ensemble
            # Get predictions for all models
            start_time = time.time()
            preds_bilstm = self.predict_keras_model("bilstm", X)
            preds_gru = self.predict_keras_model("gru_attention", X)
            preds_cnn = self.predict_keras_model("cnn_lstm", X)
            probs_distil = self.predict_distilbert(texts)
            latency = (time.time() - start_time) * 1000 / len(texts)
            
            w = self.ensemble_weights
            for i, text in enumerate(texts):
                p_pos = (
                    w["bilstm"] * float(preds_bilstm[i, 0]) +
                    w["gru_attention"] * float(preds_gru[i, 0]) +
                    w["cnn_lstm"] * float(preds_cnn[i, 0]) +
                    w["distilbert"] * float(probs_distil[i][1])
                )
                sent = "Positive" if p_pos >= 0.5 else "Negative"
                conf = p_pos if p_pos >= 0.5 else (1.0 - p_pos)
                results.append({
                    "text": text,
                    "model_name": model_name,
                    "sentiment": sent,
                    "confidence": round(conf, 4),
                    "probabilities": {"positive": round(p_pos, 4), "negative": round(1.0 - p_pos, 4)},
                    "execution_time_ms": round(latency, 2)
                })
                
        return results

    def extract_attention_weights(self, text: str) -> List[Dict[str, float]]:
        """
        Extracts sequence attention weights from the GRU Attention model.
        Returns a list of dictionaries mapping {"word": w, "weight": float}.
        """
        gru_model = self.models.get("gru_attention")
        if gru_model is None:
            return []
            
        cleaned = self.preprocessor.clean_text(text)
        words = cleaned.split()
        if not words:
            return []
            
        # Re-create sequence
        seq = self.preprocessor.texts_to_sequences([cleaned])
        X = self.preprocessor.pad_sequences(seq)
        
        # Re-execute GRU layers manually or via Keras sub-models to extract weights
        try:
            # Reconstruct the intermediate layers:
            # Input -> Embedding -> GRU
            inp = gru_model.input
            embedding_layer = gru_model.layers[1]
            gru_layer = gru_model.layers[2]
            attn_layer = gru_model.get_layer("attention_layer")
            
            # Forward pass up to GRU
            x_emb = embedding_layer(inp)
            x_gru = gru_layer(x_emb)
            
            # Calculate alignment weights: e = tanh(x_gru * W)
            # W is from AttentionLayer
            W_att = attn_layer.weights[0]
            e = tf.tanh(tf.matmul(x_gru, W_att))
            a = tf.nn.softmax(e, axis=1) # Shape: (1, seq_len, 1)
            
            # Evaluate using TensorFlow graph execution
            weights = a.numpy()[0, :, 0] # Shape: (seq_len,)
            
            # Map weights to original words
            # The weights align with the first len(words) elements, and the rest is padded (0)
            word_weights = []
            max_words_show = min(len(words), self.preprocessor.max_len)
            
            for i in range(max_words_show):
                word_weights.append({
                    "word": words[i],
                    "weight": float(weights[i])
                })
                
            # Normalize weights to sum to 1.0 for the visible words
            total_visible_weight = sum(item["weight"] for item in word_weights)
            if total_visible_weight > 0:
                for item in word_weights:
                    item["weight"] = round(item["weight"] / total_visible_weight, 4)
                    
            return word_weights
        except Exception as e:
            print(f"ModelService: Failed to extract attention weights ({e}). Returning uniform weights.")
            # Fallback uniform weights
            return [{"word": w, "weight": round(1.0 / len(words), 4)} for w in words]
