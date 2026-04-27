# 🍹 Runas Zawadihub – FlavorPrint Loyalty Platform

**Runas Zawadihub** is a modern loyalty & rewards system designed for a non‑alcoholic food & beverage restaurant.  
It goes beyond simple points cards by using **FlavorPrint** – an intelligent pattern‑detection engine that spots repeat purchases and automatically creates personalised offers.

Built as a ready‑to‑pitch MVP, the platform showcases how a POS‑integrated loyalty system can drive repeat business with tier‑based multipliers, category bonuses, and AI‑powered rewards.

---

## ✨ Unique Twist – FlavorPrint™ Pattern Detection

- Tracks each customer’s purchase history.
- Detects frequent single items (≥3 times in 14 days) – e.g., “You love Mango Smoothies – get 50% off!”
- Identifies combo patterns (≥2 times in 30 days) – e.g., “Latte + Croissant combo 30% off!”
- Milestone reward: every 10 transactions → **Free meal of your choice!**
- The detection runs on‑demand when the customer’s dashboard loads.

---

## 🎯 Features Demonstrated

| Feature | Details |
|--------|---------|
| 🏆 Tier Progression | Bronze → Silver → Gold → Platinum (based on total spend) |
| 📊 Interactive Dashboard | Real‑time points, tier progress, recent transactions |
| 💳 Points Calculation | 1 point per $1 × tier multiplier + category bonuses |
| 🤖 Pattern Detection | AI‑powered spending analysis (no external APIs) |
| 🎁 Personalised Rewards | Dynamic offers based on detected patterns |
| 📱 Responsive UI | Works on mobile, tablet, and desktop |
| 🧪 Testing | Pytest suite for pattern detection |

---

## 🛠️ Tech Stack

- **Backend:** Python 3.10, FastAPI, SQLAlchemy, PostgreSQL 14
- **Frontend:** Vanilla HTML, CSS, JavaScript (no frameworks)
- **Authentication:** JWT with bcrypt
- **Infrastructure:** Docker Compose

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose installed on your machine.
- (Optional) Python 3.10+ for local testing without Docker.

### Run the entire app

```bash
git clone https://github.com/tolo017/zawadihub.git
cd runas-zawadihub
sudo docker-compose up --build
