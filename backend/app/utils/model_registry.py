import os
import logging
import threading
from typing import Dict, Any, Optional, List, Tuple
import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import Layer
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from backend.app.utils.preprocess import TextPreprocessor

# Setup logger
logger = logging.getLogger("sentiment_platform.model_registry")

# Register custom AttentionLayer for deserializing the GRU model
@tf.keras.utils.register_keras_serializable(package="custom")
class AttentionLayer(Layer):
    def __init__(self, **kwargs):
        super(AttentionLayer, self).__init__(**kwargs)
        
    def build(self, input_shape):
        self.W = self.add_weight(
            name="attention_weight",
            shape=(input_shape[-1], 1),
            initializer="glorot_uniform",
            trainable=True
        )
        super(AttentionLayer, self).build(input_shape)
        
    def call(self, x):
        e = tf.tanh(tf.matmul(x, self.W))
        a = tf.nn.softmax(e, axis=1)
        context = tf.reduce_sum(x * a, axis=1)
        return context, a

    def get_config(self):
        return super(AttentionLayer, self).get_config()


class ModelRegistry:
    """
    Thread-safe Singleton ModelRegistry that loads all active NLP model architectures
    and coordinates inference execution.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(ModelRegistry, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
            
        self._models: Dict[str, Any] = {
            "bilstm": None,
            "gru": None,
            "cnn_lstm": None,
            "distilbert": None
        }
        self._tokenizer = None
        self._ready: bool = False
        self._preprocessor: Optional[TextPreprocessor] = None
        
        self._initialized = True

    @classmethod
    def get_instance(cls) -> "ModelRegistry":
        return cls()

    def is_ready(self) -> bool:
        return self._ready

    def get_model(self, name: str) -> Any:
        return self._models.get(name)

    def load_models(self, model_dir: str):
        """
        Loads deep learning models from the specified model directory.
        Updates self._ready = True if at least DistilBERT is loaded successfully.
        """
        logger.info(f"ModelRegistry: Loading models from directory: {model_dir}")
        
        # 1. Load preprocessor/tokenizer
        tokenizer_path = os.path.join(model_dir, "tokenizer.json")
        if os.path.exists(tokenizer_path):
            try:
                self._preprocessor = TextPreprocessor.load(tokenizer_path)
                logger.info("ModelRegistry: Local TextPreprocessor loaded successfully.")
            except Exception as e:
                logger.error(f"ModelRegistry: Failed to load TextPreprocessor from {tokenizer_path}: {e}")
                self._preprocessor = TextPreprocessor(max_words=10000, max_len=100)
        else:
            logger.warning(f"ModelRegistry: tokenizer.json not found at {tokenizer_path}. Using fallback.")
            self._preprocessor = TextPreprocessor(max_words=10000, max_len=100)

        # 2. Load BiLSTM
        bilstm_path = os.path.join(model_dir, "bilstm", "model.keras")
        if not os.path.exists(bilstm_path):
            bilstm_path = os.path.join(model_dir, "bilstm", "model.h5")
            
        if os.path.exists(bilstm_path):
            try:
                self._models["bilstm"] = tf.keras.models.load_model(bilstm_path)
                logger.info(f"ModelRegistry: BiLSTM model loaded from {bilstm_path}.")
            except Exception as e:
                logger.error(f"ModelRegistry: Failed to load BiLSTM model: {e}")
        else:
            logger.warning(f"ModelRegistry: BiLSTM model file not found.")

        # 3. Load GRU
        gru_path = os.path.join(model_dir, "gru_attention", "model.keras")
        if not os.path.exists(gru_path):
            gru_path = os.path.join(model_dir, "gru_attention", "model.h5")
            
        if os.path.exists(gru_path):
            try:
                custom_objects = {"AttentionLayer": AttentionLayer}
                self._models["gru"] = tf.keras.models.load_model(gru_path, custom_objects=custom_objects)
                logger.info(f"ModelRegistry: GRU model loaded from {gru_path}.")
            except Exception as e:
                logger.error(f"ModelRegistry: Failed to load GRU model: {e}")
        else:
            logger.warning(f"ModelRegistry: GRU model file not found.")

        # 4. Load CNN-LSTM
        cnn_lstm_path = os.path.join(model_dir, "cnn_lstm", "model.keras")
        if not os.path.exists(cnn_lstm_path):
            cnn_lstm_path = os.path.join(model_dir, "cnn_lstm", "model.h5")
            
        if os.path.exists(cnn_lstm_path):
            try:
                self._models["cnn_lstm"] = tf.keras.models.load_model(cnn_lstm_path)
                logger.info(f"ModelRegistry: CNN-LSTM model loaded from {cnn_lstm_path}.")
            except Exception as e:
                logger.error(f"ModelRegistry: Failed to load CNN-LSTM model: {e}")
        else:
            logger.warning(f"ModelRegistry: CNN-LSTM model file not found.")

        # 5. Load DistilBERT
        distilbert_path = os.path.join(model_dir, "distilbert")
        if os.path.exists(os.path.join(distilbert_path, "config.json")):
            try:
                self._tokenizer = AutoTokenizer.from_pretrained(distilbert_path)
                self._models["distilbert"] = AutoModelForSequenceClassification.from_pretrained(distilbert_path)
                logger.info(f"ModelRegistry: DistilBERT model loaded from local cache {distilbert_path}.")
                self._ready = True
            except Exception as e:
                logger.error(f"ModelRegistry: Failed to load local DistilBERT cache: {e}")
        
        # Fallback to online loading if offline failed
        if self._models["distilbert"] is None:
            try:
                model_name = "distilbert-base-uncased-finetuned-sst-2-english"
                logger.info(f"ModelRegistry: Fetching online DistilBERT model: {model_name}...")
                self._tokenizer = AutoTokenizer.from_pretrained(model_name)
                self._models["distilbert"] = AutoModelForSequenceClassification.from_pretrained(model_name)
                logger.info("ModelRegistry: DistilBERT loaded online.")
                self._ready = True
            except Exception as e:
                logger.error(f"ModelRegistry: Online DistilBERT download failed: {e}")
                
        logger.info(f"ModelRegistry load complete. ready={self._ready}")

    def predict_distilbert(self, text: str) -> Dict[str, Any]:
        """
        Runs HuggingFace DistilBERT sequence classification.
        """
        try:
            model = self._models.get("distilbert")
            if model is None or self._tokenizer is None:
                raise ValueError("DistilBERT model not loaded.")
                
            inputs = self._tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=self._preprocessor.max_len if self._preprocessor else 100
            )
            
            with torch.no_grad():
                outputs = model(**inputs)
                logits = outputs.logits
                probs = torch.softmax(logits, dim=1).cpu().numpy()[0]
                
            p_neg, p_pos = float(probs[0]), float(probs[1])
            if p_pos > p_neg:
                sentiment = "positive"
                confidence = p_pos
            elif p_neg > p_pos:
                sentiment = "negative"
                confidence = p_neg
            else:
                sentiment = "neutral"
                confidence = 0.5
                
            return {"sentiment": sentiment, "confidence": round(confidence, 4)}
        except Exception as e:
            logger.error(f"DistilBERT inference error: {e}")
            return {"sentiment": "neutral", "confidence": 0.0, "error": str(e)}

    def _preprocess_text(self, text: str) -> np.ndarray:
        if self._preprocessor is None:
            raise ValueError("TextPreprocessor is not initialized.")
        cleaned = self._preprocessor.clean_text(text)
        seq = self._preprocessor.texts_to_sequences([cleaned])
        X = self._preprocessor.pad_sequences(seq)
        return X

    def predict_bilstm(self, text: str) -> Dict[str, Any]:
        try:
            model = self._models.get("bilstm")
            if model is None:
                raise ValueError("BiLSTM model not loaded.")
                
            X = self._preprocess_text(text)
            pred = float(model.predict(X, verbose=0)[0, 0])
            
            if pred > 0.5:
                sentiment = "positive"
                confidence = pred
            elif pred < 0.5:
                sentiment = "negative"
                confidence = 1.0 - pred
            else:
                sentiment = "neutral"
                confidence = 0.5
                
            return {"sentiment": sentiment, "confidence": round(confidence, 4)}
        except Exception as e:
            logger.error(f"BiLSTM inference error: {e}")
            return {"sentiment": "neutral", "confidence": 0.0, "error": str(e)}

    def predict_gru(self, text: str) -> Dict[str, Any]:
        try:
            model = self._models.get("gru")
            if model is None:
                raise ValueError("GRU model not loaded.")
                
            X = self._preprocess_text(text)
            pred = float(model.predict(X, verbose=0)[0, 0])
            
            if pred > 0.5:
                sentiment = "positive"
                confidence = pred
            elif pred < 0.5:
                sentiment = "negative"
                confidence = 1.0 - pred
            else:
                sentiment = "neutral"
                confidence = 0.5
                
            # Extract Attention weights
            attn_dict = {}
            try:
                # Reconstruct intermediate graph execution
                inp = model.input
                embedding_layer = model.layers[1]
                gru_layer = model.layers[2]
                attn_layer = model.get_layer("attention_layer")
                
                x_emb = embedding_layer(inp)
                x_gru = gru_layer(x_emb)
                
                # Multiply by attention weights
                W_att = attn_layer.weights[0]
                e = tf.tanh(tf.matmul(x_gru, W_att))
                a = tf.nn.softmax(e, axis=1)
                weights = a.numpy()[0, :, 0]
                
                # Map to original cleaned words
                cleaned = self._preprocessor.clean_text(text)
                words = cleaned.split()
                
                if words:
                    max_words = min(len(words), self._preprocessor.max_len)
                    raw_word_weights = []
                    for i in range(max_words):
                        raw_word_weights.append({
                            "word": words[i],
                            "weight": float(weights[i])
                        })
                    # Normalize weights to sum to 1.0 for the visible words
                    total_weight = sum(item["weight"] for item in raw_word_weights)
                    if total_weight > 0:
                        for item in raw_word_weights:
                            attn_dict[item["word"]] = round(item["weight"] / total_weight, 4)
            except Exception as ex:
                logger.error(f"Failed to extract GRU attention weights: {ex}")
                
            return {"sentiment": sentiment, "confidence": round(confidence, 4), "attention_weights": attn_dict}
        except Exception as e:
            logger.error(f"GRU inference error: {e}")
            return {"sentiment": "neutral", "confidence": 0.0, "attention_weights": {}, "error": str(e)}

    def predict_cnn_lstm(self, text: str) -> Dict[str, Any]:
        try:
            model = self._models.get("cnn_lstm")
            if model is None:
                raise ValueError("CNN-LSTM model not loaded.")
                
            X = self._preprocess_text(text)
            pred = float(model.predict(X, verbose=0)[0, 0])
            
            if pred > 0.5:
                sentiment = "positive"
                confidence = pred
            elif pred < 0.5:
                sentiment = "negative"
                confidence = 1.0 - pred
            else:
                sentiment = "neutral"
                confidence = 0.5
                
            return {"sentiment": sentiment, "confidence": round(confidence, 4)}
        except Exception as e:
            logger.error(f"CNN-LSTM inference error: {e}")
            return {"sentiment": "neutral", "confidence": 0.0, "error": str(e)}

    def predict_ensemble(self, text: str) -> Dict[str, Any]:
        try:
            # Model config weights
            weights = {
                "bilstm": 0.2,
                "gru": 0.25,
                "cnn_lstm": 0.15,
                "distilbert": 0.4
            }
            
            # Predict each model
            res_bilstm = self.predict_bilstm(text)
            res_gru = self.predict_gru(text)
            res_cnn = self.predict_cnn_lstm(text)
            res_distilbert = self.predict_distilbert(text)
            
            all_results = {
                "bilstm": res_bilstm,
                "gru": res_gru,
                "cnn_lstm": res_cnn,
                "distilbert": res_distilbert
            }
            
            # Map predictions to positive probabilities
            probs_pos = {}
            for name, res in all_results.items():
                if "error" not in res:
                    if res["sentiment"] == "positive":
                        probs_pos[name] = res["confidence"]
                    elif res["sentiment"] == "negative":
                        probs_pos[name] = 1.0 - res["confidence"]
                    else:
                        probs_pos[name] = 0.5
            
            if not probs_pos:
                raise ValueError("No active models available for Ensemble.")
                
            # Weighted average over available models
            total_active_weight = sum(weights[name] for name in probs_pos)
            ensemble_prob_pos = sum(
                (weights[name] / total_active_weight) * probs_pos[name]
                for name in probs_pos
            )
            
            if ensemble_prob_pos > 0.5:
                sentiment = "positive"
                confidence = ensemble_prob_pos
            elif ensemble_prob_pos < 0.5:
                sentiment = "negative"
                confidence = 1.0 - ensemble_prob_pos
            else:
                sentiment = "neutral"
                confidence = 0.5
                
            # Build individual model scores list
            model_scores = []
            for name, res in all_results.items():
                if "error" not in res:
                    model_scores.append({
                        "model_name": name,
                        "sentiment": res["sentiment"],
                        "confidence": res["confidence"]
                    })
                    
            return {
                "sentiment": sentiment,
                "confidence": round(confidence, 4),
                "model_scores": model_scores
            }
        except Exception as e:
            logger.error(f"Ensemble inference error: {e}")
            return {"sentiment": "neutral", "confidence": 0.0, "model_scores": [], "error": str(e)}
