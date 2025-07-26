#!/usr/bin/env python3
"""
Demo data seeding script for Namma Krushi application.
Creates sample farmer data for testing and demonstration purposes.
"""

from datetime import datetime, date, timedelta
from decimal import Decimal
import random

from sqlalchemy.orm import Session
from passlib.context import CryptContext

from src.app.config.database import SessionLocal, engine, Base, create_tables
from src.app.models.user import User
from src.app.models.crop import Crop
from src.app.models.daily_log import DailyLog
from src.app.models.todo import TodoTask
from src.app.models.sale import Sale
from src.app.models.chat import ChatHistory
from src.app.models.weather import WeatherHistory

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Sample data for Karnataka farmers
SAMPLE_FARMERS = [
    {
        "name": "Ravi Kumar",
        "email": "ravi.kumar@example.com",
        "phone": "+91-9876543210",
        "location": "Mysore Rural",
        "district": "Mysore",
        "latitude": 12.2958,
        "longitude": 76.6394,
    },
    {
        "name": "Lakshmi Devi",
        "email": "lakshmi.devi@example.com",
        "phone": "+91-9876543211",
        "location": "Mandya",
        "district": "Mandya",
        "latitude": 12.5218,
        "longitude": 76.8951,
    },
    {
        "name": "Suresh Gowda",
        "email": "suresh.gowda@example.com",
        "phone": "+91-9876543212",
        "location": "Hassan",
        "district": "Hassan",
        "latitude": 13.0072,
        "longitude": 76.1004,
    },
    {
        "name": "Manjula Reddy",
        "email": "manjula.reddy@example.com",
        "phone": "+91-9876543213",
        "location": "Kolar",
        "district": "Kolar",
        "latitude": 13.1373,
        "longitude": 78.1294,
    },
    {
        "name": "Krishnamurthy",
        "email": "krishnamurthy@example.com",
        "phone": "+91-9876543214",
        "location": "Tumkur",
        "district": "Tumkur",
        "latitude": 13.3379,
        "longitude": 77.1022,
    },
]

SAMPLE_FARMS = [
    {
        "crop_name": "Green Valley Farm",
        "total_area_acres": 5.5,
        "cultivable_area_acres": 5.0,
        "soil_type": "Red Soil",
        "water_source": "Borewell",
        "irrigation_type": "Drip Irrigation",
        "current_crop": "Tomato",
        "crop_variety": "Arka Rakshak",
        "crop_stage": "flowering",
        "crop_health_score": 85.0,
        "previous_crops": ["Rice", "Sugarcane", "Maize"],
        "average_yield": 12.5,
    },
    {
        "crop_name": "Sunrise Organic Farm",
        "total_area_acres": 3.2,
        "cultivable_area_acres": 3.0,
        "soil_type": "Black Soil",
        "water_source": "Canal",
        "irrigation_type": "Flood Irrigation",
        "current_crop": "Rice",
        "crop_variety": "BPT 5204",
        "crop_stage": "vegetative",
        "crop_health_score": 92.0,
        "previous_crops": ["Ragi", "Groundnut"],
        "average_yield": 8.2,
    },
    {
        "crop_name": "Coconut Grove",
        "total_area_acres": 8.0,
        "cultivable_area_acres": 7.5,
        "soil_type": "Laterite Soil",
        "water_source": "Rainwater + Borewell",
        "irrigation_type": "Sprinkler",
        "current_crop": "Coconut",
        "crop_variety": "Malayan Dwarf",
        "crop_stage": "fruiting",
        "crop_health_score": 78.0,
        "previous_crops": ["Arecanut", "Pepper"],
        "average_yield": 15000,  # nuts per year
    },
    {
        "crop_name": "Mango Orchard",
        "total_area_acres": 6.8,
        "cultivable_area_acres": 6.5,
        "soil_type": "Red Sandy Soil",
        "water_source": "Tank",
        "irrigation_type": "Drip Irrigation",
        "current_crop": "Mango",
        "crop_variety": "Alphonso",
        "crop_stage": "fruiting",
        "crop_health_score": 88.0,
        "previous_crops": ["Cashew", "Jackfruit"],
        "average_yield": 25.0,
    },
    {
        "crop_name": "Spice Garden",
        "total_area_acres": 4.2,
        "cultivable_area_acres": 4.0,
        "soil_type": "Loamy Soil",
        "water_source": "Well",
        "irrigation_type": "Manual",
        "current_crop": "Cardamom",
        "crop_variety": "Malabar",
        "crop_stage": "harvesting",
        "crop_health_score": 95.0,
        "previous_crops": ["Coffee", "Pepper", "Ginger"],
        "average_yield": 2.8,
    },
]

SAMPLE_ACTIVITIES = [
    "Watered the crops",
    "Applied organic fertilizer",
    "Checked for pest infestation",
    "Harvested vegetables",
    "Planted new seedlings",
    "Pruned fruit trees",
    "Weeded the field",
    "Sprayed pesticide",
    "Irrigated the field",
    "Collected eggs from poultry",
]

SAMPLE_CHAT_MESSAGES = [
    {
        "user_message": "ನನ್ನ ಟೊಮೇಟೊ ಗಿಡಗಳಲ್ಲಿ ಹಳದಿ ಎಲೆಗಳು ಕಾಣಿಸುತ್ತಿವೆ. ಏನು ಮಾಡಬೇಕು?",
        "ai_response": "ಟೊಮೇಟೊ ಗಿಡಗಳಲ್ಲಿ ಹಳದಿ ಎಲೆಗಳು ಸಾಮಾನ್ಯವಾಗಿ ನೀರಿನ ಕೊರತೆ ಅಥವಾ ಪೋಷಕಾಂಶಗಳ ಕೊರತೆಯಿಂದ ಆಗುತ್ತದೆ. ನಿಯಮಿತವಾಗಿ ನೀರು ಕೊಡಿ ಮತ್ತು ಸಾವಯವ ಗೊಬ್ಬರ ಹಾಕಿ.",
    },
    {
        "user_message": "What is the best time to plant rice in Karnataka?",
        "ai_response": "In Karnataka, the best time to plant rice is during the Kharif season (June-July) with the onset of monsoon. For irrigated areas, you can also plant during Rabi season (November-December).",
    },
    {
        "user_message": "ಮಳೆಗಾಲದಲ್ಲಿ ಮೆಣಸಿನ ಗಿಡಗಳನ್ನು ಹೇಗೆ ನೋಡಿಕೊಳ್ಳಬೇಕು?",
        "ai_response": "ಮಳೆಗಾಲದಲ್ಲಿ ಮೆಣಸಿನ ಗಿಡಗಳಿಗೆ ಒಳ್ಳೆಯ ಒಳಚರಂಡಿ ಬೇಕು. ಅಧಿಕ ನೀರು ಸೇರದಂತೆ ನೋಡಿಕೊಳ್ಳಿ ಮತ್ತು ಶಿಲೀಂಧ್ರ ರೋಗಗಳಿಗೆ ಸಾವಯವ ಔಷಧಿ ಸಿಂಪಡಿಸಿ.",
    },
]


def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return pwd_context.hash(password)


def create_demo_users(db: Session) -> list[User]:
    """Create demo users."""
    users = []

    for i, farmer_data in enumerate(SAMPLE_FARMERS):
        user = User(
            name=farmer_data["name"],
            email=farmer_data["email"],
            password_hash=hash_password(
                "demo123"
            ),  # Default password for all demo users
            phone=farmer_data["phone"],
            location=farmer_data["location"],
            district=farmer_data["district"],
            state="Karnataka",
            latitude=farmer_data["latitude"],
            longitude=farmer_data["longitude"],
        )
        db.add(user)
        users.append(user)

    db.commit()

    # Refresh to get IDs
    for user in users:
        db.refresh(user)

    return users


def create_demo_crops(db: Session, users: list[User]) -> list[Crop]:
    """Create demo farms for users."""
    farms = []

    for i, (user, farm_data) in enumerate(zip(users, SAMPLE_FARMS)):
        # Calculate planting and harvest dates
        planting_date = date.today() - timedelta(days=random.randint(30, 120))
        expected_harvest_date = planting_date + timedelta(days=random.randint(60, 180))

        farm = Crop(
            user_id=user.id,
            crop_name=farm_data["crop_name"],
            crop_code=f"NK{1000 + i}",
            latitude=user.latitude + random.uniform(-0.01, 0.01),
            longitude=user.longitude + random.uniform(-0.01, 0.01),
            address=f"{farm_data['crop_name']}, {user.location}",
            village=user.location,
            district=user.district,
            state="Karnataka",
            total_area_acres=farm_data["total_area_acres"],
            cultivable_area_acres=farm_data["cultivable_area_acres"],
            soil_type=farm_data["soil_type"],
            water_source=farm_data["water_source"],
            irrigation_type=farm_data["irrigation_type"],
            current_crop=farm_data["current_crop"],
            crop_variety=farm_data["crop_variety"],
            planting_date=planting_date,
            expected_harvest_date=expected_harvest_date,
            crop_stage=farm_data["crop_stage"],
            crop_health_score=farm_data["crop_health_score"],
            previous_crops=farm_data["previous_crops"],
            average_yield=farm_data["average_yield"],
        )
        db.add(farm)
        farms.append(farm)

    db.commit()

    # Refresh to get IDs
    for farm in farms:
        db.refresh(farm)

    return farms


def create_demo_daily_logs(db: Session, farms: list[Crop]) -> None:
    """Create demo daily logs."""
    for farm in farms:
        # Create logs for the past 30 days
        for days_ago in range(30):
            log_date = date.today() - timedelta(days=days_ago)

            # Skip some days randomly to make it realistic
            if random.random() < 0.3:
                continue

            activity = random.choice(SAMPLE_ACTIVITIES)

            daily_log = DailyLog(
                crop_id=farm.id,
                log_date=log_date,
                activity_type="farming",
                activity_details={
                    "description": activity,
                    "duration": random.randint(30, 180),
                },
                weather_conditions=random.choice(
                    ["Sunny", "Cloudy", "Rainy", "Partly Cloudy"]
                ),
                weather_temp=random.uniform(20, 35),
                weather_humidity=random.uniform(40, 90),
                notes=f"Completed {activity.lower()} successfully.",
                voice_note_url=None,
                images=[],
            )
            db.add(daily_log)

    db.commit()


def create_demo_todos(db: Session, users: list[User], farms: list[Crop]) -> None:
    """Create demo todo tasks."""
    todo_tasks = [
        "Apply fertilizer to tomato plants",
        "Check irrigation system",
        "Harvest ready vegetables",
        "Spray organic pesticide",
        "Prepare soil for next planting",
        "Clean farm equipment",
        "Check weather forecast",
        "Visit agricultural extension office",
        "Buy seeds for next season",
        "Repair fence around farm",
    ]

    for user, farm in zip(users, farms):
        # Create 3-5 todos per user
        for i in range(random.randint(3, 5)):
            task = random.choice(todo_tasks)
            due_date = date.today() + timedelta(days=random.randint(1, 14))

            todo = TodoTask(
                user_id=user.id,
                crop_id=farm.id,
                task_title=task,
                task_description=f"Remember to {task.lower()} for {farm.current_crop}",
                due_date=due_date,
                priority=random.choice(["low", "medium", "high"]),
                status="pending",
                is_recurring=random.choice([True, False]),
                recurrence_pattern="weekly" if random.choice([True, False]) else None,
            )
            db.add(todo)

    db.commit()


def create_demo_sales(db: Session, farms: list[Crop]) -> None:
    """Create demo sales records."""
    for farm in farms:
        # Create 5-10 sales records for the past 6 months
        for _ in range(random.randint(5, 10)):
            sale_date = date.today() - timedelta(days=random.randint(1, 180))
            quantity = random.uniform(10, 500)
            price_per_unit = random.uniform(5, 100)

            sale = Sale(
                crop_id=farm.id,
                crop_type=farm.current_crop,
                crop_variety=farm.crop_variety,
                quantity_kg=quantity,
                price_per_kg=round(price_per_unit, 2),
                total_amount=round(quantity * price_per_unit, 2),
                buyer_name=random.choice(
                    [
                        "Local Market",
                        "Wholesale Trader",
                        "Direct Consumer",
                        "Cooperative Society",
                    ]
                ),
                buyer_contact=f"+91-98765432{random.randint(10, 99)}",
                sale_date=sale_date,
                payment_status=random.choice(["completed", "pending", "partial"]),
                payment_method=random.choice(["cash", "bank_transfer", "cheque"]),
                market_price_reference=round(
                    price_per_unit * random.uniform(0.9, 1.1), 2
                ),
                notes=f"Sale of {farm.current_crop} from {farm.crop_name}",
            )
            db.add(sale)

    db.commit()


def create_demo_chat_history(db: Session, users: list[User]) -> None:
    """Create demo chat history."""
    for user in users:
        # Create 3-5 chat conversations per user
        for i in range(random.randint(3, 5)):
            chat_data = random.choice(SAMPLE_CHAT_MESSAGES)

            chat = ChatHistory(
                user_id=user.id,
                user_message=chat_data["user_message"],
                ai_response=chat_data["ai_response"],
                language=random.choice(["kn", "en"]),
                message_type="general",
                context_data={"farm_context": "general_farming"},
                user_rating=random.randint(4, 5) if random.random() < 0.8 else None,
            )
            db.add(chat)

    db.commit()


def create_demo_weather_history(db: Session, users: list[User]) -> None:
    """Create demo weather history."""
    for user in users:
        # Create weather records for the past 7 days
        for days_ago in range(7):
            weather_date = date.today() - timedelta(days=days_ago)

            weather = WeatherHistory(
                user_id=user.id,
                location_name=user.location,
                latitude=user.latitude,
                longitude=user.longitude,
                date=weather_date,
                temperature=random.uniform(20, 35),
                humidity=random.uniform(40, 90),
                rainfall=random.uniform(0, 50) if random.random() < 0.4 else 0,
                wind_speed=random.uniform(5, 25),
                conditions=random.choice(["sunny", "cloudy", "rainy", "partly_cloudy"]),
                recommended_actions=f"Good day for {random.choice(['irrigation', 'harvesting', 'planting', 'fertilizing'])}",
            )
            db.add(weather)

    db.commit()


def seed_demo_data():
    """Main function to seed all demo data."""
    print("🌱 Starting demo data seeding...")

    # Create tables
    create_tables()

    # Get database session
    db = SessionLocal()
    try:
        # Clear existing data
        print("🧹 Clearing existing demo data...")
        db.query(WeatherHistory).delete()
        db.query(ChatHistory).delete()
        db.query(Sale).delete()
        db.query(TodoTask).delete()
        db.query(DailyLog).delete()
        db.query(Crop).delete()
        db.query(User).delete()
        db.commit()
        print("✅ Cleared existing data")
        print("👨‍🌾 Creating demo users...")
        users = create_demo_users(db)
        print(f"✅ Created {len(users)} demo users")

        print("🚜 Creating demo crops...")
        crops = create_demo_crops(db, users)
        print(f"✅ Created {len(crops)} demo crops")

        print("📝 Creating demo daily logs...")
        create_demo_daily_logs(db, crops)
        print("✅ Created demo daily logs")

        print("✅ Creating demo todo tasks...")
        create_demo_todos(db, users, crops)
        print("✅ Created demo todo tasks")

        print("💰 Creating demo sales records...")
        create_demo_sales(db, crops)
        print("✅ Created demo sales records")

        print("💬 Creating demo chat history...")
        create_demo_chat_history(db, users)
        print("✅ Created demo chat history")

        print("🌤️ Creating demo weather history...")
        create_demo_weather_history(db, users)
        print("✅ Created demo weather history")

        print("\n🎉 Demo data seeding completed successfully!")
        print("\nDemo user credentials:")
        print("Email: ravi.kumar@example.com | Password: demo123")
        print("Email: lakshmi.devi@example.com | Password: demo123")
        print("Email: suresh.gowda@example.com | Password: demo123")
        print("Email: manjula.reddy@example.com | Password: demo123")
        print("Email: krishnamurthy@example.com | Password: demo123")

    except Exception as e:
        print(f"❌ Error seeding demo data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_data()
