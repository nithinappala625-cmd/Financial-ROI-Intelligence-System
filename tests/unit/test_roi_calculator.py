from app.utils.roi_calculator import calc_roi, calc_burn_rate, calc_evs, calc_margin


def test_calc_roi():
    # ROI = (Revenue - Cost) / Cost * 100
    assert calc_roi(revenue=150000, cost=100000) == 50.0
    assert calc_roi(revenue=100000, cost=100000) == 0.0
    assert calc_roi(revenue=50000, cost=100000) == -50.0
    # Division by zero protection
    assert calc_roi(revenue=100, cost=0) == 0.0


def test_calc_margin():
    # Margin = (Revenue - Cost) / Revenue * 100
    assert calc_margin(revenue=200000, cost=150000) == 25.0
    assert calc_margin(revenue=100000, cost=150000) == -50.0
    # Division by zero protection
    assert calc_margin(revenue=0, cost=50000) == 0.0


def test_calc_burn_rate():
    # Burn Rate = Expenses / Months
    assert calc_burn_rate(total_expenses=120000, months_passed=6) == 20000.0
    # Division by zero protection returns total_expenses
    assert calc_burn_rate(total_expenses=10000, months_passed=0) == 10000.0


def test_calc_evs():
    # EVS = Contribution Value / Salary Cost
    assert calc_evs(contribution_value=120000, salary=100000) == 1.2
    assert calc_evs(contribution_value=80000, salary=100000) == 0.8
    # Division by zero protection
    assert calc_evs(contribution_value=50000, salary=0) == 0.0
