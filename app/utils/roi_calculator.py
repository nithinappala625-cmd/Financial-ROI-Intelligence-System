"""ROI Calculator Utility functions."""


def calc_roi(revenue: float, cost: float) -> float:
    """ROI = (Revenue - Cost) / Cost * 100"""
    if cost <= 0:
        return 0.0
    return ((revenue - cost) / cost) * 100.0


def calc_margin(revenue: float, cost: float) -> float:
    """Margin = (Revenue - Cost) / Revenue * 100"""
    if revenue <= 0:
        return 0.0
    return ((revenue - cost) / revenue) * 100.0


def calc_burn_rate(total_expenses: float, months_passed: float) -> float:
    """Burn Rate = Total Expenses / Months Passed"""
    if months_passed <= 0:
        return total_expenses
    return total_expenses / months_passed


def calc_evs(contribution_value: float, salary: float) -> float:
    """EVS = Contribution Value / Salary Cost"""
    if salary <= 0:
        return 0.0
    return contribution_value / salary
