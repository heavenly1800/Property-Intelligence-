# Entity Relationship Diagram (ERD)

## Core Domain

Property
│
├── belongs to → Market
├── owned by → Person
├── has many → Opportunities
├── has many → AI Analyses
├── has many → Communications
├── has many → Documents
├── has many → Tasks
└── belongs to → Deal

Person
│
├── belongs to → Company
├── has many → Deals
├── has many → Buyer Profiles
├── has many → Seller Profiles
└── has many → Communications

Deal
│
├── belongs to → Property
├── has many → Offers
├── has many → Documents
├── has many → Tasks
└── has many → Timeline Events

Opportunity
│
├── belongs to → Property
├── belongs to → Strategy
├── has many → Buyer Matches
└── has one → AI Analysis

Strategy
│
├── Wholesale
├── Fix & Flip
├── Buy & Hold
├── BRRRR
├── Seller Finance
├── Commercial
├── Development
└── Short-Term Rental

AI Analysis
│
├── belongs to → Property
├── belongs to → Opportunity
└── creates → Recommendations