from datetime import date

from balance_api.models.transactions import get_date_rage, PeriodType, go_back_in_time


def test_models_transactions_get_date_rage_current_month():
    start_date, end_date = get_date_rage(
        period_type=PeriodType.CURRENT_MONTH,
        start_date=None,
        end_date=None
    )

    print(f"Start date: {start_date} - End date: {end_date}")


def test_models_transactions_get_date_rage_last_month():
    start_date, end_date = get_date_rage(
        period_type=PeriodType.LAST_MONTH,
        start_date=None,
        end_date=None
    )

    print(f"Start date: {start_date} - End date: {end_date}")


def test_models_transactions_get_date_rage_current_year():
    start_date, end_date = get_date_rage(
        period_type=PeriodType.CURRENT_YEAR,
        start_date=None,
        end_date=None
    )

    print(f"Start date: {start_date} - End date: {end_date}")


def test_models_transactions_get_date_rage_last_year():
    start_date, end_date = get_date_rage(
        period_type=PeriodType.LAST_YEAR,
        start_date=None,
        end_date=None
    )

    print(f"Start date: {start_date} - End date: {end_date}")


def test_models_transactions_get_date_rage_last_3_months():
    start_date, end_date = get_date_rage(
        period_type=PeriodType.LAST_3_MONTHS,
        start_date=None,
        end_date=None
    )

    print(f"Start date: {start_date} - End date: {end_date}")


def test_models_transactions_get_date_rage_last_6_months():
    start_date, end_date = get_date_rage(
        period_type=PeriodType.LAST_6_MONTHS,
        start_date=None,
        end_date=None
    )

    print(f"Start date: {start_date} - End date: {end_date}")


def test_models_transactions_get_date_rage_last_12_months():
    start_date, end_date = get_date_rage(
        period_type=PeriodType.LAST_12_MONTHS,
        start_date=None,
        end_date=None
    )

    print(f"Start date: {start_date} - End date: {end_date}")


def test_models_transactions_go_back_in_time():
    current_date = date(2023, 2, 12)
    first_day_last_month = go_back_in_time(current_date, 1)

    assert first_day_last_month.day == 1
    assert first_day_last_month.month == 1
    assert first_day_last_month.year == 2023

    first_day_last_2_months = go_back_in_time(current_date, 2)

    assert first_day_last_2_months.day == 1
    assert first_day_last_2_months.month == 12
    assert first_day_last_2_months.year == 2022

    first_day_last_3_months = go_back_in_time(current_date, 3)

    assert first_day_last_3_months.day == 1
    assert first_day_last_3_months.month == 11
    assert first_day_last_3_months.year == 2022
