from sqlalchemy.orm import Session
from backend.app.database.models import PredictionLog
from typing import List, Dict, Any
import datetime
import random
from collections import Counter
import re

class DatabaseService:
    """
    Handles logging predictions, generating dashboard analytics, and querying error analysis logs.
    """

    @staticmethod
    def log_prediction(
        db: Session,
        text: str,
        model_name: str,
        sentiment: str,
        confidence: float,
        probabilities: Dict[str, float],
        execution_time_ms: float,
        true_label: str = None
    ) -> PredictionLog:
        db_log = PredictionLog(
            text=text,
            model_name=model_name,
            sentiment=sentiment,
            confidence=confidence,
            probabilities=probabilities,
            true_label=true_label,
            execution_time_ms=execution_time_ms
        )
        db.add(db_log)
        db.commit()
        db.refresh(db_log)
        return db_log

    @staticmethod
    def log_bulk_predictions(
        db: Session,
        logs_data: List[Dict[str, Any]]
    ):
        db_logs = [
            PredictionLog(
                text=item["text"],
                model_name=item["model_name"],
                sentiment=item["sentiment"],
                confidence=item["confidence"],
                probabilities=item["probabilities"],
                true_label=item.get("true_label"),
                execution_time_ms=item["execution_time_ms"]
            )
            for item in logs_data
        ]
        db.bulk_save_objects(db_logs)
        db.commit()

    @staticmethod
    def get_logs(db: Session, limit: int = 100) -> List[PredictionLog]:
        return db.query(PredictionLog).order_by(PredictionLog.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_analytics(db: Session) -> Dict[str, Any]:
        """
        Calculates advanced business intelligence aggregates from historical predictions.
        """
        logs = db.query(PredictionLog).all()
        total_count = len(logs)
        
        if total_count == 0:
            return {
                "total_count": 0,
                "positive_percentage": 0.0,
                "negative_percentage": 0.0,
                "sentiment_distribution": {"Positive": 0, "Negative": 0},
                "confidence_distribution": {
                    "0.5-0.6": 0, "0.6-0.7": 0, "0.7-0.8": 0, "0.8-0.9": 0, "0.9-1.0": 0
                },
                "sentiment_trends": [],
                "top_positive_words": [],
                "top_negative_words": [],
                "model_average_latencies": {}
            }

        pos_count = sum(1 for log in logs if log.sentiment == "Positive")
        neg_count = total_count - pos_count

        # Confidence Distribution
        conf_bins = {"0.5-0.6": 0, "0.6-0.7": 0, "0.7-0.8": 0, "0.8-0.9": 0, "0.9-1.0": 0}
        for log in logs:
            conf = log.confidence
            if 0.5 <= conf < 0.6:
                conf_bins["0.5-0.6"] += 1
            elif 0.6 <= conf < 0.7:
                conf_bins["0.6-0.7"] += 1
            elif 0.7 <= conf < 0.8:
                conf_bins["0.7-0.8"] += 1
            elif 0.8 <= conf < 0.9:
                conf_bins["0.8-0.9"] += 1
            elif 0.9 <= conf <= 1.0:
                conf_bins["0.9-1.0"] += 1

        # Sentiment Trends (Grouped by date)
        trends = {}
        for log in logs:
            date_str = log.created_at.strftime("%Y-%m-%d")
            if date_str not in trends:
                trends[date_str] = {"Positive": 0, "Negative": 0}
            trends[date_str][log.sentiment] += 1
            
        trend_list = [
            {"date": k, "Positive": v["Positive"], "Negative": v["Negative"]}
            for k, v in sorted(trends.items())
        ]

        # Word Frequencies (Word Cloud helpers)
        pos_words = []
        neg_words = []
        stop_words = {"this", "is", "a", "the", "and", "i", "it", "was", "to", "for", "in", "of", "with", "but", "not", "my", "on", "that", "so", "have", "you"}
        
        for log in logs:
            words = [w.lower() for w in re.findall(r'\w+', log.text) if len(w) > 2]
            words = [w for w in words if w not in stop_words]
            if log.sentiment == "Positive":
                pos_words.extend(words)
            else:
                neg_words.extend(words)
                
        top_pos = [{"word": w, "count": c} for w, c in Counter(pos_words).most_common(15)]
        top_neg = [{"word": w, "count": c} for w, c in Counter(neg_words).most_common(15)]

        # Model average latency
        model_latencies = {}
        model_counts = {}
        for log in logs:
            model_latencies[log.model_name] = model_latencies.get(log.model_name, 0) + log.execution_time_ms
            model_counts[log.model_name] = model_counts.get(log.model_name, 0) + 1

        avg_latencies = {
            m: round(model_latencies[m] / model_counts[m], 2) for m in model_latencies
        }

        return {
            "total_count": total_count,
            "positive_percentage": round((pos_count / total_count) * 100, 2),
            "negative_percentage": round((neg_count / total_count) * 100, 2),
            "sentiment_distribution": {"Positive": pos_count, "Negative": neg_count},
            "confidence_distribution": conf_bins,
            "sentiment_trends": trend_list,
            "top_positive_words": top_pos,
            "top_negative_words": top_neg,
            "model_average_latencies": avg_latencies
        }

    @staticmethod
    def get_error_analysis(db: Session) -> Dict[str, Any]:
        """
        Pulls logs where the user specified a true label to verify accuracy, false positives, and false negatives.
        """
        labeled_logs = db.query(PredictionLog).filter(PredictionLog.true_label.isnot(None)).all()
        
        if not labeled_logs:
            return {
                "total_labeled": 0,
                "accuracy": 0.0,
                "false_positives": [],
                "false_negatives": [],
                "metrics": {"TP": 0, "FP": 0, "TN": 0, "FN": 0}
            }
            
        tp = fp = tn = fn = 0
        false_pos = []
        false_neg = []
        
        for log in labeled_logs:
            pred = log.sentiment
            true = log.true_label
            
            if pred == "Positive" and true == "Positive":
                tp += 1
            elif pred == "Positive" and true == "Negative":
                fp += 1
                false_pos.append(log.to_dict())
            elif pred == "Negative" and true == "Negative":
                tn += 1
            elif pred == "Negative" and true == "Positive":
                fn += 1
                false_neg.append(log.to_dict())
                
        total_labeled = len(labeled_logs)
        accuracy = (tp + tn) / total_labeled if total_labeled > 0 else 0.0
        
        return {
            "total_labeled": total_labeled,
            "accuracy": round(accuracy * 100, 2),
            "false_positives": false_pos,
            "false_negatives": false_neg,
            "metrics": {"TP": tp, "FP": fp, "TN": tn, "FN": fn}
        }

    @staticmethod
    def seed_data(db: Session):
        """
        Seeds the database with high-quality, simulated analytics log history.
        """
        if db.query(PredictionLog).count() > 0:
            return # Already seeded
            
        logger.info("Seeding database with simulated prediction logs...")
        
        positive_phrases = [
            "This product is amazing and saves me hours of work.",
            "I love the design! Sleek, modern and extremely responsive.",
            "The customer service was excellent. They went above and beyond.",
            "Highly recommend this app. Truly premium quality.",
            "Absolutely beautiful interface and very fast execution.",
            "The best sentiment analyzer I have used so far.",
            "Really impressive speed and accuracy. Five stars!",
            "Great tool for business intelligence, very helpful dashboards."
        ]
        
        negative_phrases = [
            "Terrible app, crashes constantly on startup.",
            "Waste of money and time. Extremely slow response.",
            "The UI is bloated, buggy, and confusing to navigate.",
            "Do not buy! Terrible customer support, very rude.",
            "Laggy, poorly designed and completely useless.",
            "Very disappointed. The tool lacks core features.",
            "Not worth the price. Performance is frustratingly bad.",
            "Extremely buggy, it failed to parse my CSV files."
        ]
        
        models = ["BiLSTM", "GRU Attention", "CNN-LSTM", "DistilBERT", "Ensemble"]
        
        # Create records spanning the last 7 days
        start_date = datetime.datetime.utcnow() - datetime.timedelta(days=7)
        
        logs_to_seed = []
        for i in range(120):
            day_offset = random.randint(0, 7)
            hour_offset = random.randint(0, 23)
            minute_offset = random.randint(0, 59)
            
            created_at = start_date + datetime.timedelta(days=day_offset, hours=hour_offset, minutes=minute_offset)
            
            is_positive = random.random() < 0.65 # 65% positive
            text = random.choice(positive_phrases) if is_positive else random.choice(negative_phrases)
            sentiment = "Positive" if is_positive else "Negative"
            
            # Simulated high-quality confidence
            confidence = random.uniform(0.78, 0.99)
            prob_pos = confidence if is_positive else (1.0 - confidence)
            
            model = random.choice(models)
            latency = random.uniform(5.0, 30.0) if model != "DistilBERT" else random.uniform(35.0, 60.0)
            if model == "Ensemble":
                latency = random.uniform(70.0, 95.0)
                
            # Add some misclassified rows for Error Analysis page demo
            true_label = sentiment
            if random.random() < 0.12: # 12% error rate in simulation
                true_label = "Negative" if sentiment == "Positive" else "Positive"
                
            db_log = PredictionLog(
                text=text,
                model_name=model,
                sentiment=sentiment,
                confidence=confidence,
                probabilities={"positive": round(prob_pos, 4), "negative": round(1.0 - prob_pos, 4)},
                true_label=true_label,
                execution_time_ms=round(latency, 2),
                created_at=created_at
            )
            logs_to_seed.append(db_log)
            
        db.bulk_save_objects(logs_to_seed)
        db.commit()
        logger.info(f"Successfully seeded {len(logs_to_seed)} analytics prediction logs.")
