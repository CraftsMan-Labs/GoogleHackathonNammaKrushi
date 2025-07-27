# Multi-Agent Crop Disease Research System

A comprehensive AI-powered system for deep research and analysis of crop diseases using multiple specialized agents. This system follows the multi-agent research pattern inspired by Anthropic's engineering approach for thorough disease diagnosis, environmental correlation, treatment recommendations, and yield impact analysis.

## 🏗️ System Architecture

### Multi-Agent Design

The system consists of 7 specialized agents coordinated by an orchestrator:

1. **Disease Identification Agent** - Analyzes images and symptoms
2. **Environmental Analysis Agent** - Correlates soil and weather factors
3. **Research Agent** - Conducts deep research using Exa search
4. **Treatment Recommendation Agent** - Provides cure procedures
5. **Yield Impact Analysis Agent** - Assesses economic implications
6. **Daily Log & Todo Integration Agent** - Creates daily logs and todo tasks
7. **Orchestrator Agent** - Coordinates all agents and compiles reports

### Key Features

- 🔬 **Image Analysis**: Gemini Vision for crop disease identification
- 🌍 **Environmental Correlation**: Soil and weather factor analysis
- 📚 **Deep Research**: Exa search for scientific literature and treatments
- 💊 **Treatment Recommendations**: Detailed cure procedures and sources
- 📊 **Yield Impact**: Economic analysis and loss predictions
- 🛡️ **Prevention Strategies**: Proactive disease management
- 🌦️ **Weather Generation**: Realistic data for top 10 agricultural cities
- 📋 **Structured Output**: Comprehensive reports with confidence scores
- 📝 **Daily Log Integration**: Automatic daily log entries for disease analysis
- ✅ **Todo Management**: Automated task creation for treatments and monitoring
- 🔐 **Authentication**: Secure access with user and crop ownership verification
- 🔄 **Workflow Integration**: Seamless connection with existing farm management

## 🚀 Usage

### Basic API Usage

```python
from src.app.services.deep_research.deep_research_diseaase import deep_research_disease_analysis

# Analyze disease with symptoms and image
result = await deep_research_disease_analysis(
    image_data=image_bytes,  # Optional crop image
    symptoms_text="Yellow spots on leaves, wilting",
    crop_type="tomato",
    location="Bangalore",
    soil_data={
        "ph": 6.2,
        "organic_matter": 2.1,
        "nitrogen": "low"
    }
)
```

### REST API Endpoints

#### Text-based Analysis with Integration
```bash
POST /api/disease-research/analyze
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
    "symptoms_text": "Yellow spots on leaves, wilting, brown edges",
    "crop_type": "tomato",
    "location": "Bangalore",
    "crop_id": 123,
    "create_logs_and_todos": true,
    "soil_data": {
        "ph": 6.2,
        "organic_matter": 2.1
    }
}
```

#### Image-based Analysis with Integration
```bash
POST /api/disease-research/analyze-with-image
Authorization: Bearer <jwt_token>
Content-Type: multipart/form-data

crop_type: tomato
symptoms_text: Yellow spots on leaves
location: Bangalore
crop_id: 123
create_logs_and_todos: true
image: [crop_image.jpg]
```

## 📊 Output Structure

### Comprehensive Disease Report

```json
{
    "analysis_id": "disease_analysis_20241227_143022",
    "timestamp": "2024-12-27T14:30:22",
    "crop_type": "tomato",
    "location": "Bangalore",
    
    "disease_identification": {
        "disease_name": "Bacterial Leaf Spot",
        "scientific_name": "Xanthomonas campestris",
        "confidence": "medium",
        "confidence_score": 0.75,
        "symptoms_observed": ["leaf spots", "yellowing", "wilting"],
        "affected_plant_parts": ["leaves", "stems"],
        "severity": "moderate"
    },
    
    "environmental_analysis": {
        "soil_ph_impact": "Acidic soil increases susceptibility",
        "moisture_conditions": "High moisture favors pathogen growth",
        "temperature_range": "Optimal development at 25-30°C",
        "humidity_impact": "High humidity promotes spore germination",
        "nutrient_deficiencies": ["nitrogen deficiency"],
        "environmental_stress_factors": ["waterlogging", "poor drainage"]
    },
    
    "weather_correlation": {
        "location": "Bangalore",
        "temperature_avg": 22.5,
        "humidity": 72.3,
        "rainfall": 85.2
    },
    
    "research_findings": {
        "disease_causes": ["bacterial pathogen", "environmental stress"],
        "pathogen_lifecycle": "Overwinters in soil debris",
        "spread_mechanisms": ["water splash", "wind dispersal"],
        "host_range": ["tomato", "pepper", "eggplant"],
        "research_sources": ["extension.org", "icar.org.in"],
        "recent_developments": ["new resistant varieties"]
    },
    
    "treatment_options": [
        {
            "treatment_name": "Copper-based Fungicide",
            "treatment_type": "chemical",
            "active_ingredients": ["copper sulfate"],
            "application_method": "Foliar spray",
            "dosage": "2-3 grams per liter",
            "frequency": "Every 7-10 days",
            "timing": "Early morning or evening",
            "cost_estimate": "₹200-300 per acre",
            "availability": "Local agricultural stores",
            "effectiveness": 0.8,
            "side_effects": ["may cause leaf burn if overused"]
        }
    ],
    
    "prevention_strategies": [
        {
            "strategy_name": "Crop Rotation",
            "description": "3-4 year rotation with non-host crops",
            "implementation_steps": ["Plan rotation sequence", "Avoid susceptible crops"],
            "timing": "Before next planting season",
            "cost": "₹500-1000 per acre",
            "effectiveness": 0.8
        }
    ],
    
    "yield_impact": {
        "potential_yield_loss": 15.0,
        "economic_impact": "Moderate impact, treatment recommended",
        "quality_impact": "Some reduction in crop quality",
        "recovery_timeline": "3-4 weeks with treatment",
        "mitigation_potential": 0.7
    },
    
    "executive_summary": "Analysis identified Bacterial Leaf Spot with medium confidence...",
    "immediate_actions": [
        "Apply copper-based fungicide immediately",
        "Improve field drainage",
        "Remove infected plant material"
    ],
    "long_term_recommendations": [
        "Implement crop rotation",
        "Use resistant varieties",
        "Establish monitoring protocols"
    ],
    "confidence_overall": 0.72,
    
    "daily_log_id": 456,
    "todo_ids": [789, 790, 791, 792, 793],
    "integration_status": "completed"
}
```

## 🔧 Configuration

### Environment Variables

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key

# Optional (for enhanced research)
EXA_API_KEY=your_exa_api_key
```

### Dependencies

```bash
# Core dependencies
pip install google-generativeai
pip install exa_py
pip install pydantic
pip install fastapi
pip install pillow

# Or install from requirements
pip install -r requirements.txt
```

## 🧪 Testing

Run the test script to verify system functionality:

```bash
python test_disease_research.py
```

### Test Cases Included

1. **Text-based Analysis**: Symptom description with soil data
2. **Multi-crop Support**: Different crops and locations
3. **Error Handling**: Graceful fallbacks for invalid inputs
4. **Weather Generation**: Realistic data for Indian cities

## 🌟 Advanced Features

### Realistic Weather Data Generation

The system generates realistic weather data for top 10 agricultural cities in India:

- Bangalore, Pune, Hyderabad, Chennai, Coimbatore
- Mysore, Salem, Madurai, Tirupur, Erode

Weather patterns include:
- Temperature ranges specific to each city
- Seasonal humidity variations
- Realistic rainfall patterns
- Wind speed and atmospheric pressure

### Multi-Modal Analysis

- **Image Processing**: Gemini Vision for visual disease identification
- **Text Analysis**: Natural language processing of symptom descriptions
- **Data Integration**: Combines soil, weather, and crop data
- **Research Synthesis**: Aggregates information from multiple sources

### Confidence Scoring

The system provides confidence scores at multiple levels:
- Disease identification confidence (0-1)
- Treatment effectiveness scores (0-1)
- Prevention strategy effectiveness (0-1)
- Overall analysis confidence (weighted average)

## 🔍 Research Capabilities

### Exa Search Integration

The research agent uses Exa search to find:
- Scientific literature on disease causes
- Treatment efficacy studies
- Prevention strategy research
- Recent developments in crop protection

### Trusted Sources

Research focuses on authoritative domains:
- extension.org (Agricultural extension)
- icar.org.in (Indian Council of Agricultural Research)
- fao.org (Food and Agriculture Organization)
- usda.gov (US Department of Agriculture)
- Scientific journals and research publications

## 📈 Yield Impact Analysis

### Economic Assessment

- Potential yield loss percentages
- Cost-benefit analysis of treatments
- Market value impact predictions
- Recovery timeline estimates

### Factors Considered

- Disease severity levels
- Environmental stress factors
- Treatment availability and effectiveness
- Crop type and growth stage
- Regional market conditions

## 🛡️ Prevention Strategies

### Integrated Approach

- **Cultural Practices**: Crop rotation, sanitation
- **Biological Control**: Beneficial microorganisms
- **Chemical Prevention**: Targeted applications
- **Environmental Management**: Soil and water optimization

### Implementation Guidance

- Step-by-step procedures
- Timing recommendations
- Cost estimates
- Effectiveness ratings

## 🚨 Error Handling

### Robust Fallbacks

- Graceful degradation when APIs fail
- Default recommendations for unknown diseases
- Fallback weather data generation
- Comprehensive error logging

### Validation

- Input parameter validation
- Image format verification
- Data consistency checks
- Confidence threshold management

## 🔄 Daily Log & Todo Integration

### Automated Daily Log Creation

The system automatically creates detailed daily log entries when disease analysis is performed:

```json
{
    "activity_type": "disease_analysis",
    "log_date": "2024-12-27",
    "activity_details": {
        "analysis_id": "disease_analysis_20241227_143022",
        "disease_identified": "Bacterial Leaf Spot",
        "confidence": "medium",
        "severity": "moderate",
        "treatment_options_count": 3,
        "yield_impact": 15.0
    },
    "diseases_noted": "Bacterial Leaf Spot",
    "disease_spotted": true,
    "ai_insights": "Analysis identified Bacterial Leaf Spot...",
    "ai_recommendations": ["Apply copper-based fungicide", "Improve drainage"]
}
```

### Automated Todo Task Generation

The system creates structured todo tasks based on analysis results:

#### Immediate Action Tasks (Due: Next Day)
- High priority tasks for urgent treatment
- Specific action items from analysis recommendations

#### Treatment Tasks (Due: 2-3 Days)
- Detailed treatment procedures with dosages
- Application methods and timing
- Cost estimates and supplier information

#### Prevention Tasks (Due: 1 Week)
- Long-term prevention strategies
- Implementation steps and timelines
- Cost-benefit analysis

#### Monitoring Tasks (Recurring Weekly)
- Progress tracking and symptom monitoring
- Photo documentation reminders
- Recovery timeline checkpoints

### Integration Benefits

- **Seamless Workflow**: From analysis to actionable tasks
- **Historical Tracking**: Complete disease management history
- **Progress Monitoring**: Automated follow-up scheduling
- **Treatment Compliance**: Structured task management
- **Economic Planning**: Cost tracking and budgeting

### Authentication & Security

- **JWT Authentication**: Secure API access
- **Crop Ownership Verification**: Users can only analyze their own crops
- **Data Privacy**: User-specific daily logs and todos
- **Audit Trail**: Complete activity tracking

## 🔮 Future Enhancements

### Planned Features

1. **Database Integration**: Store and retrieve analysis history
2. **Machine Learning**: Improve accuracy with usage data
3. **Real-time Monitoring**: IoT sensor integration
4. **Mobile App**: Farmer-friendly interface
5. **Multilingual Support**: Local language translations
6. **Expert Network**: Connect with agricultural specialists

### Scalability

- Microservice architecture ready
- Async processing for large-scale deployment
- Caching for improved performance
- Load balancing support

## 📞 Support

For technical support or feature requests:
- Check the API documentation at `/docs`
- Review the health check endpoint at `/api/disease-research/health`
- Consult the service info at `/api/disease-research/info`

## 📄 License

This system is part of the Namma Krushi agricultural assistant platform.

---

**Built with ❤️ for Karnataka farmers using cutting-edge AI technology**