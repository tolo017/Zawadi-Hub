import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import defaultdict
import json
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import logging

logger = logging.getLogger(__name__)

class PatternDetection:
    def __init__(self):
        self.scaler = StandardScaler()
        
    def detect_spending_patterns(self, transactions: List[Dict]) -> Dict:
        """Detect spending patterns from transaction history"""
        if not transactions:
            return {"patterns": [], "segments": []}
        
        # Extract features
        amounts = [t.get("amount", 0) for t in transactions]
        categories = [t.get("category", "unknown") for t in transactions]
        timestamps = [t.get("transaction_date") for t in transactions]
        
        patterns = {
            "average_spend": np.mean(amounts) if amounts else 0,
            "spend_std": np.std(amounts) if len(amounts) > 1 else 0,
            "total_spend": sum(amounts),
            "transaction_count": len(transactions),
            "category_distribution": self._get_category_distribution(categories),
            "temporal_patterns": self._analyze_temporal_patterns(timestamps, amounts),
            "basket_analysis": self._analyze_basket_patterns(transactions)
        }
        
        # Detect anomalies
        patterns["spending_anomalies"] = self._detect_anomalies(amounts)
        
        return patterns
    
    def segment_customers(self, customers_data: List[Dict]) -> Dict:
        """Segment customers using K-means clustering"""
        if len(customers_data) < 5:
            return {"segments": [], "labels": []}
        
        # Prepare features
        features = []
        for customer in customers_data:
            features.append([
                customer.get("total_points", 0),
                customer.get("lifetime_value", 0),
                customer.get("transaction_count", 0),
                customer.get("avg_transaction_value", 0)
            ])
        
        features = np.array(features)
        
        # Scale features
        features_scaled = self.scaler.fit_transform(features)
        
        # Apply K-means (optimal k determined by elbow method simplified)
        k = min(4, len(customers_data))
        kmeans = KMeans(n_clusters=k, random_state=42)
        labels = kmeans.fit_predict(features_scaled)
        
        # Analyze segments
        segments = []
        for i in range(k):
            segment_indices = np.where(labels == i)[0]
            segment_data = features[segment_indices]
            
            segment = {
                "segment_id": i,
                "size": len(segment_indices),
                "avg_points": float(np.mean(segment_data[:, 0])),
                "avg_lifetime_value": float(np.mean(segment_data[:, 1])),
                "characteristics": self._describe_segment(segment_data),
                "recommended_rewards": self._suggest_rewards_for_segment(segment_data)
            }
            segments.append(segment)
        
        return {
            "segments": segments,
            "labels": labels.tolist(),
            "centroids": kmeans.cluster_centers_.tolist()
        }
    
    def predict_next_purchase(self, transaction_history: List[Dict]) -> Dict:
        """Predict next purchase timing and category"""
        if len(transaction_history) < 3:
            return {"prediction": "insufficient_data", "confidence": 0}
        
        timestamps = [t.get("transaction_date") for t in transaction_history]
        if not all(timestamps):
            return {"prediction": "invalid_data", "confidence": 0}
        
        # Calculate time between purchases
        time_diffs = []
        for i in range(1, len(timestamps)):
            if isinstance(timestamps[i], str):
                dt1 = datetime.fromisoformat(timestamps[i-1].replace('Z', '+00:00'))
                dt2 = datetime.fromisoformat(timestamps[i].replace('Z', '+00:00'))
            else:
                dt1 = timestamps[i-1]
                dt2 = timestamps[i]
            time_diffs.append((dt2 - dt1).total_seconds() / 86400)  # in days
        
        if not time_diffs:
            return {"prediction": "insufficient_data", "confidence": 0}
        
        avg_interval = np.mean(time_diffs)
        std_interval = np.std(time_diffs) if len(time_diffs) > 1 else 0
        
        # Predict next purchase date
        last_transaction = timestamps[-1]
        if isinstance(last_transaction, str):
            last_dt = datetime.fromisoformat(last_transaction.replace('Z', '+00:00'))
        else:
            last_dt = last_transaction
        
        predicted_date = last_dt + timedelta(days=avg_interval)
        
        # Predict category based on history
        categories = [t.get("category", "unknown") for t in transaction_history]
        predicted_category = max(set(categories), key=categories.count)
        
        confidence = min(0.9, 1 - (std_interval / avg_interval if avg_interval > 0 else 1))
        
        return {
            "predicted_date": predicted_date.isoformat(),
            "predicted_category": predicted_category,
            "confidence": float(confidence),
            "expected_interval_days": float(avg_interval)
        }
    
    def _get_category_distribution(self, categories: List[str]) -> Dict:
        distribution = {}
        for category in categories:
            distribution[category] = distribution.get(category, 0) + 1
        
        # Normalize
        total = sum(distribution.values())
        if total > 0:
            return {k: v/total for k, v in distribution.items()}
        return distribution
    
    def _analyze_temporal_patterns(self, timestamps: List, amounts: List) -> Dict:
        patterns = {
            "weekly_pattern": defaultdict(list),
            "hourly_pattern": defaultdict(list),
            "monthly_trend": []
        }
        
        for ts, amount in zip(timestamps, amounts):
            if not ts:
                continue
            
            if isinstance(ts, str):
                dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
            else:
                dt = ts
            
            # Day of week (0=Monday, 6=Sunday)
            patterns["weekly_pattern"][dt.weekday()].append(amount)
            
            # Hour of day
            patterns["hourly_pattern"][dt.hour].append(amount)
            
            # Monthly trend
            month_key = f"{dt.year}-{dt.month:02d}"
            patterns["monthly_trend"].append({
                "month": month_key,
                "amount": amount,
                "date": dt.isoformat()
            })
        
        # Calculate averages
        for day in patterns["weekly_pattern"]:
            amounts = patterns["weekly_pattern"][day]
            patterns["weekly_pattern"][day] = {
                "avg": np.mean(amounts) if amounts else 0,
                "count": len(amounts)
            }
        
        for hour in patterns["hourly_pattern"]:
            amounts = patterns["hourly_pattern"][hour]
            patterns["hourly_pattern"][hour] = {
                "avg": np.mean(amounts) if amounts else 0,
                "count": len(amounts)
            }
        
        return patterns
    
    def _analyze_basket_patterns(self, transactions: List[Dict]) -> Dict:
        """Analyze frequently bought together items"""
        item_pairs = defaultdict(int)
        
        for transaction in transactions:
            items = transaction.get("items", [])
            if isinstance(items, str):
                try:
                    items = json.loads(items)
                except:
                    items = []
            
            if isinstance(items, list) and len(items) > 1:
                # Count item pairs
                for i in range(len(items)):
                    for j in range(i+1, len(items)):
                        pair = tuple(sorted([items[i], items[j]]))
                        item_pairs[pair] += 1
        
        # Get top pairs
        sorted_pairs = sorted(item_pairs.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "frequent_pairs": [
                {"items": list(pair), "count": count}
                for pair, count in sorted_pairs
            ],
            "total_pairs": len(item_pairs)
        }
    
    def _detect_anomalies(self, amounts: List[float], threshold: float = 2.0) -> List[Dict]:
        """Detect anomalous spending using z-score"""
        if len(amounts) < 5:
            return []
        
        amounts_array = np.array(amounts)
        mean = np.mean(amounts_array)
        std = np.std(amounts_array)
        
        if std == 0:
            return []
        
        z_scores = np.abs((amounts_array - mean) / std)
        anomalies = np.where(z_scores > threshold)[0]
        
        return [
            {
                "index": int(idx),
                "amount": float(amounts_array[idx]),
                "z_score": float(z_scores[idx]),
                "is_high": amounts_array[idx] > mean
            }
            for idx in anomalies
        ]
    
    def _describe_segment(self, segment_data: np.ndarray) -> List[str]:
        """Generate descriptive labels for customer segment"""
        characteristics = []
        
        avg_points = segment_data[:, 0].mean()
        avg_value = segment_data[:, 1].mean()
        avg_transactions = segment_data[:, 2].mean()
        avg_transaction_value = segment_data[:, 3].mean()
        
        if avg_points > 10000:
            characteristics.append("high_points")
        elif avg_points < 1000:
            characteristics.append("low_points")
        
        if avg_value > 5000:
            characteristics.append("high_value")
        elif avg_value < 500:
            characteristics.append("low_value")
        
        if avg_transactions > 50:
            characteristics.append("frequent_shopper")
        elif avg_transactions < 10:
            characteristics.append("infrequent_shopper")
        
        if avg_transaction_value > 200:
            characteristics.append("big_spender")
        elif avg_transaction_value < 50:
            characteristics.append("small_spender")
        
        return characteristics
    
    def _suggest_rewards_for_segment(self, segment_data: np.ndarray) -> List[Dict]:
        """Suggest rewards based on segment characteristics"""
        suggestions = []
        
        avg_points = segment_data[:, 0].mean()
        avg_value = segment_data[:, 1].mean()
        
        if avg_points > 10000:
            suggestions.append({
                "type": "premium",
                "description": "Exclusive VIP rewards",
                "points_range": "10000+"
            })
        
        if avg_value > 5000:
            suggestions.append({
                "type": "loyalty_bonus",
                "description": "High-value customer bonus",
                "points_range": "5000-10000"
            })
        
        if len(segment_data) > 0 and segment_data[:, 2].mean() > 20:
            suggestions.append({
                "type": "frequency_bonus",
                "description": "Frequent shopper reward",
                "points_range": "2000-5000"
            })
        
        # Always include some basic suggestions
        if not suggestions:
            suggestions.extend([
                {
                    "type": "welcome",
                    "description": "Welcome bonus for new engagement",
                    "points_range": "500-1000"
                },
                {
                    "type": "seasonal",
                    "description": "Seasonal special offer",
                    "points_range": "1000-2000"
                }
            ])
        
        return suggestions