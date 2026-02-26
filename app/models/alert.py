"""
Alert model — TODO: Implement.

Table: alerts
Columns: id, type (AlertTypeEnum: budget_exhaustion/employee_underperformance/
         financial_anomaly/cash_flow_risk/milestone_delay),
         severity (AlertSeverityEnum: low/medium/high/critical),
         entity_id, entity_type, message, resolved, resolved_by, created_at
Relationships: standalone — references projects or employees
"""

# TODO: Implement this model — see Section 11 and 14.2 of the design document.
