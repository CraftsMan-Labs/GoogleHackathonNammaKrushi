#!/usr/bin/env python3
"""
Seed data generator for Indian agricultural trends
Creates realistic daily price data for top crops, vegetables, and fruits
for both consumer and farmer markets over the last 3 months.
"""

import sqlite3
import random
import math
from datetime import datetime, timedelta, date
from typing import List, Dict, Tuple

# Top 10 crops, vegetables, and fruits in India
TOP_CROPS = [
    "Rice",
    "Wheat",
    "Sugarcane",
    "Cotton",
    "Jute",
    "Tea",
    "Coffee",
    "Tobacco",
    "Oilseeds",
    "Pulses",
]

TOP_VEGETABLES = [
    "Onion",
    "Potato",
    "Tomato",
    "Cabbage",
    "Cauliflower",
    "Brinjal",
    "Okra",
    "Green Chili",
    "Carrot",
    "Beans",
]

TOP_FRUITS = [
    "Mango",
    "Banana",
    "Apple",
    "Orange",
    "Grapes",
    "Pomegranate",
    "Papaya",
    "Guava",
    "Watermelon",
    "Pineapple",
]

# Major Indian markets and regions
MAJOR_MARKETS = [
    {"location": "Delhi", "state": "Delhi", "type": "wholesale"},
    {"location": "Mumbai", "state": "Maharashtra", "type": "retail"},
    {"location": "Bangalore", "state": "Karnataka", "type": "supermarket"},
    {"location": "Chennai", "state": "Tamil Nadu", "type": "wholesale"},
    {"location": "Kolkata", "state": "West Bengal", "type": "local_market"},
    {"location": "Hyderabad", "state": "Telangana", "type": "retail"},
    {"location": "Pune", "state": "Maharashtra", "type": "wholesale"},
    {"location": "Ahmedabad", "state": "Gujarat", "type": "local_market"},
    {"location": "Jaipur", "state": "Rajasthan", "type": "retail"},
    {"location": "Lucknow", "state": "Uttar Pradesh", "type": "wholesale"},
]

# Base prices (INR per kg) - realistic Indian market prices
BASE_PRICES = {
    # Crops
    "Rice": {"consumer": 45, "farmer": 25},
    "Wheat": {"consumer": 35, "farmer": 20},
    "Sugarcane": {"consumer": 40, "farmer": 28},
    "Cotton": {"consumer": 180, "farmer": 120},
    "Jute": {"consumer": 85, "farmer": 55},
    "Tea": {"consumer": 400, "farmer": 250},
    "Coffee": {"consumer": 600, "farmer": 350},
    "Tobacco": {"consumer": 300, "farmer": 180},
    "Oilseeds": {"consumer": 120, "farmer": 80},
    "Pulses": {"consumer": 90, "farmer": 60},
    # Vegetables
    "Onion": {"consumer": 25, "farmer": 15},
    "Potato": {"consumer": 20, "farmer": 12},
    "Tomato": {"consumer": 30, "farmer": 18},
    "Cabbage": {"consumer": 18, "farmer": 10},
    "Cauliflower": {"consumer": 25, "farmer": 15},
    "Brinjal": {"consumer": 22, "farmer": 14},
    "Okra": {"consumer": 35, "farmer": 22},
    "Green Chili": {"consumer": 80, "farmer": 50},
    "Carrot": {"consumer": 28, "farmer": 18},
    "Beans": {"consumer": 45, "farmer": 28},
    # Fruits
    "Mango": {"consumer": 60, "farmer": 35},
    "Banana": {"consumer": 40, "farmer": 25},
    "Apple": {"consumer": 120, "farmer": 80},
    "Orange": {"consumer": 50, "farmer": 30},
    "Grapes": {"consumer": 80, "farmer": 50},
    "Pomegranate": {"consumer": 150, "farmer": 100},
    "Papaya": {"consumer": 25, "farmer": 15},
    "Guava": {"consumer": 35, "farmer": 22},
    "Watermelon": {"consumer": 15, "farmer": 8},
    "Pineapple": {"consumer": 45, "farmer": 28},
}


def get_seasonal_factor(crop_name: str, current_date: date) -> float:
    """Get seasonal price factor based on crop and date"""
    month = current_date.month

    # Seasonal patterns for different crops
    seasonal_patterns = {
        # Crops - harvest seasons affect prices
        "Rice": {
            10: 0.8,
            11: 0.85,
            12: 0.9,
            1: 1.0,
            2: 1.1,
            3: 1.15,
            4: 1.2,
            5: 1.15,
            6: 1.1,
            7: 1.0,
            8: 0.9,
            9: 0.85,
        },
        "Wheat": {
            3: 0.8,
            4: 0.85,
            5: 0.9,
            6: 1.0,
            7: 1.1,
            8: 1.15,
            9: 1.2,
            10: 1.15,
            11: 1.1,
            12: 1.0,
            1: 0.95,
            2: 0.9,
        },
        # Vegetables - seasonal availability
        "Onion": {
            1: 1.2,
            2: 1.15,
            3: 1.1,
            4: 1.0,
            5: 0.9,
            6: 0.85,
            7: 0.9,
            8: 1.0,
            9: 1.1,
            10: 1.15,
            11: 1.2,
            12: 1.25,
        },
        "Potato": {
            1: 0.9,
            2: 0.85,
            3: 0.8,
            4: 0.9,
            5: 1.0,
            6: 1.1,
            7: 1.2,
            8: 1.15,
            9: 1.1,
            10: 1.0,
            11: 0.95,
            12: 0.9,
        },
        "Tomato": {
            1: 1.1,
            2: 1.0,
            3: 0.9,
            4: 0.85,
            5: 0.9,
            6: 1.0,
            7: 1.1,
            8: 1.2,
            9: 1.15,
            10: 1.1,
            11: 1.05,
            12: 1.1,
        },
        # Fruits - seasonal patterns
        "Mango": {
            1: 1.5,
            2: 1.4,
            3: 1.2,
            4: 0.8,
            5: 0.6,
            6: 0.7,
            7: 0.9,
            8: 1.1,
            9: 1.3,
            10: 1.4,
            11: 1.5,
            12: 1.5,
        },
        "Apple": {
            1: 1.0,
            2: 1.1,
            3: 1.2,
            4: 1.3,
            5: 1.4,
            6: 1.5,
            7: 1.4,
            8: 1.2,
            9: 0.8,
            10: 0.7,
            11: 0.8,
            12: 0.9,
        },
    }

    # Default seasonal pattern if crop not specified
    default_pattern = {i: 1.0 for i in range(1, 13)}

    pattern = seasonal_patterns.get(crop_name, default_pattern)
    return pattern.get(month, 1.0)


def generate_price_with_trends(
    base_price: float, days_from_start: int, crop_name: str, current_date: date
) -> float:
    """Generate realistic price with trends, seasonality, and random variations"""

    # Seasonal factor
    seasonal_factor = get_seasonal_factor(crop_name, current_date)

    # Long-term trend (slight inflation over 3 months)
    trend_factor = 1.0 + (days_from_start * 0.0008)  # ~7% annual inflation

    # Weekly cycle (markets are more active on certain days)
    weekly_cycle = 1.0 + 0.05 * math.sin(2 * math.pi * days_from_start / 7)

    # Random daily variation
    daily_variation = random.uniform(0.92, 1.08)

    # Occasional price spikes (weather, transport issues, etc.)
    if random.random() < 0.05:  # 5% chance of spike
        spike_factor = random.uniform(1.15, 1.4)
    else:
        spike_factor = 1.0

    final_price = (
        base_price
        * seasonal_factor
        * trend_factor
        * weekly_cycle
        * daily_variation
        * spike_factor
    )
    return round(final_price, 2)


def get_quality_grade() -> str:
    """Get random quality grade with realistic distribution"""
    grades = ["A", "B", "C"]
    weights = [0.3, 0.5, 0.2]  # Most produce is B grade
    return random.choices(grades, weights=weights)[0]


def get_availability_status() -> str:
    """Get random availability status"""
    statuses = ["abundant", "normal", "scarce"]
    weights = [0.2, 0.6, 0.2]
    return random.choices(statuses, weights=weights)[0]


def get_demand_level() -> str:
    """Get random demand level"""
    levels = ["high", "medium", "low"]
    weights = [0.3, 0.5, 0.2]
    return random.choices(levels, weights=weights)[0]


def get_price_trend() -> str:
    """Get random price trend"""
    trends = ["increasing", "stable", "decreasing"]
    weights = [0.35, 0.4, 0.25]
    return random.choices(trends, weights=weights)[0]


def create_database_and_tables():
    """Create database and tables if they don't exist"""
    conn = sqlite3.connect("src/namma_krushi.db")
    cursor = conn.cursor()

    # Create consumer_prices table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS consumer_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            price_date DATE NOT NULL,
            crop_type TEXT NOT NULL,
            crop_variety TEXT,
            price_per_kg REAL NOT NULL,
            market_location TEXT NOT NULL,
            market_type TEXT,
            vendor_name TEXT,
            vendor_type TEXT,
            quality_grade TEXT,
            quality_notes TEXT,
            source_region TEXT,
            transportation_distance_km REAL,
            supply_chain_stages TEXT,
            availability_status TEXT,
            demand_level TEXT,
            seasonal_factor TEXT,
            price_trend TEXT,
            price_volatility TEXT,
            competitor_price_min REAL,
            competitor_price_max REAL,
            notes TEXT,
            data_source TEXT,
            verified TEXT DEFAULT 'verified',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # Create farmer_prices table (similar structure for farmer pricing)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS farmer_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            price_date DATE NOT NULL,
            crop_type TEXT NOT NULL,
            crop_variety TEXT,
            price_per_kg REAL NOT NULL,
            market_location TEXT NOT NULL,
            market_type TEXT,
            farmer_name TEXT,
            farm_size_acres REAL,
            quality_grade TEXT,
            quantity_sold_kg REAL,
            source_region TEXT,
            transportation_cost_per_kg REAL,
            middleman_involved TEXT,
            payment_terms TEXT,
            availability_status TEXT,
            demand_level TEXT,
            seasonal_factor TEXT,
            price_trend TEXT,
            price_volatility TEXT,
            notes TEXT,
            data_source TEXT,
            verified TEXT DEFAULT 'verified',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    conn.commit()
    conn.close()


def generate_consumer_price_data():
    """Generate consumer price data for the last 3 months"""
    conn = sqlite3.connect("src/namma_krushi.db")
    cursor = conn.cursor()

    # Clear existing data
    cursor.execute("DELETE FROM consumer_prices")

    # Generate data for last 3 months (90 days)
    end_date = date.today()
    start_date = end_date - timedelta(days=90)

    all_crops = TOP_CROPS + TOP_VEGETABLES + TOP_FRUITS

    for single_date in (start_date + timedelta(n) for n in range(90)):
        days_from_start = (single_date - start_date).days

        for crop in all_crops:
            # Generate data for 2-3 markets per crop per day
            selected_markets = random.sample(MAJOR_MARKETS, random.randint(2, 4))

            for market in selected_markets:
                base_consumer_price = BASE_PRICES[crop]["consumer"]

                # Generate price with realistic variations
                price = generate_price_with_trends(
                    base_consumer_price, days_from_start, crop, single_date
                )

                # Add market type adjustment
                market_adjustments = {
                    "wholesale": 0.85,
                    "retail": 1.0,
                    "supermarket": 1.15,
                    "local_market": 0.95,
                }
                price *= market_adjustments.get(market["type"], 1.0)

                # Generate competitor prices
                competitor_min = round(price * random.uniform(0.9, 0.95), 2)
                competitor_max = round(price * random.uniform(1.05, 1.15), 2)

                # Insert data
                cursor.execute(
                    """
                    INSERT INTO consumer_prices (
                        price_date, crop_type, crop_variety, price_per_kg,
                        market_location, market_type, vendor_name, vendor_type,
                        quality_grade, source_region, transportation_distance_km,
                        supply_chain_stages, availability_status, demand_level,
                        seasonal_factor, price_trend, price_volatility,
                        competitor_price_min, competitor_price_max,
                        data_source, verified
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        single_date.isoformat(),
                        crop,
                        f"{crop} Premium"
                        if random.random() > 0.7
                        else f"{crop} Standard",
                        price,
                        market["location"],
                        market["type"],
                        f"{market['location']} {market['type'].title()} Store",
                        market["type"],
                        get_quality_grade(),
                        market["state"],
                        random.randint(50, 500),
                        "farmer->wholesaler->retailer"
                        if market["type"] == "retail"
                        else "farmer->wholesaler",
                        get_availability_status(),
                        get_demand_level(),
                        "normal"
                        if 0.9 <= get_seasonal_factor(crop, single_date) <= 1.1
                        else "seasonal",
                        get_price_trend(),
                        "medium",
                        competitor_min,
                        competitor_max,
                        "market_survey",
                        "verified",
                    ),
                )

    conn.commit()
    conn.close()
    print(f"Generated consumer price data for {len(all_crops)} crops across 90 days")


def generate_farmer_price_data():
    """Generate farmer price data for the last 3 months"""
    conn = sqlite3.connect("src/namma_krushi.db")
    cursor = conn.cursor()

    # Clear existing data
    cursor.execute("DELETE FROM farmer_prices")

    # Generate data for last 3 months (90 days)
    end_date = date.today()
    start_date = end_date - timedelta(days=90)

    all_crops = TOP_CROPS + TOP_VEGETABLES + TOP_FRUITS

    for single_date in (start_date + timedelta(n) for n in range(90)):
        days_from_start = (single_date - start_date).days

        for crop in all_crops:
            # Generate data for 1-2 markets per crop per day (farmers sell less frequently)
            selected_markets = random.sample(MAJOR_MARKETS, random.randint(1, 3))

            for market in selected_markets:
                base_farmer_price = BASE_PRICES[crop]["farmer"]

                # Generate price with realistic variations
                price = generate_price_with_trends(
                    base_farmer_price, days_from_start, crop, single_date
                )

                # Farmer prices are typically lower and more volatile
                price *= random.uniform(0.85, 1.05)

                # Generate realistic farm data
                farm_size = random.uniform(1.0, 50.0)
                quantity_sold = random.uniform(100, 5000)  # kg
                transportation_cost = random.uniform(1.0, 5.0)  # per kg

                # Insert data
                cursor.execute(
                    """
                    INSERT INTO farmer_prices (
                        price_date, crop_type, crop_variety, price_per_kg,
                        market_location, market_type, farmer_name, farm_size_acres,
                        quality_grade, quantity_sold_kg, source_region,
                        transportation_cost_per_kg, middleman_involved, payment_terms,
                        availability_status, demand_level, seasonal_factor,
                        price_trend, price_volatility, data_source, verified
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        single_date.isoformat(),
                        crop,
                        f"{crop} Local" if random.random() > 0.6 else f"{crop} Hybrid",
                        round(price, 2),
                        market["location"],
                        "mandi" if market["type"] == "wholesale" else "direct_sale",
                        f"Farmer_{random.randint(1000, 9999)}",
                        round(farm_size, 2),
                        get_quality_grade(),
                        round(quantity_sold, 2),
                        market["state"],
                        round(transportation_cost, 2),
                        "yes" if random.random() > 0.4 else "no",
                        "immediate" if random.random() > 0.7 else "15_days",
                        get_availability_status(),
                        get_demand_level(),
                        "normal"
                        if 0.9 <= get_seasonal_factor(crop, single_date) <= 1.1
                        else "seasonal",
                        get_price_trend(),
                        "high" if random.random() > 0.6 else "medium",
                        "market_survey",
                        "verified",
                    ),
                )

    conn.commit()
    conn.close()
    print(f"Generated farmer price data for {len(all_crops)} crops across 90 days")


def generate_summary_stats():
    """Generate and display summary statistics"""
    conn = sqlite3.connect("src/namma_krushi.db")
    cursor = conn.cursor()

    print("\n=== SUMMARY STATISTICS ===")

    # Consumer prices summary
    cursor.execute("SELECT COUNT(*) FROM consumer_prices")
    consumer_count = cursor.fetchone()[0]
    print(f"Total consumer price records: {consumer_count}")

    # Farmer prices summary
    cursor.execute("SELECT COUNT(*) FROM farmer_prices")
    farmer_count = cursor.fetchone()[0]
    print(f"Total farmer price records: {farmer_count}")

    # Date range
    cursor.execute("SELECT MIN(price_date), MAX(price_date) FROM consumer_prices")
    min_date, max_date = cursor.fetchone()
    print(f"Date range: {min_date} to {max_date}")

    # Top 5 most expensive crops (consumer)
    cursor.execute(
        """
        SELECT crop_type, AVG(price_per_kg) as avg_price 
        FROM consumer_prices 
        GROUP BY crop_type 
        ORDER BY avg_price DESC 
        LIMIT 5
    """
    )
    print("\nTop 5 most expensive crops (consumer avg):")
    for crop, price in cursor.fetchall():
        print(f"  {crop}: ₹{price:.2f}/kg")

    # Price trends by market type
    cursor.execute(
        """
        SELECT market_type, AVG(price_per_kg) as avg_price, COUNT(*) as records
        FROM consumer_prices 
        GROUP BY market_type 
        ORDER BY avg_price DESC
    """
    )
    print("\nAverage prices by market type:")
    for market_type, avg_price, records in cursor.fetchall():
        print(f"  {market_type}: ₹{avg_price:.2f}/kg ({records} records)")

    conn.close()


def main():
    """Main function to generate all seed data"""
    print("🌱 Generating Indian Agricultural Trends Seed Data...")
    print("=" * 60)

    # Create database and tables
    print("📊 Creating database and tables...")
    create_database_and_tables()

    # Generate consumer price data
    print("🛒 Generating consumer price data...")
    generate_consumer_price_data()

    # Generate farmer price data
    print("👨‍🌾 Generating farmer price data...")
    generate_farmer_price_data()

    # Generate summary statistics
    generate_summary_stats()

    print("\n✅ Seed data generation completed successfully!")
    print("📈 Data includes:")
    print("   • 30 agricultural products (10 crops + 10 vegetables + 10 fruits)")
    print("   • 90 days of daily price trends")
    print("   • 10 major Indian markets")
    print("   • Both consumer and farmer pricing data")
    print("   • Realistic seasonal variations and market dynamics")


if __name__ == "__main__":
    main()
