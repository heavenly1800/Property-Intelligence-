class PropertyIntelligence(BaseModel):
    property: dict
    workflow: dict | None = None
    research: ResearchResult | None = None
    decision: dict | None = None
    buyer: dict | None = None
    offer: dict | None = None
    metadata: dict = Field(default_factory=dict)