from datetime import datetime, timedelta
from typing import List, Dict, Optional
import random
from enum import Enum

class RewardType(Enum):
    DISCOUNT = "discount"
    FREE_ITEM = "free_item"
    EARLY_ACCESS = "early_access"
    BIRTHDAY_GIFT = "birthday_gift"
    ANNIVERSARY = "anniversary"
    LOYALTY_BONUS = "loyalty_bonus"
    SEASONAL = "seasonal"
    REFERRAL = "referral"

class RewardsEngine:
    def __init__(self):
        self.reward_templates = self._initialize_templates()
    
    def generate_personalized_rewards(
        self, 
        customer_data: Dict,
        transaction_history: List[Dict],
        pattern_insights: Dict
    ) -> List[Dict]:
        """Generate personalized rewards based on customer behavior"""
        rewards = []
        
        # Base on customer tier
        rewards.extend(self._get_tier_based_rewards(customer_data))
        
        # Based on spending patterns
        rewards.extend(self._get_pattern_based_rewards(pattern_insights))
        
        # Special occasions
        rewards.extend(self._get_occasion_rewards(customer_data))
        
        # Random surprise reward (for engagement)
        if random.random() < 0.3:  # 30% chance
            rewards.append(self._generate_surprise_reward(customer_data))
        
        # Filter and prioritize
        filtered_rewards = self._filter_rewards(rewards, customer_data)
        prioritized_rewards = self._prioritize_rewards(filtered_rewards, customer_data)
        
        return prioritized_rewards[:5]  # Return top 5 rewards
    
    def calculate_points(self, amount: float, customer_tier: str, 
                        category: Optional[str] = None) -> int:
        """Calculate points earned from a transaction"""
        base_multiplier = 1
        
        # Tier multipliers
        tier_multipliers = {
            "bronze": 1.0,
            "silver": 1.2,
            "gold": 1.5,
            "platinum": 2.0
        }
        
        # Category multipliers (incentivize certain categories)
        category_multipliers = {
            "electronics": 1.5,
            "fashion": 1.2,
            "groceries": 1.0,
            "home": 1.3,
            "entertainment": 1.1
        }
        
        multiplier = base_multiplier * tier_multipliers.get(customer_tier, 1.0)
        if category:
            multiplier *= category_multipliers.get(category, 1.0)
        
        # 1 point per dollar, multiplied by tier and category
        points = int(amount * multiplier)
        
        # Round up to nearest 10 for cleaner numbers
        points = ((points + 9) // 10) * 10
        
        return max(10, points)  # Minimum 10 points
    
    def _initialize_templates(self) -> Dict:
        return {
            RewardType.DISCOUNT: {
                "base_points": 1000,
                "description_template": "{percentage}% off your next purchase",
                "variations": [
                    {"percentage": 10, "points": 1000},
                    {"percentage": 20, "points": 2000},
                    {"percentage": 30, "points": 3500},
                    {"percentage": 50, "points": 6000}
                ]
            },
            RewardType.FREE_ITEM: {
                "base_points": 1500,
                "description_template": "Free {item} with your next purchase",
                "variations": [
                    {"item": "coffee", "points": 500},
                    {"item": "dessert", "points": 1000},
                    {"item": "premium item", "points": 2500}
                ]
            },
            RewardType.EARLY_ACCESS: {
                "base_points": 2000,
                "description_template": "Early access to {product}",
                "variations": [
                    {"product": "new collection", "points": 2000},
                    {"product": "sale items", "points": 1500},
                    {"product": "exclusive products", "points": 3000}
                ]
            },
            RewardType.BIRTHDAY_GIFT: {
                "base_points": 500,
                "description_template": "Birthday surprise! {gift}",
                "variations": [
                    {"gift": "Special birthday treat", "points": 500},
                    {"gift": "Birthday discount bundle", "points": 1000}
                ]
            }
        }
    
    def _get_tier_based_rewards(self, customer_data: Dict) -> List[Dict]:
        rewards = []
        tier = customer_data.get("customer_tier", "bronze")
        points = customer_data.get("active_points", 0)
        
        if tier == "silver" and points >= 500:
            rewards.append({
                "type": "tier_reward",
                "name": "Silver Member Bonus",
                "description": "Exclusive 15% discount for Silver members",
                "points_required": 500,
                "discount_percentage": 15,
                "expiry_days": 30
            })
        
        if tier == "gold" and points >= 1500:
            rewards.append({
                "type": "tier_reward",
                "name": "Gold Member VIP Access",
                "description": "VIP early access to sales and new arrivals",
                "points_required": 1500,
                "expiry_days": 45
            })
        
        if tier == "platinum" and points >= 3000:
            rewards.append({
                "type": "tier_reward",
                "name": "Platinum Concierge",
                "description": "Personal shopping assistant for your next visit",
                "points_required": 3000,
                "expiry_days": 60
            })
        
        return rewards
    
    def _get_pattern_based_rewards(self, pattern_insights: Dict) -> List[Dict]:
        rewards = []
        
        patterns = pattern_insights.get("patterns", {})
        
        # Reward frequent shoppers
        transaction_count = patterns.get("transaction_count", 0)
        if transaction_count > 10:
            rewards.append({
                "type": "frequency_reward",
                "name": "Frequent Shopper Bonus",
                "description": "Thank you for being a loyal customer!",
                "points_bonus": 200,
                "expiry_days": 14
            })
        
        # Reward consistent spending
        spend_std = patterns.get("spend_std", 0)
        avg_spend = patterns.get("average_spend", 0)
        if spend_std > 0 and avg_spend > 0 and spend_std / avg_spend < 0.5:
            rewards.append({
                "type": "consistency_reward",
                "name": "Consistent Spender",
                "description": "Reward for your consistent shopping pattern",
                "discount_percentage": 10,
                "expiry_days": 21
            })
        
        # Category-specific rewards
        category_dist = patterns.get("category_distribution", {})
        if category_dist:
            top_category = max(category_dist.items(), key=lambda x: x[1])[0]
            rewards.append({
                "type": "category_reward",
                "name": f"Your Favorite: {top_category.title()}",
                "description": f"Extra points on your next {top_category} purchase",
                "points_multiplier": 1.5,
                "category": top_category,
                "expiry_days": 30
            })
        
        return rewards
    
    def _get_occasion_rewards(self, customer_data: Dict) -> List[Dict]:
        rewards = []
        today = datetime.utcnow()
        
        # Check birthday
        dob = customer_data.get("date_of_birth")
        if dob:
            if isinstance(dob, str):
                birth_date = datetime.fromisoformat(dob.replace('Z', '+00:00'))
            else:
                birth_date = dob
            
            if (birth_date.month == today.month and 
                abs(birth_date.day - today.day) <= 7):
                rewards.append({
                    "type": "birthday",
                    "name": "Happy Birthday!",
                    "description": "Special birthday gift for you",
                    "points_bonus": 500,
                    "free_item": "Birthday Surprise",
                    "expiry_days": 14
                })
        
        # Check join anniversary
        join_date = customer_data.get("join_date")
        if join_date:
            if isinstance(join_date, str):
                join_dt = datetime.fromisoformat(join_date.replace('Z', '+00:00'))
            else:
                join_dt = join_date
            
            years_joined = today.year - join_dt.year
            if (join_dt.month == today.month and 
                abs(join_dt.day - today.day) <= 7 and 
                years_joined > 0):
                rewards.append({
                    "type": "anniversary",
                    "name": f"{years_joined} Year Anniversary",
                    "description": f"Thank you for {years_joined} year{'s' if years_joined > 1 else ''} of loyalty!",
                    "points_bonus": years_joined * 100,
                    "discount_percentage": min(25, years_joined * 5),
                    "expiry_days": 30
                })
        
        return rewards
    
    def _generate_surprise_reward(self, customer_data: Dict) -> Dict:
        surprise_types = [
            {
                "name": "Mystery Bonus",
                "description": "A surprise reward just for you!",
                "points_bonus": random.randint(50, 200),
                "type": "surprise"
            },
            {
                "name": "Flash Reward",
                "description": "Limited time special offer",
                "discount_percentage": random.choice([5, 10, 15]),
                "type": "flash"
            },
            {
                "name": "Loyalty Token",
                "description": "Exchange for a special treat",
                "free_item": "Loyalty Token",
                "type": "token"
            }
        ]
        
        reward = random.choice(surprise_types)
        reward["expiry_days"] = random.randint(3, 7)  # Short expiry for urgency
        return reward
    
    def _filter_rewards(self, rewards: List[Dict], customer_data: Dict) -> List[Dict]:
        """Filter out inappropriate or duplicate rewards"""
        filtered = []
        seen_types = set()
        
        for reward in rewards:
            reward_type = reward.get("type")
            
            # Skip if we've already seen this type (unless it's tier-based)
            if reward_type in seen_types and reward_type != "tier_reward":
                continue
            
            # Check if customer has enough points for point-based rewards
            if "points_required" in reward:
                if customer_data.get("active_points", 0) < reward["points_required"]:
                    continue
            
            filtered.append(reward)
            seen_types.add(reward_type)
        
        return filtered
    
    def _prioritize_rewards(self, rewards: List[Dict], customer_data: Dict) -> List[Dict]:
        """Prioritize rewards based on relevance and value"""
        
        def reward_score(reward: Dict) -> float:
            score = 0
            
            # Type weights
            type_weights = {
                "birthday": 2.0,
                "anniversary": 1.8,
                "tier_reward": 1.5,
                "category_reward": 1.3,
                "frequency_reward": 1.2,
                "consistency_reward": 1.1,
                "surprise": 1.0,
                "flash": 0.9
            }
            
            score += type_weights.get(reward.get("type", ""), 0.5)
            
            # Value-based scoring
            if "points_bonus" in reward:
                score += reward["points_bonus"] / 1000
            
            if "discount_percentage" in reward:
                score += reward["discount_percentage"] / 50
            
            # Shorter expiry gets higher priority (creates urgency)
            if "expiry_days" in reward:
                score += (30 - reward["expiry_days"]) / 30
            
            return score
        
        return sorted(rewards, key=reward_score, reverse=True)