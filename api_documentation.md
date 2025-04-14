# Loan Prediction System API Documentation

This document provides comprehensive documentation for the Loan Prediction System API, which connects all analytical components together.

## API Overview

The Loan Prediction System API provides endpoints for:
1. Main loan prediction
2. Geographic analysis
3. Time-based analysis
4. Competitive analysis
5. Risk segmentation
6. Financial planning integration

All endpoints accept JSON input and return JSON responses. The API uses session IDs to maintain state between calls, allowing different analytical components to work with the same loan application data.

## Base URL

```
http://[server-address]:5000/api
```

## Authentication

Currently, the API does not require authentication. In a production environment, appropriate authentication mechanisms should be implemented.

## Endpoints

### 1. Predict Loan Approval

**Endpoint:** `/predict`

**Method:** POST

**Description:** Processes loan parameters and returns prediction results.

**Request Body:**
```json
{
  "loan_amount": 10000,
  "interest_rate": 5.0,
  "term": 36,
  "grade": "B",
  "employment_length": 5,
  "annual_income": 60000,
  "dti_ratio": 20,
  "income_verification": "Verified",
  "home_ownership": "MORTGAGE",
  "total_credit_lines": 10,
  "open_credit_lines": 5,
  "mortgage_accounts": 1,
  "paid_principal": 5000,
  "paid_total": 7000
}
```

**Response:**
```json
{
  "session_id": "20250413213000",
  "prediction": 1,
  "probability": 0.85,
  "status": "success"
}
```

### 2. Geographic Analysis

**Endpoint:** `/geographic-analysis`

**Method:** POST

**Description:** Processes location data and returns regional risk assessment.

**Request Body:**
```json
{
  "session_id": "20250413213000",
  "location": "California"
}
```

**Response:**
```json
{
  "region": "California",
  "risk_score": 65.5,
  "unemployment_rate": 4.2,
  "median_income": 75000,
  "housing_price_index": 320.5,
  "approval_rate": 72.3,
  "regional_comparison": {
    "risk_score_percentile": 65,
    "unemployment_percentile": 40,
    "income_percentile": 85,
    "housing_percentile": 90
  },
  "status": "success"
}
```

### 3. Time-Based Analysis

**Endpoint:** `/time-based-analysis`

**Method:** POST

**Description:** Processes loan parameters and returns seasonal trends and forecasts.

**Request Body:**
```json
{
  "session_id": "20250413213000"
}
```

**Response:**
```json
{
  "loan_amount": 10000,
  "term_months": 36,
  "interest_rate": 5.0,
  "monthly_payment": 299.71,
  "total_payment": 10789.56,
  "total_interest": 789.56,
  "current_month": 4,
  "seasonal_factor": 1.05,
  "base_approval_probability": 0.85,
  "adjusted_approval_probability": 0.89,
  "repayment_timeline": [
    {
      "month": 1,
      "payment": 299.71,
      "principal_payment": 257.88,
      "interest_payment": 41.83,
      "remaining_principal": 9742.12
    },
    // Additional months...
  ],
  "seasonal_trends": [
    {
      "month": 1,
      "approval_factor": 0.95
    },
    // Additional months...
  ],
  "status": "success"
}
```

### 4. Competitive Analysis

**Endpoint:** `/competitive-analysis`

**Method:** POST

**Description:** Compares loan terms with market averages and provides alternative lender recommendations.

**Request Body:**
```json
{
  "session_id": "20250413213000"
}
```

**Response:**
```json
{
  "user_loan": {
    "amount": 10000,
    "interest_rate": 5.0,
    "term_months": 36,
    "total_payment": 10789.56,
    "monthly_payment": 299.71
  },
  "market_average": {
    "interest_rate": 5.5,
    "term_months": 36,
    "total_payment": 10872.36,
    "monthly_payment": 302.01
  },
  "comparison": {
    "interest_rate_diff": -0.5,
    "payment_diff": -82.80
  },
  "alternative_lenders": [
    {
      "name": "LenderA",
      "min_grade": "C",
      "avg_interest_rate": 4.8,
      "avg_term": 36,
      "pros": "Low rates, flexible terms",
      "cons": "Strict approval criteria"
    },
    // Additional lenders...
  ],
  "best_lender": {
    "name": "LenderA",
    "interest_rate": 4.8,
    "total_payment": 10745.76,
    "monthly_payment": 298.49,
    "potential_savings": 43.80
  },
  "status": "success"
}
```

### 5. Risk Segmentation

**Endpoint:** `/risk-segmentation`

**Method:** POST

**Description:** Provides detailed risk profiles and tiered categorization.

**Request Body:**
```json
{
  "session_id": "20250413213000"
}
```

**Response:**
```json
{
  "risk_profile": {
    "annual_income": 60000,
    "dti_ratio": 20,
    "credit_grade": "B",
    "custom_score": 75.5
  },
  "risk_tier": {
    "tier": "Medium",
    "default_probability": 0.15,
    "recommended_interest_premium": 1.5,
    "max_loan_amount": 25000
  },
  "borrower_segment": {
    "segment": "middle_income",
    "income_weight": 0.3,
    "dti_weight": 0.5,
    "grade_weight": 0.2
  },
  "recommendation": "Approve",
  "status": "success"
}
```

### 6. Financial Planning

**Endpoint:** `/financial-planning`

**Method:** POST

**Description:** Provides debt consolidation analysis and retirement impact assessment.

**Request Body:**
```json
{
  "session_id": "20250413213000",
  "debt_profile": {
    "credit_card": {"balance": 5000, "interest_rate": 18.0, "min_payment": 150},
    "car_loan": {"balance": 15000, "interest_rate": 6.0, "min_payment": 300},
    "personal_loan": {"balance": 8000, "interest_rate": 10.0, "min_payment": 200}
  }
}
```

**Response:**
```json
{
  "debt_consolidation": {
    "current_debt": {
      "total_balance": 28000,
      "weighted_avg_rate": 9.46,
      "total_min_payment": 650,
      "months_to_debt_free": 60,
      "total_interest": 11000
    },
    "consolidated_debt": {
      "total_balance": 28000,
      "interest_rate": 5.0,
      "monthly_payment": 528.65,
      "months_to_debt_free": 60,
      "total_interest": 3719
    },
    "impact": {
      "monthly_payment_change": 121.35,
      "time_saved": 0,
      "interest_savings": 7281
    }
  },
  "retirement_impact": {
    "monthly_contribution": 60.68,
    "years_to_retirement": 30,
    "projected_growth": 75000
  },
  "financial_health": {
    "debt_to_income_current": 0.13,
    "debt_to_income_consolidated": 0.11,
    "net_worth_projections": [
      {
        "year": 0,
        "net_worth": -28000
      },
      // Additional years...
    ]
  },
  "status": "success"
}
```

## Error Handling

All endpoints return appropriate HTTP status codes:
- 200: Success
- 400: Bad request (invalid parameters)
- 500: Server error

Error responses include a message explaining the error:

```json
{
  "status": "error",
  "message": "Invalid parameter: loan_amount must be a positive number"
}
```

## Using Session IDs

1. First, make a call to `/predict` with all loan parameters
2. The response includes a `session_id`
3. Use this `session_id` in subsequent calls to other endpoints
4. This allows all analytical components to work with the same loan data

## Integration Example

Here's an example of how to integrate all components:

```javascript
// Step 1: Submit loan application and get prediction
const loanData = {
  loan_amount: 10000,
  interest_rate: 5.0,
  term: 36,
  // Other parameters...
};

fetch('/api/predict', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(loanData)
})
.then(response => response.json())
.then(prediction => {
  const sessionId = prediction.session_id;
  
  // Step 2: Get geographic analysis
  return fetch('/api/geographic-analysis', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, location: 'California' })
  });
})
.then(response => response.json())
.then(geoAnalysis => {
  // Process geographic analysis results
  
  // Step 3: Get time-based analysis
  // And so on for other components...
});
```

## Conclusion

This API provides a comprehensive interface for all components of the Loan Prediction System to work together. By using session IDs, different analytical components can share data and provide a unified experience for users.
