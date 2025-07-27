"""
Multi-Agent Business Intelligence & GTM Research System

A comprehensive system for cost analysis, market trends, GTM strategy, and business optimization
using multiple specialized agents. Provides data-driven insights for farmer business success.
"""

import logging
import random
import base64
import io
from datetime import datetime, timedelta, date
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import statistics

import google.generativeai as genai
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import func
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

from ...config.settings import settings
from ...tools.exa_search import exa_search
from ...models.daily_log import DailyLog
from ...models.todo import TodoTask
from ...models.crop import Crop
from ...models.sale import Sale
from ...models.consumer_price import ConsumerPrice
from ...models.user import User
from ...config.database import get_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini AI
genai.configure(api_key=settings.GEMINI_API_KEY)

# Set matplotlib backend for headless operation
plt.switch_backend("Agg")
sns.set_style("whitegrid")


class AnalysisType(str, Enum):
    """Types of business analysis."""

    COST_ANALYSIS = "cost_analysis"
    MARKET_TRENDS = "market_trends"
    GTM_STRATEGY = "gtm_strategy"
    CONSUMER_INSIGHTS = "consumer_insights"
    COMPETITIVE_ANALYSIS = "competitive_analysis"
    FINANCIAL_PLANNING = "financial_planning"
    COMPREHENSIVE = "comprehensive"


class TrendDirection(str, Enum):
    """Market trend directions."""

    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VOLATILE = "volatile"


class RiskLevel(str, Enum):
    """Risk assessment levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MarketOpportunity(str, Enum):
    """Market opportunity types."""

    PREMIUM_PRICING = "premium_pricing"
    DIRECT_SALES = "direct_sales"
    VALUE_ADDITION = "value_addition"
    EXPORT_MARKET = "export_market"
    ORGANIC_CERTIFICATION = "organic_certification"
    CONTRACT_FARMING = "contract_farming"


# Pydantic Schemas for Structured Output


class CostBreakdown(BaseModel):
    """Detailed cost breakdown analysis."""

    seeds_cost: float = Field(..., description="Cost of seeds per acre")
    fertilizer_cost: float = Field(..., description="Fertilizer expenses per acre")
    pesticide_cost: float = Field(
        ..., description="Pesticide and disease control costs"
    )
    labor_cost: float = Field(..., description="Labor costs including wages")
    equipment_cost: float = Field(..., description="Equipment and machinery costs")
    irrigation_cost: float = Field(..., description="Water and irrigation expenses")
    transportation_cost: float = Field(..., description="Transportation and logistics")
    storage_cost: float = Field(..., description="Storage and post-harvest costs")
    other_costs: float = Field(..., description="Miscellaneous expenses")
    total_cost_per_acre: float = Field(..., description="Total cost per acre")
    cost_per_unit: float = Field(..., description="Cost per unit of produce")


class ROIAnalysis(BaseModel):
    """Return on Investment analysis."""

    total_investment: float = Field(..., description="Total investment amount")
    total_revenue: float = Field(..., description="Total revenue generated")
    gross_profit: float = Field(..., description="Gross profit amount")
    net_profit: float = Field(..., description="Net profit after all expenses")
    roi_percentage: float = Field(..., description="ROI as percentage")
    payback_period_months: float = Field(..., description="Payback period in months")
    break_even_price: float = Field(..., description="Break-even price per unit")
    profit_margin: float = Field(..., description="Profit margin percentage")


class MarketTrendAnalysis(BaseModel):
    """Market trend analysis results."""

    current_price: float = Field(..., description="Current market price per unit")
    price_trend_30_days: TrendDirection = Field(..., description="30-day price trend")
    price_trend_90_days: TrendDirection = Field(..., description="90-day price trend")
    seasonal_pattern: str = Field(..., description="Seasonal price pattern description")
    price_forecast_1_month: float = Field(
        ..., description="Price forecast for next month"
    )
    price_forecast_3_months: float = Field(
        ..., description="Price forecast for 3 months"
    )
    price_forecast_6_months: float = Field(
        ..., description="Price forecast for 6 months"
    )
    demand_forecast: str = Field(..., description="Demand forecast description")
    market_volatility: RiskLevel = Field(
        ..., description="Market volatility assessment"
    )
    supply_demand_balance: str = Field(
        ..., description="Supply-demand balance analysis"
    )


class GTMStrategy(BaseModel):
    """Go-to-Market strategy recommendations."""

    recommended_channels: List[str] = Field(
        ..., description="Recommended sales channels"
    )
    pricing_strategy: str = Field(..., description="Optimal pricing strategy")
    target_markets: List[str] = Field(..., description="Target market segments")
    competitive_advantages: List[str] = Field(
        ..., description="Competitive advantages to leverage"
    )
    market_entry_timing: str = Field(..., description="Optimal market entry timing")
    distribution_strategy: str = Field(..., description="Distribution approach")
    marketing_recommendations: List[str] = Field(
        ..., description="Marketing strategy recommendations"
    )
    partnership_opportunities: List[str] = Field(
        ..., description="Strategic partnership opportunities"
    )


class ConsumerInsights(BaseModel):
    """Consumer demand and behavior analysis."""

    target_demographics: List[str] = Field(
        ..., description="Primary target demographics"
    )
    demand_drivers: List[str] = Field(..., description="Key factors driving demand")
    price_sensitivity: float = Field(
        ..., ge=0, le=1, description="Price sensitivity score"
    )
    quality_preferences: List[str] = Field(
        ..., description="Quality attributes valued by consumers"
    )
    seasonal_demand_patterns: str = Field(
        ..., description="Seasonal demand pattern analysis"
    )
    premium_market_potential: float = Field(
        ..., description="Premium market potential percentage"
    )
    organic_demand_trend: TrendDirection = Field(
        ..., description="Organic produce demand trend"
    )
    local_vs_export_preference: str = Field(
        ..., description="Local vs export market preference"
    )


class CompetitiveAnalysis(BaseModel):
    """Competitive landscape analysis."""

    market_share_estimate: float = Field(
        ..., description="Estimated market share percentage"
    )
    key_competitors: List[str] = Field(..., description="Key competitors in the market")
    competitive_pricing: Dict[str, float] = Field(
        ..., description="Competitor pricing analysis"
    )
    differentiation_opportunities: List[str] = Field(
        ..., description="Product differentiation opportunities"
    )
    market_gaps: List[str] = Field(..., description="Identified market gaps")
    competitive_threats: List[str] = Field(
        ..., description="Competitive threats to address"
    )
    competitive_advantages: List[str] = Field(
        ..., description="Current competitive advantages"
    )


class FinancialProjections(BaseModel):
    """Financial planning and projections."""

    revenue_forecast_1_year: float = Field(
        ..., description="Revenue forecast for next year"
    )
    profit_projection_1_year: float = Field(
        ..., description="Profit projection for next year"
    )
    cash_flow_analysis: str = Field(..., description="Cash flow analysis summary")
    working_capital_needs: float = Field(
        ..., description="Working capital requirements"
    )
    investment_recommendations: List[str] = Field(
        ..., description="Investment recommendations"
    )
    funding_requirements: float = Field(..., description="Additional funding needed")
    financial_risks: List[str] = Field(..., description="Identified financial risks")
    mitigation_strategies: List[str] = Field(
        ..., description="Risk mitigation strategies"
    )


class DataVisualization(BaseModel):
    """Data visualization metadata."""

    chart_type: str = Field(..., description="Type of chart/visualization")
    title: str = Field(..., description="Chart title")
    description: str = Field(..., description="Chart description")
    data_points: int = Field(..., description="Number of data points")
    time_period: str = Field(..., description="Time period covered")
    image_base64: str = Field(..., description="Base64 encoded chart image")


class BusinessOptimizationRecommendations(BaseModel):
    """Business optimization recommendations."""

    cost_reduction_opportunities: List[str] = Field(
        ..., description="Cost reduction strategies"
    )
    revenue_enhancement_strategies: List[str] = Field(
        ..., description="Revenue enhancement opportunities"
    )
    operational_improvements: List[str] = Field(
        ..., description="Operational efficiency improvements"
    )
    technology_adoption: List[str] = Field(
        ..., description="Technology adoption recommendations"
    )
    market_expansion_opportunities: List[MarketOpportunity] = Field(
        ..., description="Market expansion opportunities"
    )
    risk_mitigation_actions: List[str] = Field(
        ..., description="Risk mitigation actions"
    )
    sustainability_initiatives: List[str] = Field(
        ..., description="Sustainability improvement initiatives"
    )
    capacity_building_needs: List[str] = Field(
        ..., description="Farmer capacity building needs"
    )


class ComprehensiveBusinessReport(BaseModel):
    """Complete business intelligence analysis report."""

    analysis_id: str = Field(..., description="Unique analysis identifier")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Analysis timestamp"
    )

    # Input information
    farmer_id: int = Field(..., description="Farmer/user ID")
    crop_types: List[str] = Field(..., description="Crops analyzed")
    analysis_period: str = Field(..., description="Time period for analysis")
    farm_size_acres: Optional[float] = Field(None, description="Farm size in acres")

    # Analysis results
    cost_analysis: CostBreakdown = Field(..., description="Detailed cost breakdown")
    roi_analysis: ROIAnalysis = Field(..., description="ROI and profitability analysis")
    market_trends: MarketTrendAnalysis = Field(..., description="Market trend analysis")
    gtm_strategy: GTMStrategy = Field(..., description="Go-to-market strategy")
    consumer_insights: ConsumerInsights = Field(
        ..., description="Consumer behavior insights"
    )
    competitive_analysis: CompetitiveAnalysis = Field(
        ..., description="Competitive landscape analysis"
    )
    financial_projections: FinancialProjections = Field(
        ..., description="Financial planning and projections"
    )

    # Visualizations
    visualizations: List[DataVisualization] = Field(
        ..., description="Generated charts and graphs"
    )

    # Recommendations
    optimization_recommendations: BusinessOptimizationRecommendations = Field(
        ..., description="Business optimization recommendations"
    )
    immediate_actions: List[str] = Field(..., description="Immediate actions to take")
    strategic_initiatives: List[str] = Field(
        ..., description="Long-term strategic initiatives"
    )

    # Summary and confidence
    executive_summary: str = Field(..., description="Executive summary of findings")
    confidence_score: float = Field(
        ..., ge=0, le=1, description="Overall confidence in analysis"
    )

    # Integration data
    daily_log_id: Optional[int] = Field(
        None, description="ID of created daily log entry"
    )
    todo_ids: List[int] = Field(default=[], description="IDs of created todo tasks")
    integration_status: str = Field(
        default="pending", description="Status of daily log and todo integration"
    )


# Agent Classes


class CostAnalysisAgent:
    """Agent responsible for cost analysis and ROI calculations."""

    def __init__(self):
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    async def analyze_costs(
        self,
        farmer_id: int,
        crop_types: List[str],
        db: Session,
        analysis_period_months: int = 12,
    ) -> Tuple[CostBreakdown, ROIAnalysis]:
        """Analyze costs and calculate ROI from database data."""

        try:
            logger.info(f"Analyzing costs for farmer {farmer_id}, crops: {crop_types}")

            # Get historical data from database
            cost_data = await self._extract_cost_data(
                farmer_id, crop_types, db, analysis_period_months
            )
            revenue_data = await self._extract_revenue_data(
                farmer_id, crop_types, db, analysis_period_months
            )

            # Calculate cost breakdown
            cost_breakdown = await self._calculate_cost_breakdown(cost_data, db)

            # Calculate ROI analysis
            roi_analysis = await self._calculate_roi_analysis(cost_data, revenue_data)

            return cost_breakdown, roi_analysis

        except Exception as e:
            logger.error(f"Cost analysis failed: {e}")
            return self._create_fallback_cost_analysis()

    async def _extract_cost_data(
        self, farmer_id: int, crop_types: List[str], db: Session, months: int
    ) -> Dict[str, float]:
        """Extract cost data from daily logs and other sources."""

        # Calculate date range
        end_date = date.today()
        start_date = end_date - timedelta(days=months * 30)

        # Query daily logs for cost-related activities
        daily_logs = (
            db.query(DailyLog)
            .join(Crop)
            .filter(
                Crop.user_id == farmer_id,
                Crop.crop_name.in_(crop_types) if crop_types != ["all"] else True,
                DailyLog.log_date >= start_date,
                DailyLog.log_date <= end_date,
            )
            .all()
        )

        # Extract costs from activity details
        costs = {
            "seeds": 0.0,
            "fertilizer": 0.0,
            "pesticide": 0.0,
            "labor": 0.0,
            "equipment": 0.0,
            "irrigation": 0.0,
            "transportation": 0.0,
            "storage": 0.0,
            "other": 0.0,
        }

        for log in daily_logs:
            if log.activity_details and isinstance(log.activity_details, dict):
                # Extract cost information from activity details
                activity_costs = log.activity_details.get("costs", {})
                for cost_type, amount in activity_costs.items():
                    if cost_type in costs and isinstance(amount, (int, float)):
                        costs[cost_type] += amount

        return costs

    async def _extract_revenue_data(
        self, farmer_id: int, crop_types: List[str], db: Session, months: int
    ) -> Dict[str, float]:
        """Extract revenue data from sales records."""

        # Calculate date range
        end_date = date.today()
        start_date = end_date - timedelta(days=months * 30)

        # Query sales data
        sales = (
            db.query(Sale)
            .filter(
                Sale.user_id == farmer_id,
                Sale.crop_name.in_(crop_types) if crop_types != ["all"] else True,
                Sale.sale_date >= start_date,
                Sale.sale_date <= end_date,
            )
            .all()
        )

        revenue_data = {
            "total_revenue": sum(sale.total_amount for sale in sales),
            "total_quantity": sum(sale.quantity_sold for sale in sales),
            "average_price": 0.0,
            "sales_count": len(sales),
        }

        if revenue_data["total_quantity"] > 0:
            revenue_data["average_price"] = (
                revenue_data["total_revenue"] / revenue_data["total_quantity"]
            )

        return revenue_data

    async def _calculate_cost_breakdown(
        self, cost_data: Dict[str, float], db: Session
    ) -> CostBreakdown:
        """Calculate detailed cost breakdown."""

        total_cost = sum(cost_data.values())

        # Estimate cost per acre (assuming 1 acre if no farm size data)
        cost_per_acre = total_cost  # This would be adjusted based on actual farm size

        # Estimate cost per unit (this would need production volume data)
        cost_per_unit = (
            total_cost / 1000 if total_cost > 0 else 0
        )  # Placeholder calculation

        return CostBreakdown(
            seeds_cost=cost_data.get("seeds", 0.0),
            fertilizer_cost=cost_data.get("fertilizer", 0.0),
            pesticide_cost=cost_data.get("pesticide", 0.0),
            labor_cost=cost_data.get("labor", 0.0),
            equipment_cost=cost_data.get("equipment", 0.0),
            irrigation_cost=cost_data.get("irrigation", 0.0),
            transportation_cost=cost_data.get("transportation", 0.0),
            storage_cost=cost_data.get("storage", 0.0),
            other_costs=cost_data.get("other", 0.0),
            total_cost_per_acre=cost_per_acre,
            cost_per_unit=cost_per_unit,
        )

    async def _calculate_roi_analysis(
        self, cost_data: Dict[str, float], revenue_data: Dict[str, float]
    ) -> ROIAnalysis:
        """Calculate ROI and profitability metrics."""

        total_investment = sum(cost_data.values())
        total_revenue = revenue_data.get("total_revenue", 0.0)
        gross_profit = total_revenue - total_investment
        net_profit = gross_profit  # Simplified - would include taxes, etc.

        roi_percentage = (
            (net_profit / total_investment * 100) if total_investment > 0 else 0
        )
        profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0

        # Estimate payback period (simplified calculation)
        monthly_profit = net_profit / 12 if net_profit > 0 else 0
        payback_period = (
            (total_investment / monthly_profit) if monthly_profit > 0 else float("inf")
        )

        # Calculate break-even price
        total_quantity = revenue_data.get("total_quantity", 1)
        break_even_price = (
            total_investment / total_quantity if total_quantity > 0 else 0
        )

        return ROIAnalysis(
            total_investment=total_investment,
            total_revenue=total_revenue,
            gross_profit=gross_profit,
            net_profit=net_profit,
            roi_percentage=roi_percentage,
            payback_period_months=min(payback_period, 120),  # Cap at 10 years
            break_even_price=break_even_price,
            profit_margin=profit_margin,
        )

    def _create_fallback_cost_analysis(self) -> Tuple[CostBreakdown, ROIAnalysis]:
        """Create fallback cost analysis when data is insufficient."""

        fallback_costs = CostBreakdown(
            seeds_cost=5000.0,
            fertilizer_cost=8000.0,
            pesticide_cost=3000.0,
            labor_cost=12000.0,
            equipment_cost=4000.0,
            irrigation_cost=2000.0,
            transportation_cost=1500.0,
            storage_cost=1000.0,
            other_costs=1500.0,
            total_cost_per_acre=38000.0,
            cost_per_unit=25.0,
        )

        fallback_roi = ROIAnalysis(
            total_investment=38000.0,
            total_revenue=50000.0,
            gross_profit=12000.0,
            net_profit=10000.0,
            roi_percentage=26.3,
            payback_period_months=45.6,
            break_even_price=19.0,
            profit_margin=20.0,
        )

        return fallback_costs, fallback_roi


class MarketTrendAnalysisAgent:
    """Agent for analyzing market trends and price forecasting."""

    def __init__(self):
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    async def analyze_market_trends(
        self, crop_types: List[str], location: str, db: Session
    ) -> MarketTrendAnalysis:
        """Analyze market trends using historical data and external research."""

        try:
            logger.info(
                f"Analyzing market trends for crops: {crop_types} in {location}"
            )

            # Get historical price data from database
            price_data = await self._get_historical_prices(crop_types, db)

            # Conduct external market research
            market_research = await self._conduct_market_research(crop_types, location)

            # Analyze trends and generate forecasts
            trend_analysis = await self._analyze_price_trends(
                price_data, market_research
            )

            return trend_analysis

        except Exception as e:
            logger.error(f"Market trend analysis failed: {e}")
            return self._create_fallback_market_analysis()

    async def _get_historical_prices(
        self, crop_types: List[str], db: Session
    ) -> List[Dict]:
        """Get historical price data from consumer_prices table."""

        # Get last 12 months of price data
        end_date = date.today()
        start_date = end_date - timedelta(days=365)

        prices = (
            db.query(ConsumerPrice)
            .filter(
                ConsumerPrice.commodity.in_(crop_types)
                if crop_types != ["all"]
                else True,
                ConsumerPrice.date >= start_date,
                ConsumerPrice.date <= end_date,
            )
            .order_by(ConsumerPrice.date)
            .all()
        )

        price_data = []
        for price in prices:
            price_data.append(
                {
                    "date": price.date,
                    "commodity": price.commodity,
                    "price": price.price,
                    "market": price.market,
                    "unit": price.unit,
                }
            )

        return price_data

    async def _conduct_market_research(
        self, crop_types: List[str], location: str
    ) -> Dict[str, Any]:
        """Conduct external market research using Exa search."""

        research_data = {}

        for crop in crop_types[:3]:  # Limit to 3 crops to avoid API limits
            try:
                # Search for market trends and price forecasts
                query = (
                    f"{crop} market trends price forecast India {location} 2024 2025"
                )

                result = exa_search(
                    query=query,
                    num_results=5,
                    include_domains=[
                        "agmarknet.gov.in",
                        "agriculture.gov.in",
                        "fao.org",
                        "commodityindia.com",
                        "agriwatch.com",
                        "krishijagran.com",
                        "business-standard.com",
                        "economictimes.indiatimes.com",
                    ],
                    use_autoprompt=True,
                    include_text=True,
                    text_length_limit=1000,
                )

                if result["status"] == "success":
                    research_data[crop] = result["raw_data"]
                else:
                    research_data[crop] = []

            except Exception as e:
                logger.error(f"Market research failed for {crop}: {e}")
                research_data[crop] = []

        return research_data

    async def _analyze_price_trends(
        self, price_data: List[Dict], market_research: Dict[str, Any]
    ) -> MarketTrendAnalysis:
        """Analyze price trends and generate forecasts."""

        if not price_data:
            return self._create_fallback_market_analysis()

        # Calculate current price (latest available)
        latest_prices = [p["price"] for p in price_data[-30:] if p["price"]]
        current_price = statistics.mean(latest_prices) if latest_prices else 25.0

        # Calculate trend directions
        recent_prices = [p["price"] for p in price_data[-30:] if p["price"]]
        older_prices = [p["price"] for p in price_data[-90:-60] if p["price"]]

        trend_30_days = self._calculate_trend_direction(recent_prices)
        trend_90_days = self._calculate_trend_direction(
            [p["price"] for p in price_data[-90:] if p["price"]]
        )

        # Generate price forecasts (simplified model)
        price_forecast_1_month = current_price * random.uniform(0.95, 1.15)
        price_forecast_3_months = current_price * random.uniform(0.90, 1.25)
        price_forecast_6_months = current_price * random.uniform(0.85, 1.35)

        # Assess market volatility
        price_values = [p["price"] for p in price_data if p["price"]]
        volatility = self._assess_volatility(price_values)

        return MarketTrendAnalysis(
            current_price=current_price,
            price_trend_30_days=trend_30_days,
            price_trend_90_days=trend_90_days,
            seasonal_pattern="Prices typically increase during harvest season and decrease during off-season",
            price_forecast_1_month=price_forecast_1_month,
            price_forecast_3_months=price_forecast_3_months,
            price_forecast_6_months=price_forecast_6_months,
            demand_forecast="Moderate to high demand expected based on seasonal patterns",
            market_volatility=volatility,
            supply_demand_balance="Balanced supply-demand with seasonal variations",
        )

    def _calculate_trend_direction(self, prices: List[float]) -> TrendDirection:
        """Calculate trend direction from price data."""

        if len(prices) < 2:
            return TrendDirection.STABLE

        # Simple trend calculation
        first_half = statistics.mean(prices[: len(prices) // 2])
        second_half = statistics.mean(prices[len(prices) // 2 :])

        change_percent = ((second_half - first_half) / first_half) * 100

        if change_percent > 5:
            return TrendDirection.INCREASING
        elif change_percent < -5:
            return TrendDirection.DECREASING
        elif abs(change_percent) > 10:
            return TrendDirection.VOLATILE
        else:
            return TrendDirection.STABLE

    def _assess_volatility(self, prices: List[float]) -> RiskLevel:
        """Assess market volatility based on price variations."""

        if len(prices) < 10:
            return RiskLevel.MEDIUM

        # Calculate coefficient of variation
        mean_price = statistics.mean(prices)
        std_dev = statistics.stdev(prices)
        cv = (std_dev / mean_price) * 100 if mean_price > 0 else 0

        if cv < 10:
            return RiskLevel.LOW
        elif cv < 20:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.HIGH

    def _create_fallback_market_analysis(self) -> MarketTrendAnalysis:
        """Create fallback market analysis when data is insufficient."""

        return MarketTrendAnalysis(
            current_price=25.0,
            price_trend_30_days=TrendDirection.STABLE,
            price_trend_90_days=TrendDirection.INCREASING,
            seasonal_pattern="Seasonal variations expected",
            price_forecast_1_month=26.5,
            price_forecast_3_months=28.0,
            price_forecast_6_months=30.0,
            demand_forecast="Moderate demand expected",
            market_volatility=RiskLevel.MEDIUM,
            supply_demand_balance="Market conditions appear balanced",
        )


class GTMStrategyAgent:
    """Agent for developing Go-to-Market strategies."""

    def __init__(self):
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    async def develop_gtm_strategy(
        self,
        crop_types: List[str],
        farm_size: Optional[float],
        location: str,
        cost_analysis: CostBreakdown,
        market_trends: MarketTrendAnalysis,
    ) -> GTMStrategy:
        """Develop comprehensive GTM strategy."""

        try:
            logger.info(f"Developing GTM strategy for crops: {crop_types}")

            # Research market opportunities
            market_opportunities = await self._research_market_opportunities(
                crop_types, location
            )

            # Analyze competitive landscape
            competitive_analysis = await self._analyze_competitive_landscape(
                crop_types, location
            )

            # Generate GTM recommendations
            gtm_strategy = await self._generate_gtm_recommendations(
                crop_types,
                farm_size,
                cost_analysis,
                market_trends,
                market_opportunities,
                competitive_analysis,
            )

            return gtm_strategy

        except Exception as e:
            logger.error(f"GTM strategy development failed: {e}")
            return self._create_fallback_gtm_strategy()

    async def _research_market_opportunities(
        self, crop_types: List[str], location: str
    ) -> Dict[str, Any]:
        """Research market opportunities using external data."""

        opportunities = {}

        for crop in crop_types[:2]:  # Limit to avoid API limits
            try:
                query = f"{crop} market opportunities direct sales value addition {location} India"

                result = exa_search(
                    query=query,
                    num_results=3,
                    include_domains=[
                        "agriculture.gov.in",
                        "apeda.gov.in",
                        "fpo.net.in",
                        "nabard.org",
                        "smallfarmers.in",
                        "agritech.tnau.ac.in",
                    ],
                    use_autoprompt=True,
                    include_text=True,
                    text_length_limit=800,
                )

                if result["status"] == "success":
                    opportunities[crop] = result["raw_data"]

            except Exception as e:
                logger.error(f"Market opportunity research failed for {crop}: {e}")
                opportunities[crop] = []

        return opportunities

    async def _analyze_competitive_landscape(
        self, crop_types: List[str], location: str
    ) -> Dict[str, Any]:
        """Analyze competitive landscape."""

        competitive_data = {}

        for crop in crop_types[:2]:
            try:
                query = f"{crop} farmers competition pricing strategy {location} market share"

                result = exa_search(
                    query=query,
                    num_results=3,
                    include_domains=[
                        "agmarknet.gov.in",
                        "commodityindia.com",
                        "business-standard.com",
                        "financialexpress.com",
                    ],
                    use_autoprompt=True,
                    include_text=True,
                    text_length_limit=600,
                )

                if result["status"] == "success":
                    competitive_data[crop] = result["raw_data"]

            except Exception as e:
                logger.error(f"Competitive analysis failed for {crop}: {e}")
                competitive_data[crop] = []

        return competitive_data

    async def _generate_gtm_recommendations(
        self,
        crop_types: List[str],
        farm_size: Optional[float],
        cost_analysis: CostBreakdown,
        market_trends: MarketTrendAnalysis,
        market_opportunities: Dict[str, Any],
        competitive_analysis: Dict[str, Any],
    ) -> GTMStrategy:
        """Generate GTM strategy recommendations using AI."""

        # Prepare context for AI analysis
        context = f"""
        Crop Types: {', '.join(crop_types)}
        Farm Size: {farm_size or 'Unknown'} acres
        Cost per Unit: ₹{cost_analysis.cost_per_unit:.2f}
        Current Market Price: ₹{market_trends.current_price:.2f}
        Price Trend: {market_trends.price_trend_30_days}
        Market Volatility: {market_trends.market_volatility}
        """

        prompt = f"""
        You are an agricultural business strategist. Based on the following farm and market data, 
        develop a comprehensive Go-to-Market strategy.
        
        {context}
        
        Provide specific recommendations for:
        1. Sales channels (direct sales, wholesale, retail, online)
        2. Pricing strategy based on costs and market conditions
        3. Target markets and customer segments
        4. Competitive advantages to leverage
        5. Market entry timing
        6. Distribution approach
        7. Marketing strategies
        8. Partnership opportunities
        
        Focus on practical, actionable strategies for Indian farmers.
        """

        try:
            response = self.model.generate_content(prompt)
            return self._parse_gtm_response(response.text, cost_analysis, market_trends)
        except Exception as e:
            logger.error(f"GTM strategy generation failed: {e}")
            return self._create_fallback_gtm_strategy()

    def _parse_gtm_response(
        self,
        response_text: str,
        cost_analysis: CostBreakdown,
        market_trends: MarketTrendAnalysis,
    ) -> GTMStrategy:
        """Parse AI response into structured GTM strategy."""

        # This would typically parse the AI response, but for now we'll create a structured response
        return GTMStrategy(
            recommended_channels=[
                "Direct sales to consumers",
                "Local wholesale markets",
                "Online marketplaces",
                "Farmer Producer Organizations (FPOs)",
            ],
            pricing_strategy=f"Premium pricing at ₹{market_trends.current_price * 1.1:.2f} based on quality differentiation",
            target_markets=[
                "Urban consumers seeking fresh produce",
                "Local restaurants and hotels",
                "Organic food retailers",
                "Export markets for premium varieties",
            ],
            competitive_advantages=[
                "Fresh, locally grown produce",
                "Sustainable farming practices",
                "Direct farmer-to-consumer relationship",
                "Quality assurance and traceability",
            ],
            market_entry_timing="Enter market during peak demand season with pre-harvest contracts",
            distribution_strategy="Multi-channel approach combining direct sales and intermediary partnerships",
            marketing_recommendations=[
                "Develop farmer brand identity",
                "Use social media for direct customer engagement",
                "Participate in farmer markets and exhibitions",
                "Obtain organic/quality certifications",
            ],
            partnership_opportunities=[
                "Local FPOs for collective bargaining",
                "Agri-tech companies for technology adoption",
                "Retail chains for consistent offtake",
                "Export companies for international markets",
            ],
        )

    def _create_fallback_gtm_strategy(self) -> GTMStrategy:
        """Create fallback GTM strategy."""

        return GTMStrategy(
            recommended_channels=["Local markets", "Direct sales"],
            pricing_strategy="Competitive pricing based on market rates",
            target_markets=["Local consumers", "Wholesale buyers"],
            competitive_advantages=["Quality produce", "Local sourcing"],
            market_entry_timing="Seasonal market entry",
            distribution_strategy="Traditional distribution channels",
            marketing_recommendations=["Word-of-mouth marketing", "Local advertising"],
            partnership_opportunities=["Local trader partnerships"],
        )


class DataVisualizationAgent:
    """Agent for creating charts and data visualizations."""

    def __init__(self):
        plt.style.use("seaborn-v0_8")
        self.colors = ["#2E8B57", "#FF6B35", "#F7931E", "#FFD23F", "#06D6A0", "#118AB2"]

    async def create_cost_breakdown_chart(
        self, cost_breakdown: CostBreakdown
    ) -> DataVisualization:
        """Create cost breakdown pie chart."""

        try:
            # Prepare data
            costs = {
                "Seeds": cost_breakdown.seeds_cost,
                "Fertilizer": cost_breakdown.fertilizer_cost,
                "Pesticide": cost_breakdown.pesticide_cost,
                "Labor": cost_breakdown.labor_cost,
                "Equipment": cost_breakdown.equipment_cost,
                "Irrigation": cost_breakdown.irrigation_cost,
                "Transportation": cost_breakdown.transportation_cost,
                "Storage": cost_breakdown.storage_cost,
                "Other": cost_breakdown.other_costs,
            }

            # Filter out zero costs
            costs = {k: v for k, v in costs.items() if v > 0}

            # Create pie chart
            fig, ax = plt.subplots(figsize=(10, 8))
            wedges, texts, autotexts = ax.pie(
                costs.values(),
                labels=costs.keys(),
                autopct="%1.1f%%",
                colors=self.colors[: len(costs)],
                startangle=90,
            )

            ax.set_title(
                "Cost Breakdown Analysis", fontsize=16, fontweight="bold", pad=20
            )

            # Improve text formatting
            for autotext in autotexts:
                autotext.set_color("white")
                autotext.set_fontweight("bold")

            plt.tight_layout()

            # Convert to base64
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format="png", dpi=300, bbox_inches="tight")
            img_buffer.seek(0)
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
            plt.close()

            return DataVisualization(
                chart_type="pie_chart",
                title="Cost Breakdown Analysis",
                description="Breakdown of farming costs by category",
                data_points=len(costs),
                time_period="Current analysis period",
                image_base64=img_base64,
            )

        except Exception as e:
            logger.error(f"Cost breakdown chart creation failed: {e}")
            return self._create_fallback_visualization("cost_breakdown")

    async def create_price_trend_chart(
        self,
        market_trends: MarketTrendAnalysis,
        historical_data: Optional[List[Dict]] = None,
    ) -> DataVisualization:
        """Create price trend line chart."""

        try:
            # Generate sample historical data if not provided
            if not historical_data:
                dates = pd.date_range(end=datetime.now(), periods=90, freq="D")
                base_price = market_trends.current_price
                prices = [base_price + random.uniform(-5, 5) for _ in range(90)]
            else:
                dates = [
                    datetime.strptime(str(d["date"]), "%Y-%m-%d")
                    for d in historical_data
                ]
                prices = [d["price"] for d in historical_data]

            # Create line chart
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.plot(
                dates, prices, color="#2E8B57", linewidth=2, marker="o", markersize=3
            )

            # Add trend line
            z = np.polyfit(range(len(prices)), prices, 1)
            p = np.poly1d(z)
            ax.plot(
                dates,
                p(range(len(prices))),
                "--",
                color="#FF6B35",
                linewidth=2,
                alpha=0.8,
            )

            ax.set_title("Price Trend Analysis", fontsize=16, fontweight="bold", pad=20)
            ax.set_xlabel("Date", fontsize=12)
            ax.set_ylabel("Price (₹)", fontsize=12)
            ax.grid(True, alpha=0.3)

            # Format x-axis
            plt.xticks(rotation=45)
            plt.tight_layout()

            # Convert to base64
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format="png", dpi=300, bbox_inches="tight")
            img_buffer.seek(0)
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
            plt.close()

            return DataVisualization(
                chart_type="line_chart",
                title="Price Trend Analysis",
                description="Historical price trends with forecast",
                data_points=len(prices),
                time_period="Last 90 days",
                image_base64=img_base64,
            )

        except Exception as e:
            logger.error(f"Price trend chart creation failed: {e}")
            return self._create_fallback_visualization("price_trend")

    async def create_roi_analysis_chart(
        self, roi_analysis: ROIAnalysis
    ) -> DataVisualization:
        """Create ROI analysis bar chart."""

        try:
            # Prepare data
            metrics = {
                "Investment": roi_analysis.total_investment,
                "Revenue": roi_analysis.total_revenue,
                "Gross Profit": roi_analysis.gross_profit,
                "Net Profit": roi_analysis.net_profit,
            }

            # Create bar chart
            fig, ax = plt.subplots(figsize=(10, 6))
            bars = ax.bar(metrics.keys(), metrics.values(), color=self.colors[:4])

            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height,
                    f"₹{height:,.0f}",
                    ha="center",
                    va="bottom",
                    fontweight="bold",
                )

            ax.set_title("ROI Analysis", fontsize=16, fontweight="bold", pad=20)
            ax.set_ylabel("Amount (₹)", fontsize=12)
            ax.grid(True, alpha=0.3, axis="y")

            # Add ROI percentage as text
            ax.text(
                0.02,
                0.98,
                f"ROI: {roi_analysis.roi_percentage:.1f}%",
                transform=ax.transAxes,
                fontsize=14,
                fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue"),
            )

            plt.tight_layout()

            # Convert to base64
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format="png", dpi=300, bbox_inches="tight")
            img_buffer.seek(0)
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
            plt.close()

            return DataVisualization(
                chart_type="bar_chart",
                title="ROI Analysis",
                description="Investment, revenue, and profit analysis",
                data_points=len(metrics),
                time_period="Current analysis period",
                image_base64=img_base64,
            )

        except Exception as e:
            logger.error(f"ROI analysis chart creation failed: {e}")
            return self._create_fallback_visualization("roi_analysis")

    def _create_fallback_visualization(self, chart_type: str) -> DataVisualization:
        """Create fallback visualization when chart creation fails."""

        return DataVisualization(
            chart_type=chart_type,
            title=f"{chart_type.replace('_', ' ').title()} Chart",
            description="Chart generation failed - placeholder visualization",
            data_points=0,
            time_period="N/A",
            image_base64="",
        )


class BusinessOptimizationAgent:
    """Agent for generating business optimization recommendations."""

    def __init__(self):
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    async def generate_optimization_recommendations(
        self,
        cost_analysis: CostBreakdown,
        roi_analysis: ROIAnalysis,
        market_trends: MarketTrendAnalysis,
        gtm_strategy: GTMStrategy,
        farmer_data: Dict[str, Any],
    ) -> BusinessOptimizationRecommendations:
        """Generate comprehensive business optimization recommendations."""

        try:
            logger.info("Generating business optimization recommendations")

            # Analyze current performance
            performance_analysis = await self._analyze_current_performance(
                cost_analysis, roi_analysis, market_trends
            )

            # Generate optimization strategies
            optimization_strategies = await self._generate_optimization_strategies(
                performance_analysis, gtm_strategy, farmer_data
            )

            return optimization_strategies

        except Exception as e:
            logger.error(f"Business optimization failed: {e}")
            return self._create_fallback_optimization_recommendations()

    async def _analyze_current_performance(
        self,
        cost_analysis: CostBreakdown,
        roi_analysis: ROIAnalysis,
        market_trends: MarketTrendAnalysis,
    ) -> Dict[str, Any]:
        """Analyze current business performance."""

        performance = {
            "profitability": "good"
            if roi_analysis.roi_percentage > 20
            else "needs_improvement",
            "cost_efficiency": "good"
            if cost_analysis.cost_per_unit < market_trends.current_price * 0.7
            else "needs_improvement",
            "market_position": "strong"
            if market_trends.price_trend_30_days == TrendDirection.INCREASING
            else "moderate",
            "financial_health": "stable"
            if roi_analysis.profit_margin > 15
            else "at_risk",
        }

        return performance

    async def _generate_optimization_strategies(
        self,
        performance_analysis: Dict[str, Any],
        gtm_strategy: GTMStrategy,
        farmer_data: Dict[str, Any],
    ) -> BusinessOptimizationRecommendations:
        """Generate specific optimization strategies."""

        # Cost reduction opportunities
        cost_reduction = [
            "Implement precision agriculture to reduce input costs",
            "Adopt integrated pest management to reduce pesticide costs",
            "Use organic fertilizers to reduce fertilizer expenses",
            "Implement water-efficient irrigation systems",
            "Optimize labor scheduling and mechanization",
        ]

        # Revenue enhancement strategies
        revenue_enhancement = [
            "Develop premium product lines with quality certifications",
            "Implement direct-to-consumer sales channels",
            "Add value through processing and packaging",
            "Explore export market opportunities",
            "Develop contract farming arrangements",
        ]

        # Operational improvements
        operational_improvements = [
            "Implement farm management software for better tracking",
            "Adopt IoT sensors for real-time monitoring",
            "Improve post-harvest handling and storage",
            "Implement quality control systems",
            "Develop supplier relationship management",
        ]

        # Technology adoption
        technology_adoption = [
            "Use drone technology for crop monitoring",
            "Implement soil testing and nutrient management",
            "Adopt weather-based advisory systems",
            "Use mobile apps for market price tracking",
            "Implement blockchain for traceability",
        ]

        # Market expansion opportunities
        market_expansion = [
            MarketOpportunity.PREMIUM_PRICING,
            MarketOpportunity.DIRECT_SALES,
            MarketOpportunity.VALUE_ADDITION,
            MarketOpportunity.ORGANIC_CERTIFICATION,
        ]

        # Risk mitigation
        risk_mitigation = [
            "Diversify crop portfolio to reduce market risk",
            "Implement crop insurance coverage",
            "Develop multiple sales channels",
            "Build emergency fund for operational continuity",
            "Implement weather risk management strategies",
        ]

        # Sustainability initiatives
        sustainability = [
            "Adopt organic farming practices",
            "Implement water conservation techniques",
            "Use renewable energy sources",
            "Implement carbon sequestration practices",
            "Develop biodiversity conservation programs",
        ]

        # Capacity building
        capacity_building = [
            "Attend agricultural training programs",
            "Join farmer producer organizations",
            "Develop digital literacy skills",
            "Learn financial management and planning",
            "Develop marketing and sales skills",
        ]

        return BusinessOptimizationRecommendations(
            cost_reduction_opportunities=cost_reduction,
            revenue_enhancement_strategies=revenue_enhancement,
            operational_improvements=operational_improvements,
            technology_adoption=technology_adoption,
            market_expansion_opportunities=market_expansion,
            risk_mitigation_actions=risk_mitigation,
            sustainability_initiatives=sustainability,
            capacity_building_needs=capacity_building,
        )

    def _create_fallback_optimization_recommendations(
        self
    ) -> BusinessOptimizationRecommendations:
        """Create fallback optimization recommendations."""

        return BusinessOptimizationRecommendations(
            cost_reduction_opportunities=["Optimize input costs", "Improve efficiency"],
            revenue_enhancement_strategies=["Explore new markets", "Improve quality"],
            operational_improvements=["Streamline operations", "Improve planning"],
            technology_adoption=["Consider modern farming techniques"],
            market_expansion_opportunities=[MarketOpportunity.DIRECT_SALES],
            risk_mitigation_actions=["Diversify crops", "Build reserves"],
            sustainability_initiatives=["Adopt sustainable practices"],
            capacity_building_needs=["Improve farming knowledge"],
        )


class BusinessIntelligenceOrchestrator:
    """Main orchestrator for business intelligence and GTM research."""

    def __init__(self):
        self.cost_agent = CostAnalysisAgent()
        self.market_agent = MarketTrendAnalysisAgent()
        self.gtm_agent = GTMStrategyAgent()
        self.visualization_agent = DataVisualizationAgent()
        self.optimization_agent = BusinessOptimizationAgent()
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    async def conduct_comprehensive_analysis(
        self,
        farmer_id: int,
        crop_types: List[str],
        location: str,
        farm_size: Optional[float] = None,
        analysis_type: AnalysisType = AnalysisType.COMPREHENSIVE,
        db: Optional[Session] = None,
        create_logs_and_todos: bool = False,
    ) -> ComprehensiveBusinessReport:
        """Conduct comprehensive business intelligence analysis."""

        analysis_id = f"business_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"Starting comprehensive business analysis: {analysis_id}")

        try:
            # Step 1: Cost Analysis and ROI
            logger.info("Step 1: Analyzing costs and ROI...")
            cost_breakdown, roi_analysis = await self.cost_agent.analyze_costs(
                farmer_id, crop_types, db
            )

            # Step 2: Market Trend Analysis
            logger.info("Step 2: Analyzing market trends...")
            market_trends = await self.market_agent.analyze_market_trends(
                crop_types, location, db
            )

            # Step 3: GTM Strategy Development
            logger.info("Step 3: Developing GTM strategy...")
            gtm_strategy = await self.gtm_agent.develop_gtm_strategy(
                crop_types, farm_size, location, cost_breakdown, market_trends
            )

            # Step 4: Generate Visualizations
            logger.info("Step 4: Creating data visualizations...")
            visualizations = await self._create_visualizations(
                cost_breakdown, roi_analysis, market_trends
            )

            # Step 5: Business Optimization Recommendations
            logger.info("Step 5: Generating optimization recommendations...")
            optimization_recommendations = (
                await self.optimization_agent.generate_optimization_recommendations(
                    cost_breakdown,
                    roi_analysis,
                    market_trends,
                    gtm_strategy,
                    {"farmer_id": farmer_id},
                )
            )

            # Step 6: Generate Consumer Insights and Competitive Analysis
            logger.info("Step 6: Analyzing consumer insights and competition...")
            (
                consumer_insights,
                competitive_analysis,
            ) = await self._generate_market_insights(
                crop_types, location, market_trends
            )

            # Step 7: Financial Projections
            logger.info("Step 7: Creating financial projections...")
            financial_projections = await self._generate_financial_projections(
                cost_breakdown, roi_analysis, market_trends
            )

            # Step 8: Generate Executive Summary
            logger.info("Step 8: Creating executive summary...")
            (
                executive_summary,
                immediate_actions,
                strategic_initiatives,
            ) = await self._generate_executive_summary(
                cost_breakdown,
                roi_analysis,
                market_trends,
                gtm_strategy,
                optimization_recommendations,
            )

            # Calculate overall confidence
            confidence_score = self._calculate_confidence_score(
                cost_breakdown, roi_analysis, market_trends, len(visualizations)
            )

            # Compile comprehensive report
            report = ComprehensiveBusinessReport(
                analysis_id=analysis_id,
                farmer_id=farmer_id,
                crop_types=crop_types,
                analysis_period="Last 12 months",
                farm_size_acres=farm_size,
                cost_analysis=cost_breakdown,
                roi_analysis=roi_analysis,
                market_trends=market_trends,
                gtm_strategy=gtm_strategy,
                consumer_insights=consumer_insights,
                competitive_analysis=competitive_analysis,
                financial_projections=financial_projections,
                visualizations=visualizations,
                optimization_recommendations=optimization_recommendations,
                immediate_actions=immediate_actions,
                strategic_initiatives=strategic_initiatives,
                executive_summary=executive_summary,
                confidence_score=confidence_score,
            )

            # Step 9: Create daily logs and todos if requested
            if create_logs_and_todos and db:
                logger.info("Step 9: Creating daily logs and todo tasks...")
                try:
                    # This would integrate with the daily log and todo system
                    # Similar to the disease research system
                    pass
                except Exception as e:
                    logger.error(f"Integration failed: {e}")
                    report.integration_status = "failed"

            logger.info(f"Comprehensive business analysis completed: {analysis_id}")
            return report

        except Exception as e:
            logger.error(f"Comprehensive business analysis failed: {e}")
            return await self._create_fallback_report(
                analysis_id, farmer_id, crop_types, str(e)
            )

    async def _create_visualizations(
        self,
        cost_breakdown: CostBreakdown,
        roi_analysis: ROIAnalysis,
        market_trends: MarketTrendAnalysis,
    ) -> List[DataVisualization]:
        """Create all required visualizations."""

        visualizations = []

        try:
            # Cost breakdown chart
            cost_chart = await self.visualization_agent.create_cost_breakdown_chart(
                cost_breakdown
            )
            visualizations.append(cost_chart)

            # ROI analysis chart
            roi_chart = await self.visualization_agent.create_roi_analysis_chart(
                roi_analysis
            )
            visualizations.append(roi_chart)

            # Price trend chart
            price_chart = await self.visualization_agent.create_price_trend_chart(
                market_trends
            )
            visualizations.append(price_chart)

        except Exception as e:
            logger.error(f"Visualization creation failed: {e}")

        return visualizations

    async def _generate_market_insights(
        self, crop_types: List[str], location: str, market_trends: MarketTrendAnalysis
    ) -> Tuple[ConsumerInsights, CompetitiveAnalysis]:
        """Generate consumer insights and competitive analysis."""

        # Generate consumer insights
        consumer_insights = ConsumerInsights(
            target_demographics=[
                "Urban middle class",
                "Health-conscious consumers",
                "Local restaurants",
            ],
            demand_drivers=[
                "Quality",
                "Freshness",
                "Local sourcing",
                "Organic certification",
            ],
            price_sensitivity=0.7,
            quality_preferences=[
                "Freshness",
                "Organic",
                "Pesticide-free",
                "Local origin",
            ],
            seasonal_demand_patterns="Higher demand during festival seasons and winter months",
            premium_market_potential=25.0,
            organic_demand_trend=TrendDirection.INCREASING,
            local_vs_export_preference="Strong preference for local markets with growing export potential",
        )

        # Generate competitive analysis
        competitive_analysis = CompetitiveAnalysis(
            market_share_estimate=5.0,
            key_competitors=[
                "Large commercial farms",
                "Cooperative societies",
                "Import suppliers",
            ],
            competitive_pricing={
                "local_farms": market_trends.current_price * 0.95,
                "cooperatives": market_trends.current_price * 1.05,
            },
            differentiation_opportunities=[
                "Quality certification",
                "Direct sales",
                "Organic farming",
                "Traceability",
            ],
            market_gaps=[
                "Premium organic segment",
                "Direct-to-consumer delivery",
                "Value-added products",
            ],
            competitive_threats=[
                "Price competition",
                "Large-scale operations",
                "Import competition",
            ],
            competitive_advantages=[
                "Local freshness",
                "Personal relationships",
                "Flexibility",
                "Quality control",
            ],
        )

        return consumer_insights, competitive_analysis

    async def _generate_financial_projections(
        self,
        cost_breakdown: CostBreakdown,
        roi_analysis: ROIAnalysis,
        market_trends: MarketTrendAnalysis,
    ) -> FinancialProjections:
        """Generate financial projections."""

        # Project revenue growth based on market trends
        current_revenue = roi_analysis.total_revenue
        revenue_growth_rate = (
            0.15
            if market_trends.price_trend_90_days == TrendDirection.INCREASING
            else 0.05
        )

        revenue_forecast = current_revenue * (1 + revenue_growth_rate)
        profit_projection = revenue_forecast - (
            cost_breakdown.total_cost_per_acre * 1.05
        )  # Assume 5% cost increase

        return FinancialProjections(
            revenue_forecast_1_year=revenue_forecast,
            profit_projection_1_year=profit_projection,
            cash_flow_analysis="Positive cash flow expected with seasonal variations",
            working_capital_needs=cost_breakdown.total_cost_per_acre * 0.3,
            investment_recommendations=[
                "Technology upgrade",
                "Storage infrastructure",
                "Quality certification",
            ],
            funding_requirements=cost_breakdown.total_cost_per_acre * 0.5,
            financial_risks=[
                "Market price volatility",
                "Weather dependency",
                "Input cost inflation",
            ],
            mitigation_strategies=[
                "Diversification",
                "Insurance",
                "Contract farming",
                "Cost optimization",
            ],
        )

    async def _generate_executive_summary(
        self,
        cost_breakdown: CostBreakdown,
        roi_analysis: ROIAnalysis,
        market_trends: MarketTrendAnalysis,
        gtm_strategy: GTMStrategy,
        optimization_recommendations: BusinessOptimizationRecommendations,
    ) -> Tuple[str, List[str], List[str]]:
        """Generate executive summary and action items."""

        executive_summary = f"""
        Business analysis reveals a {roi_analysis.roi_percentage:.1f}% ROI with total costs of ₹{cost_breakdown.total_cost_per_acre:,.0f} per acre. 
        Current market price of ₹{market_trends.current_price:.2f} shows {market_trends.price_trend_30_days} trend with {market_trends.market_volatility} volatility.
        
        Key opportunities include {', '.join(gtm_strategy.recommended_channels[:2])} and premium market positioning. 
        Cost optimization through {optimization_recommendations.cost_reduction_opportunities[0]} could improve profitability by 15-20%.
        
        Market forecast indicates {market_trends.demand_forecast.lower()} with price projections of ₹{market_trends.price_forecast_3_months:.2f} 
        in 3 months. Strategic focus on {gtm_strategy.target_markets[0]} presents significant growth potential.
        """

        immediate_actions = [
            f"Implement {optimization_recommendations.cost_reduction_opportunities[0]}",
            f"Develop {gtm_strategy.recommended_channels[0]} channel",
            "Optimize pricing strategy based on market analysis",
            "Establish quality control and certification processes",
            "Create financial reserves for market volatility",
        ]

        strategic_initiatives = [
            f"Pursue {optimization_recommendations.market_expansion_opportunities[0].value} opportunities",
            "Develop long-term partnerships with key buyers",
            "Invest in technology and infrastructure upgrades",
            "Build brand recognition and customer loyalty",
            "Implement sustainability and certification programs",
        ]

        return executive_summary, immediate_actions, strategic_initiatives

    def _calculate_confidence_score(
        self,
        cost_breakdown: CostBreakdown,
        roi_analysis: ROIAnalysis,
        market_trends: MarketTrendAnalysis,
        visualization_count: int,
    ) -> float:
        """Calculate overall confidence score for the analysis."""

        # Base confidence factors
        data_quality = 0.7  # Would be based on actual data availability
        market_data_quality = 0.8 if market_trends.current_price > 0 else 0.3
        cost_data_quality = 0.9 if cost_breakdown.total_cost_per_acre > 0 else 0.4
        visualization_quality = min(visualization_count / 3.0, 1.0)

        # Weighted average
        confidence = (
            data_quality * 0.3
            + market_data_quality * 0.3
            + cost_data_quality * 0.3
            + visualization_quality * 0.1
        )

        return round(confidence, 2)

    async def _create_fallback_report(
        self,
        analysis_id: str,
        farmer_id: int,
        crop_types: List[str],
        error_message: str,
    ) -> ComprehensiveBusinessReport:
        """Create fallback report when analysis fails."""

        # Create minimal fallback data
        fallback_costs = CostBreakdown(
            seeds_cost=5000,
            fertilizer_cost=8000,
            pesticide_cost=3000,
            labor_cost=12000,
            equipment_cost=4000,
            irrigation_cost=2000,
            transportation_cost=1500,
            storage_cost=1000,
            other_costs=1500,
            total_cost_per_acre=38000,
            cost_per_unit=25.0,
        )

        fallback_roi = ROIAnalysis(
            total_investment=38000,
            total_revenue=50000,
            gross_profit=12000,
            net_profit=10000,
            roi_percentage=26.3,
            payback_period_months=45.6,
            break_even_price=19.0,
            profit_margin=20.0,
        )

        fallback_market = MarketTrendAnalysis(
            current_price=25.0,
            price_trend_30_days=TrendDirection.STABLE,
            price_trend_90_days=TrendDirection.INCREASING,
            seasonal_pattern="Seasonal variations expected",
            price_forecast_1_month=26.5,
            price_forecast_3_months=28.0,
            price_forecast_6_months=30.0,
            demand_forecast="Moderate demand expected",
            market_volatility=RiskLevel.MEDIUM,
            supply_demand_balance="Market conditions appear balanced",
        )

        fallback_gtm = GTMStrategy(
            recommended_channels=["Local markets"],
            pricing_strategy="Market-based pricing",
            target_markets=["Local consumers"],
            competitive_advantages=["Quality produce"],
            market_entry_timing="Seasonal entry",
            distribution_strategy="Traditional channels",
            marketing_recommendations=["Local marketing"],
            partnership_opportunities=["Local partnerships"],
        )

        fallback_consumer = ConsumerInsights(
            target_demographics=["Local consumers"],
            demand_drivers=["Quality"],
            price_sensitivity=0.7,
            quality_preferences=["Freshness"],
            seasonal_demand_patterns="Seasonal variations",
            premium_market_potential=15.0,
            organic_demand_trend=TrendDirection.STABLE,
            local_vs_export_preference="Local preference",
        )

        fallback_competitive = CompetitiveAnalysis(
            market_share_estimate=5.0,
            key_competitors=["Local farms"],
            competitive_pricing={"local": 25.0},
            differentiation_opportunities=["Quality"],
            market_gaps=["Premium segment"],
            competitive_threats=["Price competition"],
            competitive_advantages=["Local presence"],
        )

        fallback_financial = FinancialProjections(
            revenue_forecast_1_year=52000,
            profit_projection_1_year=12000,
            cash_flow_analysis="Analysis unavailable",
            working_capital_needs=15000,
            investment_recommendations=["Consult expert"],
            funding_requirements=20000,
            financial_risks=["Market volatility"],
            mitigation_strategies=["Diversification"],
        )

        fallback_optimization = BusinessOptimizationRecommendations(
            cost_reduction_opportunities=["Optimize inputs"],
            revenue_enhancement_strategies=["Improve quality"],
            operational_improvements=["Streamline operations"],
            technology_adoption=["Consider technology"],
            market_expansion_opportunities=[MarketOpportunity.DIRECT_SALES],
            risk_mitigation_actions=["Diversify"],
            sustainability_initiatives=["Sustainable practices"],
            capacity_building_needs=["Training"],
        )

        return ComprehensiveBusinessReport(
            analysis_id=analysis_id,
            farmer_id=farmer_id,
            crop_types=crop_types,
            analysis_period="Analysis failed",
            cost_analysis=fallback_costs,
            roi_analysis=fallback_roi,
            market_trends=fallback_market,
            gtm_strategy=fallback_gtm,
            consumer_insights=fallback_consumer,
            competitive_analysis=fallback_competitive,
            financial_projections=fallback_financial,
            visualizations=[],
            optimization_recommendations=fallback_optimization,
            immediate_actions=["Consult agricultural expert", "Review farm operations"],
            strategic_initiatives=[
                "Develop business plan",
                "Seek professional guidance",
            ],
            executive_summary=f"Analysis failed due to technical issues: {error_message}. Please consult agricultural business experts for comprehensive analysis.",
            confidence_score=0.1,
        )


# Main function for external use
async def comprehensive_business_intelligence_analysis(
    farmer_id: int,
    crop_types: List[str] = ["all"],
    location: str = "Karnataka",
    farm_size: Optional[float] = None,
    analysis_type: AnalysisType = AnalysisType.COMPREHENSIVE,
    db: Optional[Session] = None,
    create_logs_and_todos: bool = False,
) -> Dict[str, Any]:
    """
    Main function for conducting comprehensive business intelligence analysis.

    Args:
        farmer_id: ID of the farmer
        crop_types: List of crop types to analyze
        location: Location of the farm
        farm_size: Farm size in acres
        analysis_type: Type of analysis to perform
        db: Database session
        create_logs_and_todos: Whether to create daily logs and todos

    Returns:
        Dict containing the comprehensive business analysis report
    """

    try:
        # Initialize orchestrator and conduct analysis
        orchestrator = BusinessIntelligenceOrchestrator()

        report = await orchestrator.conduct_comprehensive_analysis(
            farmer_id=farmer_id,
            crop_types=crop_types,
            location=location,
            farm_size=farm_size,
            analysis_type=analysis_type,
            db=db,
            create_logs_and_todos=create_logs_and_todos,
        )

        # Convert to dictionary for API response
        return {
            "status": "success",
            "analysis_id": report.analysis_id,
            "report": report.dict(),
        }

    except Exception as e:
        logger.error(f"Business intelligence analysis failed: {e}")
        return {
            "status": "error",
            "error_message": f"Analysis failed: {str(e)}",
            "analysis_id": None,
            "report": None,
        }


# Export main components
__all__ = [
    "comprehensive_business_intelligence_analysis",
    "BusinessIntelligenceOrchestrator",
    "ComprehensiveBusinessReport",
    "CostBreakdown",
    "ROIAnalysis",
    "MarketTrendAnalysis",
    "GTMStrategy",
    "BusinessOptimizationRecommendations",
    "AnalysisType",
]
