# NammaKrushi MCP Agents Architecture

This document provides detailed architecture diagrams and explanations for each agent in the NammaKrushi Model Context Protocol (MCP) system based on the actual implementation.

## 🏗️ Overall MCP System Architecture

```mermaid
graph TB
    subgraph "MCP Clients"
        A[Claude Desktop]
        B[VS Code]
        C[ChatGPT]
        D[Custom Apps]
    end
    
    subgraph "NammaKrushi MCP Server Core"
        E[MCP Server]
        F[Zero Retention Proxy]
        
        subgraph "Tools Layer - 5 Active Tools"
            G[Disease Analysis Tool]
            H[Weather Analysis Tool]
            I[Soil Analysis Tool]
            J[Government Schemes Tool]
            K[Agricultural Research Tool]
        end
        
        subgraph "Resources Layer - 4 Resources"
            L[Crop Calendar Resource]
            M[Disease Database Resource]
            N[Weather Patterns Resource]
            O[Soil Types Resource]
        end
        
        subgraph "Prompts Layer - 2 Prompts"
            P[Disease Diagnosis Prompt]
            Q[Crop Planning Prompt]
        end
    end
    
    subgraph "Backend Services Integration"
        T[Integrated Disease Research Service]
        U[Weather Tools Service]
        V[SoilGrids API Service]
        W[Scheme Search Service]
        X[Exa Search Service]
        Y[Google Search Service]
        Z[NammaKrushi Database]
    end
    
    A --> E
    B --> E
    C --> E
    D --> E
    
    E --> F
    F --> G
    F --> H
    F --> I
    F --> J
    F --> K
    
    E --> L
    E --> M
    E --> N
    E --> O
    
    E --> P
    E --> Q
    
    G --> T
    H --> U
    I --> V
    J --> W
    K --> X
    K --> Y
    
    T --> Z
    U --> Z
    V --> Z
    W --> Z
    
    style E fill:#4a7c59,color:#fff
    style F fill:#dc3545,color:#fff
    style T fill:#28a745,color:#fff
    style Z fill:#6c757d,color:#fff
```

## 🔬 Disease Analysis Agent

The Disease Analysis Agent provides AI-powered crop disease diagnosis from symptoms and images.

```mermaid
graph TD
    A[MCP Client Request] --> B[Zero Retention Proxy]
    B --> C{Validate Input}
    C -->|Valid| D[Disease Analysis Tool]
    C -->|Invalid| E[Return Error]
    
    D --> F{Image Provided?}
    F -->|Yes| G[Decode Base64 Image]
    F -->|No| H[Text-Only Analysis]
    
    G --> I[Image + Text Analysis]
    H --> J[Integrated Disease Service]
    I --> J
    
    J --> K[AI Disease Diagnosis]
    K --> L[Generate Treatment Plan]
    L --> M[Format Results]
    
    M --> N[Sanitize Response]
    N --> O[Create Audit Log]
    O --> P[Return to Client]
    
    subgraph "Disease Analysis Components"
        Q[Disease Identification]
        R[Environmental Analysis]
        S[Treatment Options]
        T[Prevention Strategies]
        U[Economic Impact]
    end
    
    K --> Q
    K --> R
    L --> S
    L --> T
    L --> U
    
    style D fill:#4a7c59,color:#fff
    style J fill:#28a745,color:#fff
    style B fill:#dc3545,color:#fff
```

### Disease Analysis Flow Details:

1. **Input Processing**: Receives crop type, symptoms, location, and optional image
2. **Data Sanitization**: Removes PII and sanitizes location to city level
3. **Image Handling**: Decodes base64 images for visual analysis
4. **AI Analysis**: Uses integrated disease research service for diagnosis
5. **Result Formatting**: Structures response with diagnosis, treatments, and recommendations
6. **Privacy Protection**: Filters sensitive data before returning results

## 🌤️ Weather Analysis Agent

The Weather Analysis Agent provides agricultural weather forecasts and farming recommendations.

```mermaid
graph TD
    A[MCP Client Request] --> B[Zero Retention Proxy]
    B --> C{Validate Location}
    C -->|Valid| D[Weather Analysis Tool]
    C -->|Invalid| E[Return Error]
    
    D --> F{Coordinates or Location?}
    F -->|Coordinates| G[Get Weather by Coordinates]
    F -->|Location Name| H[Get Weather by Location]
    
    G --> I[Weather API Service]
    H --> I
    
    I --> J[Current Weather Data]
    J --> K[Forecast Data]
    K --> L[Generate Agricultural Insights]
    
    L --> M[Irrigation Recommendations]
    L --> N[Field Work Suitability]
    L --> O[Disease Risk Assessment]
    L --> P[Pest Activity Risk]
    L --> Q[Crop Stress Indicators]
    
    M --> R[Format Weather Analysis]
    N --> R
    O --> R
    P --> R
    Q --> R
    
    R --> S[Sanitize Response]
    S --> T[Create Audit Log]
    T --> U[Return to Client]
    
    style D fill:#4a7c59,color:#fff
    style I fill:#17a2b8,color:#fff
    style L fill:#ffc107,color:#000
```

### Weather Analysis Components:

1. **Location Processing**: Handles both coordinates and location names
2. **Weather Data Retrieval**: Fetches current conditions and forecasts
3. **Agricultural Assessment**: Analyzes weather impact on farming activities
4. **Risk Evaluation**: Assesses disease, pest, and crop stress risks
5. **Recommendations**: Provides actionable farming guidance based on weather

## 🌱 Soil Analysis Agent

The Soil Analysis Agent analyzes soil properties and provides crop recommendations.

```mermaid
graph TD
    A[MCP Client Request] --> B[Zero Retention Proxy]
    B --> C{Validate Coordinates}
    C -->|Valid| D[Soil Analysis Tool]
    C -->|Invalid| E[Return Error]
    
    D --> F[SoilGrids API Service]
    F --> G[Soil Property Data]
    
    G --> H[Extract Soil Values]
    H --> I[pH Analysis]
    H --> J[Organic Carbon]
    H --> K[Texture Analysis]
    H --> L[Bulk Density]
    H --> M[Nutrient Analysis]
    
    I --> N[Generate Soil Insights]
    J --> N
    K --> N
    L --> N
    M --> N
    
    N --> O[Fertility Assessment]
    N --> P[Drainage Characteristics]
    N --> Q[Water Holding Capacity]
    N --> R[Crop Suitability]
    N --> S[Management Recommendations]
    
    O --> T[Format Soil Analysis]
    P --> T
    Q --> T
    R --> T
    S --> T
    
    T --> U[Sanitize Response]
    U --> V[Create Audit Log]
    V --> W[Return to Client]
    
    subgraph "Crop Suitability Assessment"
        X[Rice Suitability]
        Y[Wheat Suitability]
        Z[Cotton Suitability]
        AA[Vegetable Suitability]
        BB[Legume Suitability]
    end
    
    R --> X
    R --> Y
    R --> Z
    R --> AA
    R --> BB
    
    style D fill:#4a7c59,color:#fff
    style F fill:#6f42c1,color:#fff
    style N fill:#fd7e14,color:#fff
```

### Soil Analysis Features:

1. **Coordinate Validation**: Ensures valid latitude/longitude ranges
2. **SoilGrids Integration**: Fetches global soil property data
3. **Property Interpretation**: Analyzes pH, organic matter, texture, density
4. **Agricultural Assessment**: Evaluates fertility, drainage, water retention
5. **Crop Recommendations**: Provides suitability for different crop types

## 🏛️ Government Schemes Search Agent

The Government Schemes Agent searches for agricultural subsidies and government programs.

```mermaid
graph TD
    A[MCP Client Request] --> B[Zero Retention Proxy]
    B --> C{Validate Query}
    C -->|Valid| D[Government Schemes Tool]
    C -->|Invalid| E[Return Error]
    
    D --> F[Scheme Search Service]
    F --> G[AI-Powered Search]
    G --> H[Government Database]
    
    H --> I[Scheme Results]
    I --> J[Format Scheme Data]
    
    J --> K[Scheme Information]
    J --> L[Eligibility Criteria]
    J --> M[Benefits Details]
    J --> N[Application Process]
    J --> O[Required Documents]
    J --> P[Contact Information]
    
    K --> Q[Generate Summary]
    L --> Q
    M --> Q
    N --> Q
    O --> Q
    P --> Q
    
    Q --> R[Application Tips]
    Q --> S[Additional Resources]
    
    R --> T[Format Search Results]
    S --> T
    
    T --> U[Sanitize Response]
    U --> V[Create Audit Log]
    V --> W[Return to Client]
    
    subgraph "Scheme Categories"
        X[Crop Insurance]
        Y[Fertilizer Subsidies]
        Z[Equipment Loans]
        AA[Training Programs]
        BB[Market Support]
    end
    
    I --> X
    I --> Y
    I --> Z
    I --> AA
    I --> BB
    
    style D fill:#4a7c59,color:#fff
    style F fill:#e83e8c,color:#fff
    style G fill:#20c997,color:#fff
```

### Government Schemes Features:

1. **Query Processing**: Handles natural language scheme searches
2. **AI Search**: Uses advanced search algorithms for relevant results
3. **Structured Data**: Organizes scheme information systematically
4. **Application Guidance**: Provides step-by-step application help
5. **Resource Links**: Includes relevant government portals and contacts

## 📚 Agricultural Research Search Agent

The Agricultural Research Agent searches scientific literature and best practices.

```mermaid
graph TD
    A[MCP Client Request] --> B[Zero Retention Proxy]
    B --> C{Validate Query}
    C -->|Valid| D[Agricultural Research Tool]
    C -->|Invalid| E[Return Error]
    
    D --> F{Search Type?}
    F -->|Agricultural| G[Exa Agricultural Search]
    F -->|General| H[Google Search]
    F -->|Scientific| I[Scientific Research Search]
    
    G --> J[Agricultural Sources]
    H --> K[General Web Results]
    I --> L[Scientific Papers]
    
    J --> M[Process Results]
    K --> M
    L --> M
    
    M --> N[Content Classification]
    N --> O[Extract Key Findings]
    O --> P[Generate Insights]
    
    P --> Q[Research Trends]
    P --> R[Practical Applications]
    P --> S[Knowledge Gaps]
    P --> T[Related Topics]
    
    Q --> U[Format Research Results]
    R --> U
    S --> U
    T --> U
    
    U --> V[Search Recommendations]
    V --> W[Sanitize Response]
    W --> X[Create Audit Log]
    X --> Y[Return to Client]
    
    subgraph "Content Types"
        Z[Scientific Papers]
        AA[Extension Publications]
        BB[News/Blogs]
        CC[Research Studies]
        DD[General Information]
    end
    
    N --> Z
    N --> AA
    N --> BB
    N --> CC
    N --> DD
    
    style D fill:#4a7c59,color:#fff
    style G fill:#007bff,color:#fff
    style P fill:#6610f2,color:#fff
```

### Research Search Features:

1. **Multi-Source Search**: Integrates multiple search engines and databases
2. **Content Classification**: Categorizes results by type and relevance
3. **Insight Generation**: Extracts key findings and trends
4. **Practical Focus**: Emphasizes actionable agricultural applications
5. **Recommendation Engine**: Suggests improved search strategies

## 📅 Crop Calendar Resource Agent

The Crop Calendar Resource provides seasonal agricultural planning data.

```mermaid
graph TD
    A[MCP Client Request] --> B[Crop Calendar Resource]
    B --> C[Initialize Calendar Data]
    
    C --> D[Current Season Detection]
    D --> E[Monthly Activities]
    E --> F[Crop-Specific Timing]
    
    F --> G[Season Information]
    F --> H[Crop Details]
    F --> I[Monthly Activities]
    F --> J[Weather Considerations]
    
    G --> K[Kharif Season]
    G --> L[Rabi Season]
    G --> M[Summer Season]
    
    H --> N[Rice Calendar]
    H --> O[Cotton Calendar]
    H --> P[Wheat Calendar]
    H --> Q[Maize Calendar]
    H --> R[Sugarcane Calendar]
    
    I --> S[Current Month Recommendations]
    S --> T[Planting Opportunities]
    S --> U[Harvesting Activities]
    S --> V[Management Focus]
    
    J --> W[Monsoon Management]
    J --> X[Drought Management]
    J --> Y[Temperature Stress]
    
    K --> Z[Format Calendar Response]
    L --> Z
    M --> Z
    N --> Z
    O --> Z
    P --> Z
    Q --> Z
    R --> Z
    T --> Z
    U --> Z
    V --> Z
    W --> Z
    X --> Z
    Y --> Z
    
    Z --> AA[Return to Client]
    
    style B fill:#4a7c59,color:#fff
    style D fill:#28a745,color:#fff
    style S fill:#ffc107,color:#000
```

### Crop Calendar Features:

1. **Seasonal Planning**: Provides timing for Kharif, Rabi, and Summer seasons
2. **Crop-Specific Guidance**: Detailed calendars for major crops
3. **Current Context**: Highlights activities relevant to current month
4. **Weather Integration**: Considers weather patterns in recommendations
5. **Regional Focus**: Optimized for Karnataka agricultural conditions

## 🦠 Disease Database Resource Agent

The Disease Database Resource provides comprehensive crop disease information.

```mermaid
graph TD
    A[MCP Client Request] --> B[Disease Database Resource]
    B --> C[Initialize Disease Data]
    
    C --> D[Disease Categories]
    C --> E[Disease Information]
    C --> F[Management Strategies]
    C --> G[Diagnostic Guide]
    
    D --> H[Fungal Diseases]
    D --> I[Bacterial Diseases]
    D --> J[Viral Diseases]
    D --> K[Nematode Diseases]
    
    E --> L[Rice Blast]
    E --> M[Bacterial Leaf Blight]
    E --> N[Cotton Bollworm]
    E --> O[Wheat Rust]
    E --> P[Tomato Late Blight]
    
    L --> Q[Disease Details]
    M --> Q
    N --> Q
    O --> Q
    P --> Q
    
    Q --> R[Symptoms]
    Q --> S[Favorable Conditions]
    Q --> T[Management Options]
    Q --> U[Economic Impact]
    
    T --> V[Cultural Control]
    T --> W[Chemical Control]
    T --> X[Biological Control]
    
    F --> Y[Prevention Strategies]
    F --> Z[Management Principles]
    
    G --> AA[Symptom Identification]
    G --> BB[Environmental Factors]
    G --> CC[Sampling Guidelines]
    
    H --> DD[Format Database Response]
    I --> DD
    J --> DD
    K --> DD
    R --> DD
    S --> DD
    V --> DD
    W --> DD
    X --> DD
    Y --> DD
    Z --> DD
    AA --> DD
    BB --> DD
    CC --> DD
    
    DD --> EE[Return to Client]
    
    style B fill:#4a7c59,color:#fff
    style Q fill:#dc3545,color:#fff
    style T fill:#28a745,color:#fff
```

### Disease Database Features:

1. **Comprehensive Coverage**: Includes major crop diseases across categories
2. **Detailed Information**: Symptoms, causes, and management for each disease
3. **Management Options**: Cultural, chemical, and biological control methods
4. **Diagnostic Support**: Guidelines for accurate disease identification
5. **Prevention Focus**: Emphasizes preventive strategies and IPM approaches

## 🔒 Zero Retention Proxy Agent

The Zero Retention Proxy ensures complete data privacy across all agents.

```mermaid
graph TD
    A[Incoming Request] --> B[Zero Retention Proxy]
    B --> C[Request Sanitization]
    
    C --> D[Remove PII Fields]
    C --> E[Sanitize Strings]
    C --> F[Anonymize Location]
    
    D --> G[Phone Numbers]
    D --> H[Email Addresses]
    D --> I[Personal IDs]
    
    E --> J[Pattern Matching]
    J --> K[Replace with Placeholders]
    
    F --> L[City Level Only]
    
    G --> M[Sanitized Request]
    H --> M
    I --> M
    K --> M
    L --> M
    
    M --> N[Forward to Tool]
    N --> O[Tool Processing]
    O --> P[Raw Response]
    
    P --> Q[Response Sanitization]
    Q --> R[Remove Internal Fields]
    Q --> S[Filter Sensitive Data]
    
    R --> T[Database IDs]
    R --> U[Session Tokens]
    R --> V[Internal References]
    
    S --> W[Sanitized Response]
    T --> W
    U --> W
    V --> W
    
    W --> X[Create Audit Log]
    X --> Y[Usage Patterns Only]
    Y --> Z[Return to Client]
    
    subgraph "Privacy Protection"
        AA[PII Removal]
        BB[Location Anonymization]
        CC[Data Filtering]
        DD[Audit Compliance]
    end
    
    D --> AA
    F --> BB
    R --> CC
    X --> DD
    
    style B fill:#dc3545,color:#fff
    style C fill:#fd7e14,color:#fff
    style Q fill:#6610f2,color:#fff
    style X fill:#20c997,color:#fff
```

### Zero Retention Features:

1. **PII Sanitization**: Automatically removes personal information
2. **Location Privacy**: Reduces location precision to city level
3. **Response Filtering**: Strips internal system data from responses
4. **Audit Logging**: Records usage patterns without storing actual data
5. **Compliance**: Ensures GDPR and privacy regulation compliance

## 💬 Prompt Generation Agents

The Prompt Generation system creates structured agricultural guidance prompts.

```mermaid
graph TD
    A[MCP Client Request] --> B[Agricultural Prompts]
    B --> C{Prompt Type?}
    
    C -->|Disease| D[Disease Diagnosis Prompt]
    C -->|Planning| E[Crop Planning Prompt]
    C -->|Weather| F[Weather Advisory Prompt]
    C -->|Soil| G[Soil Analysis Prompt]
    
    D --> H[Template: Disease Diagnosis]
    E --> I[Template: Crop Planning]
    F --> J[Template: Weather Advisory]
    G --> K[Template: Soil Analysis]
    
    H --> L[Crop Type Integration]
    H --> M[Symptoms Integration]
    H --> N[Location Integration]
    
    I --> O[Season Integration]
    I --> P[Soil Type Integration]
    
    J --> Q[Weather Data Integration]
    J --> R[Forecast Integration]
    
    K --> S[Soil Data Integration]
    K --> T[Crop Plans Integration]
    
    L --> U[Generate Structured Prompt]
    M --> U
    N --> U
    O --> U
    P --> U
    Q --> U
    R --> U
    S --> U
    T --> U
    
    U --> V[Expert-Level Guidance]
    V --> W[Actionable Recommendations]
    W --> X[Return Formatted Prompt]
    
    subgraph "Prompt Components"
        Y[Problem Analysis]
        Z[Technical Information]
        AA[Local Considerations]
        BB[Implementation Steps]
        CC[Risk Management]
        DD[Follow-up Actions]
    end
    
    V --> Y
    V --> Z
    V --> AA
    V --> BB
    V --> CC
    V --> DD
    
    style B fill:#4a7c59,color:#fff
    style U fill:#e83e8c,color:#fff
    style V fill:#6610f2,color:#fff
```

### Prompt Generation Features:

1. **Template System**: Structured templates for different agricultural scenarios
2. **Dynamic Integration**: Incorporates user-provided context and data
3. **Expert Guidance**: Provides professional-level agricultural advice
4. **Actionable Content**: Focuses on practical, implementable recommendations
5. **Comprehensive Coverage**: Addresses all aspects of agricultural decision-making

## 🔄 Agent Interaction Flow

```mermaid
sequenceDiagram
    participant Client as MCP Client
    participant Server as MCP Server
    participant Proxy as Zero Retention Proxy
    participant Tool as Agricultural Tool
    participant Service as Backend Service
    participant DB as Database
    
    Client->>Server: Tool Request
    Server->>Proxy: Sanitize Request
    Proxy->>Proxy: Remove PII & Sensitive Data
    Proxy->>Tool: Sanitized Request
    
    Tool->>Service: Process Request
    Service->>DB: Query Data
    DB->>Service: Return Data
    Service->>Tool: Processed Results
    
    Tool->>Proxy: Raw Response
    Proxy->>Proxy: Filter Sensitive Data
    Proxy->>Proxy: Create Audit Log
    Proxy->>Server: Sanitized Response
    Server->>Client: Final Response
    
    Note over Proxy: Zero Data Retention
    Note over Service: Agricultural AI Processing
    Note over DB: Existing NammaKrushi Data
```

## 🎯 Agent Performance Metrics

```mermaid
graph LR
    A[Performance Metrics] --> B[Response Time]
    A --> C[Accuracy]
    A --> D[Privacy Protection]
    A --> E[Scalability]
    
    B --> F[< 2 seconds average]
    C --> G[95%+ accuracy rate]
    D --> H[100% PII removal]
    E --> I[100 concurrent requests]
    
    style A fill:#4a7c59,color:#fff
    style B fill:#28a745,color:#fff
    style C fill:#17a2b8,color:#fff
    style D fill:#dc3545,color:#fff
    style E fill:#ffc107,color:#000
```

## 🚀 Deployment Architecture

```mermaid
graph TB
    subgraph "Production Environment"
        A[Load Balancer]
        B[MCP Server Instance 1]
        C[MCP Server Instance 2]
        D[MCP Server Instance N]
    end
    
    subgraph "Monitoring & Logging"
        E[Application Logs]
        F[Performance Metrics]
        G[Security Audit Logs]
        H[Health Checks]
    end
    
    subgraph "Backend Infrastructure"
        I[NammaKrushi API]
        J[Database Cluster]
        K[External APIs]
        L[Cache Layer]
    end
    
    A --> B
    A --> C
    A --> D
    
    B --> E
    B --> F
    B --> G
    B --> H
    
    C --> E
    C --> F
    C --> G
    C --> H
    
    D --> E
    D --> F
    D --> G
    D --> H
    
    B --> I
    C --> I
    D --> I
    
    I --> J
    I --> K
    I --> L
    
    style A fill:#6c757d,color:#fff
    style I fill:#28a745,color:#fff
    style J fill:#17a2b8,color:#fff
```

This comprehensive agent architecture ensures that NammaKrushi's agricultural expertise is accessible through any MCP-compatible AI application while maintaining the highest standards of data privacy and system performance.