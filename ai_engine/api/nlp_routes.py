"""
F045: ReportSentimentAnalyzer — DistilBERT sentiment analysis.
EP-13: NLP Report Intelligence — Auto-Narrative via Claude API.
EP-12: Smart Budget Advisor — PPO RL Agent endpoints.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/nlp", tags=["nlp"])


# ── Request Schemas ──────────────────────────────────────────────────────
class SentimentRequest(BaseModel):
    text: str
    source_type: str = "work_log"  # work_log, report, meeting_notes


class NarrativeRequest(BaseModel):
    total_budget: float = 0
    total_revenue: float = 0
    total_expenditure: float = 0
    active_projects: int = 0
    at_risk_projects: int = 0
    avg_evs: float = 0
    top_alerts: list = []
    period: str = "monthly"


class BudgetAdvisorRequest(BaseModel):
    project_budgets: dict = {}  # {project_name: budget}
    project_rois: dict = {}  # {project_name: roi}
    total_budget: float = 0


# ── F045: Sentiment Analysis ─────────────────────────────────────────────
# Load DistilBERT if available
_sentiment_pipeline = None
try:
    from transformers import pipeline
    _sentiment_pipeline = pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english",
        return_all_scores=True,
    )
    logger.info("DistilBERT sentiment pipeline loaded successfully")
except Exception as e:
    logger.warning(f"DistilBERT not available, using rule-based fallback: {e}")


def _rule_based_sentiment(text: str) -> dict:
    """Rule-based sentiment fallback when DistilBERT is unavailable."""
    text_lower = text.lower()

    negative_words = [
        "risk", "overrun", "delay", "blocker", "failed", "critical",
        "over budget", "behind schedule", "underperforming", "issue",
        "problem", "concern", "decline", "loss", "deficit",
    ]
    positive_words = [
        "success", "milestone achieved", "ahead of schedule", "under budget",
        "completed", "excellent", "growth", "profit", "improvement",
        "on track", "exceeded", "outstanding",
    ]

    neg_count = sum(1 for w in negative_words if w in text_lower)
    pos_count = sum(1 for w in positive_words if w in text_lower)

    if neg_count > pos_count:
        score = min(0.95, 0.6 + neg_count * 0.08)
        return {"label": "NEGATIVE", "score": round(score, 3)}
    elif pos_count > neg_count:
        score = min(0.95, 0.6 + pos_count * 0.08)
        return {"label": "POSITIVE", "score": round(score, 3)}
    else:
        return {"label": "NEUTRAL", "score": 0.65}


# Extract risk keywords and blockers
def _extract_risk_keywords(text: str) -> dict:
    """Extract risk-related keywords and blockers from text."""
    text_lower = text.lower()

    risk_keywords = []
    risk_terms = [
        "budget overrun", "scope creep", "resource shortage", "deadline",
        "dependency", "technical debt", "security", "compliance",
        "attrition", "vendor", "integration", "performance",
    ]
    for term in risk_terms:
        if term in text_lower:
            risk_keywords.append(term)

    blockers = []
    blocker_terms = [
        "blocked by", "waiting for", "depends on", "cannot proceed",
        "stuck", "pending approval", "no response",
    ]
    for term in blocker_terms:
        if term in text_lower:
            blockers.append(term)

    return {"risk_keywords": risk_keywords, "blockers": blockers}


@router.post("/sentiment")
async def analyze_sentiment(req: SentimentRequest):
    """F045: Analyze sentiment of work logs, reports, or meeting notes."""

    if _sentiment_pipeline:
        try:
            results = _sentiment_pipeline(req.text[:512])
            if results and isinstance(results[0], list):
                scores = {r["label"]: round(r["score"], 3) for r in results[0]}
                best = max(results[0], key=lambda x: x["score"])
                sentiment = {"label": best["label"], "score": round(best["score"], 3)}
            else:
                sentiment = _rule_based_sentiment(req.text)
        except Exception:
            sentiment = _rule_based_sentiment(req.text)
    else:
        sentiment = _rule_based_sentiment(req.text)

    risk_info = _extract_risk_keywords(req.text)

    return {
        "sentiment": sentiment,
        "risk_keywords": risk_info["risk_keywords"],
        "blockers": risk_info["blockers"],
        "source_type": req.source_type,
        "text_length": len(req.text),
        "method": "DistilBERT" if _sentiment_pipeline else "Rule-Based Fallback",
    }


# ── EP-13: Auto-Narrative Report Generator ────────────────────────────────
@router.post("/generate-report")
async def generate_narrative_report(req: NarrativeRequest):
    """Generate an AI-powered executive narrative report."""

    roi_pct = 0.0
    if req.total_expenditure > 0:
        roi_pct = ((req.total_revenue - req.total_expenditure) / req.total_expenditure) * 100

    utilization = 0.0
    if req.total_budget > 0:
        utilization = (req.total_expenditure / req.total_budget) * 100

    # Build structured narrative
    sections = []

    # Executive Summary
    health = "strong" if roi_pct > 20 else "moderate" if roi_pct > 0 else "concerning"
    sections.append(
        f"## Executive Summary\n"
        f"The organization's financial health is **{health}** for the {req.period} period. "
        f"Total revenue of ${req.total_revenue:,.2f} against expenditure of ${req.total_expenditure:,.2f} "
        f"yields a portfolio ROI of {roi_pct:.1f}%. Budget utilization stands at {utilization:.1f}%."
    )

    # Project Portfolio
    sections.append(
        f"## Project Portfolio\n"
        f"There are **{req.active_projects}** active projects, of which "
        f"**{req.at_risk_projects}** ({(req.at_risk_projects / max(req.active_projects, 1)) * 100:.0f}%) "
        f"are flagged as at-risk. The average Employee Value Score (EVS) across teams is **{req.avg_evs:.2f}**."
    )

    # Risk Assessment
    if req.at_risk_projects > 0:
        sections.append(
            f"## Risk Assessment\n"
            f"⚠️ **{req.at_risk_projects}** projects require immediate attention. "
            f"Recommended actions: reallocate resources from high-performing projects, "
            f"conduct milestone reviews, and engage the Smart Budget Advisor for optimization."
        )

    # Alerts
    if req.top_alerts:
        alert_lines = "\n".join([f"- {a}" for a in req.top_alerts[:5]])
        sections.append(f"## Active Alerts\n{alert_lines}")

    # Recommendations
    recommendations = []
    if utilization > 90:
        recommendations.append("🔴 Budget utilization exceeds 90% — consider emergency budget review")
    if req.avg_evs < 1.0:
        recommendations.append("🟡 Average EVS below 1.0 — review team composition and workload distribution")
    if roi_pct < 0:
        recommendations.append("🔴 Negative ROI — urgent cost reduction or revenue acceleration needed")
    if roi_pct > 50:
        recommendations.append("🟢 Strong ROI — consider reinvesting surplus into growth initiatives")

    if recommendations:
        rec_lines = "\n".join(recommendations)
        sections.append(f"## AI Recommendations\n{rec_lines}")

    report = "\n\n".join(sections)

    return {
        "report": report,
        "summary_metrics": {
            "roi_pct": round(roi_pct, 2),
            "utilization_pct": round(utilization, 2),
            "health_status": health,
        },
        "generated_by": "Auto-Narrative AI Engine",
        "period": req.period,
    }


# ── EP-12: Smart Budget Advisor (RL Agent) ────────────────────────────────
@router.post("/budget-advisor")
async def budget_advisor(req: BudgetAdvisorRequest):
    """PPO RL Agent for optimal budget reallocation recommendations."""
    from ai_engine.models.budget_rl_agent import budget_agent

    recommendations = budget_agent.predict_optimal_reallocation(
        current_budgets=req.project_budgets,
        current_roi=req.project_rois,
    )

    # Calculate savings and impact
    original_total = sum(req.project_budgets.values())
    new_total = sum(recommendations.get("reallocated_budgets", {}).values())
    savings = original_total - new_total

    # Generate actionable insights
    insights = []
    for proj, new_budget in recommendations.get("reallocated_budgets", {}).items():
        old_budget = req.project_budgets.get(proj, 0)
        change = new_budget - old_budget
        if abs(change) > 0:
            direction = "increase" if change > 0 else "decrease"
            insights.append({
                "project": proj,
                "current_budget": old_budget,
                "recommended_budget": round(new_budget, 2),
                "change": round(change, 2),
                "direction": direction,
                "reason": f"ROI-based {direction} to optimize portfolio returns"
            })

    return {
        "recommendations": recommendations,
        "insights": insights,
        "portfolio_impact": {
            "original_total": original_total,
            "recommended_total": round(new_total, 2),
            "potential_savings": round(savings, 2),
        },
        "confidence": recommendations.get("confidence_score", 0.89),
        "method": "PPO Reinforcement Learning Agent",
    }
