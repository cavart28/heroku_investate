import streamlit as st
import pandas as pd


def values_of_series_of_invest(invest_amounts,
                               rate_between_amounts,
                               final_only=True,
                               invest_at_begining_of_period=False):
    """
    Total values after investing each of the values in invest_values, the running total increasing
    by the percentage in rate_between_values from one investment to the next.
    By default invest_at_begining_of_period is set to False meaning that each investment is made
    at the begining of the period and thus is not subject to the period growth.

    :param: invest_values, an iterable of invested values
    :param: rate_between_values, an iterable of rate of growth for the periods from one
                                 investment to the next
    :param: invest_at_begining_of_period, boolean, whether to invest at the begining of a period
            or the end.

    >>> values_of_series_of_invest([1, 1], [0, 0])
    2
    >>> # final_only controls whether to get the intermediate values
    >>> values_of_series_of_invest([1, 1], [0, 0], final_only=False)
    [1, 2]
    >>> # the first rate is not used by default, since the amounts are invested at the END of the period
    >>> values_of_series_of_invest([1, 1], [0.05, 0], final_only=False)
    [1.0, 2.0]
    >>> # this can be changed however, by setting invest_at_begining_of_period to True
    >>> values_of_series_of_invest([1, 1], [0.05, 0], invest_at_begining_of_period=True, final_only=False)
    [1.05, 2.05]
    >>> values_of_series_of_invest([1, 1], [0.05, 0.08], invest_at_begining_of_period=True, final_only=False)
    [1.05, 2.1340000000000003]

    # it can easily be used to get total invested value after several regular investments
    >>> n_years = 10
    >>> rate = 0.08
    >>> yearly_investment = 100
    >>> values_of_series_of_invest([yearly_investment] * n_years, [rate] * n_years)
    1448.656246590984

    # another application is to get the historical growth of a stock from one year to the next
    # to evaluate the total value of a series of investments

    """

    if invest_at_begining_of_period:
        total = invest_amounts.pop(0) * (1 + rate_between_amounts.pop(0))
        value_over_time = [total]
    else:
        total = 0
        value_over_time = []

    for invest, rate in zip(invest_amounts, rate_between_amounts):
        total = total * (1 + rate) + invest
        value_over_time.append(total)

    if final_only:
        return total
    else:
        return value_over_time


def total_of_regular_investment(reg_invest_value, rate, n_periods):
    """
    A special case of total_of_series_of_invest, when the investements are constant and the rate
    remains constant. Uses math formula instead of recursion. Not super useful except may be to
    keep track of the formula for other usage.

    >>> total_of_regular_investment(10, 0, 5)
    50
    # the investment is applied at the END of the period and thus does not benefit from its growth
    >>> total_of_regular_investment(10, 0.01, 1)
    10.0
    >>> total_of_regular_investment(10, 0.01, 2)
    20.099999999999987
    >>> total_of_regular_investment(10, 0.01, 5)
    51.0100501000001
    """

    if rate == 0:
        return reg_invest_value * n_periods
    else:
        factor = 1 + rate
        return reg_invest_value + reg_invest_value * (factor - factor ** n_periods) / (1 - factor)


def compute_mortg_principal(loan_rate=0.04,
                            loan_amount=1000,
                            years_to_maturity=30,
                            n_payment_per_year=12):
    """
    Compute the principal payment of a mortgage

    :param: loan_rate, float, the yearly rate of the mortgage
    :param: loan_amount, float, the initial amount borrowed
    :param: years_to_maturity, float, the number of years to repay the mortgage
    :param: n_payment_per_year, int, the number of payments made in a year assumed at a regular
            interval. Typically this should be left to 12.

    >>> compute_mortg_principal(loan_amount=100000, loan_rate=0.025, years_to_maturity=15)
    666.7892090089922
    """

    if loan_rate == 0:
        return loan_amount / (years_to_maturity * n_payment_per_year)
    else:
        period_rate_factor = 1 + loan_rate / n_payment_per_year
        n_periods = years_to_maturity * n_payment_per_year

        # if we don't pay anything off, the loan amount increases after each month, following this function
        total_loan = loan_amount * period_rate_factor ** n_periods

        # if we place a 1 unit at the END of every month at the same rate as the loan rate, this is what we get:
        invest_value_factor = values_of_series_of_invest([1] * n_periods, [loan_rate / n_payment_per_year] * n_periods)

        # when the loan is paid off, P * invest_value_factor = total_loan so this is the monthly payment:
        return total_loan / invest_value_factor


def compute_equity_and_interest(loan_rate=0.025,
                                loan_amount=240000,
                                years_to_maturity=15,
                                n_payment_per_year=12,
                                initial_equity=0,
                                estate_growth_rate=0):
    """
    Return two series, the first one giving the equity over time and the second the interests paid
    to the lender over time.

    :param: loan_rate, float, the yearly rate of the mortgage
    :param: loan_amount, float, the initial amount borrowed
    :param: years_to_maturity, float, the number of years to repay the mortgage
    :param: n_payment_per_year, int, the number of payments made in a year assumed at a regular
            interval. Typically this should be left to 12.
    :param: initial_equity, float, the amount of initial equity, e.g. downpayment or value of the
            purchase above the paid price
    :param: estate_growth_rate, float, expected yearly increase in real estate value
    """

    principal = compute_mortg_principal(loan_rate,
                                        loan_amount,
                                        years_to_maturity,
                                        n_payment_per_year)
    # initial variable values
    equity = initial_equity
    interest_paid = 0
    remaining_loan = loan_amount
    equity_over_time = [equity]
    interest_paid_over_time = [interest_paid]

    period_interest_factor = loan_rate / n_payment_per_year
    period_estate_growth_factor = 1 + estate_growth_rate / n_payment_per_year

    for period in range(years_to_maturity * n_payment_per_year):
        period_interest = remaining_loan * period_interest_factor
        remaining_loan += period_interest - principal
        interest_paid += period_interest
        equity += principal - period_interest
        equity_over_time.append(equity)
        interest_paid_over_time.append(interest_paid)

    if estate_growth_rate > 0:
        equity_over_time = [equ * period_estate_growth_factor ** (n_period+1) for n_period, equ in
                            enumerate(equity_over_time)]

    return equity_over_time, interest_paid_over_time


def inflation_adjust(month_costs_gen, yearly_infl_rate=0.02):
    """
    Given a list of monthly costs, adjust then for inflation so as to have the actual future
    dollar cost
    """
    for i, cost in enumerate(month_costs_gen):
        yield cost * (1 + yearly_infl_rate / 12) ** i


# TODO: each variable is beneficial or not, take that into account to allow ranges
def house_investment(mortg_rate=0.0275,
                     down_payment_perc=0.2,
                     house_cost=240000,
                     tax=3000,
                     insurance=3000,
                     repair=6000,
                     estate_rate=0.04,
                     mortgage_n_years=15,
                     n_years_after_pay_off=10,
                     monthly_rental_income=6000,
                     percentage_rented=1,
                     inflation_rate=0.02,
                     income_tax=0.35,
                     management_fees_rate=0.22,
                     plot=True):
    """
    Compute two series, one returning the amount of equity and the second the monthly income
    (positive or negative) from renting the house. The income can then be used in the function
    values_of_series_of_invest to emulate its investment in the stock market for example
    """

    n_months_repay = mortgage_n_years * 12
    n_total_months = n_months_repay + n_years_after_pay_off * 12
    loan_amount = house_cost * (1 - down_payment_perc)
    # get the mortgage monthly cost
    monthly_mort_payment = compute_mortg_principal(loan_rate=mortg_rate,
                                                   loan_amount=loan_amount,
                                                   years_to_maturity=mortgage_n_years,
                                                   n_payment_per_year=12)

    # costs are affected by inflation
    # TO DO: Taxes are more affected by the real estate values
    extra_cost_per_month = [(tax + insurance + repair) / 12] * n_total_months
    infl_adj_extra_cost_per_month = inflation_adjust(extra_cost_per_month, inflation_rate)
    # if rented, a percentage of the cost can be deducted from income
    infl_adj_extra_cost_per_month = [cost * (1 - percentage_rented * income_tax)
                                     for cost in infl_adj_extra_cost_per_month]
    # series of total monthly cost
    total_cost_per_month = [cost + monthly_mort_payment * (i <= n_months_repay)
                            for i, cost in enumerate(infl_adj_extra_cost_per_month)]

    # series of rental income
    rental_income = [monthly_rental_income * (1 - management_fees_rate) * percentage_rented
                     * (1 - income_tax) * (1 + estate_rate / 12) ** (i+1)
                     for i in range(n_total_months)]
    # series of monthly balance
    monthly_income = [i[0] - i[1] for i in zip(rental_income, total_cost_per_month)]

    # house values over time
    house_value = [house_cost * (1 + estate_rate / 12) ** (i+1) for i in range(n_total_months)]

    # if nothing were repaid, the loan would follow this
    unrepaid_loan_remaining = [loan_amount * (1 + mortg_rate / 12) ** (i+1) for i in range(n_months_repay)]
    # but we do repay, we can imagine we pay in a different account on the side
    repaid_total = values_of_series_of_invest([monthly_mort_payment] * n_months_repay,
                                              [mortg_rate / 12] * n_months_repay,
                                              final_only=False)
    # and the loan balance is the difference between the "unrepaid loan" and what we amass in the
    # side account
    loan_remaining = [i[0] - i[1] for i in zip(unrepaid_loan_remaining, repaid_total)]
    # adding the extra months, where the loan is fully repaid
    loan_remaining += [0] * (n_total_months - n_months_repay)
    # the equity is the difference between the house value and the remaining loan
    equity = [i[0] - i[1] for i in zip(house_value, loan_remaining)]
    return equity, monthly_income


def compare_house_invest_vs_stock(equity,
                                  monthly_income,
                                  stock_market_rate=0.08,
                                  down_payment_perc=0.1,
                                  house_cost=240000,
                                  plot=True):
    stock_market_month_rate = stock_market_rate / 12

    # total house investment. Note that negative income are counted negatively, which
    # is ok since one could assume that the money spent would have been invested in stock otherwise

    positive_monthly_income = [inc * int(inc > 0) for inc in monthly_income]
    negative_monthly_income = [-inc * int(inc <= 0) for inc in monthly_income]

    house_invest = [i[0] + i[1] for i in zip(equity, values_of_series_of_invest(positive_monthly_income,
                                                                                [stock_market_month_rate] * len(
                                                                                    monthly_income),
                                                                                final_only=False,
                                                                                invest_at_begining_of_period=False))]
    # the same initial investment in stock would yield
    down_payment_invest = [down_payment_perc * house_cost * (1 + stock_market_month_rate) ** (i+1) for i in
                           range(len(monthly_income))]
    invested_negative_monthly_income = values_of_series_of_invest(negative_monthly_income,
                                                                  [stock_market_month_rate] * len(
                                                                      negative_monthly_income),
                                                                  final_only=False,
                                                                  invest_at_begining_of_period=False)
    total_stock_market_invest = [i + j for (i, j) in zip(down_payment_invest, invested_negative_monthly_income)]

    return house_invest, total_stock_market_invest


st.title('House vs other investment')

house_cost = st.sidebar.number_input('House price', value=240000)
down_payment_perc = st.sidebar.number_input('Down payment percentage', value=10) * 0.01
mortg_rate = st.sidebar.number_input('Mortgage rate', value=2.75) * 0.01
mortgage_n_years = st.sidebar.number_input('Mortgage duration in years', value=15)
n_years_after_pay_off = st.sidebar.number_input('Years to display after pay off', value=5)

tax = st.sidebar.number_input('Yearly tax', value=4000)
insurance = st.sidebar.number_input('Yearly insurance cost', value=3000)
repair = st.sidebar.number_input('Yearly repair cost', value=6000)
monthly_rental_income = st.sidebar.number_input('Average monthly rental income', value=7500)
percentage_rented = st.sidebar.number_input('Percentage rented', value=0.5)

estate_rate = st.sidebar.number_input('Yearly real estate market increase', value=3.5) * 0.01
inflation_rate = st.sidebar.number_input('Inflation rate', value=2.1) * 0.01
income_tax = st.sidebar.number_input('Income tax percentage', value=33) * 0.01
management_fees_rate = st.sidebar.number_input('Management fees', value=22) * 0.01
stock_market_rate = st.sidebar.number_input('Yearly rate of other investment', value=8) * 0.01

equity, monthly_income = house_investment(mortg_rate,
                                          down_payment_perc,
                                          house_cost,
                                          tax,
                                          insurance,
                                          repair,
                                          estate_rate,
                                          mortgage_n_years,
                                          n_years_after_pay_off,
                                          monthly_rental_income,
                                          percentage_rented,
                                          inflation_rate,
                                          income_tax,
                                          management_fees_rate,
                                          plot=False)

df = pd.DataFrame()
df['equity'] = equity
df['montlhy_income'] = monthly_income

house_invest, down_payment_invest = compare_house_invest_vs_stock(equity,
                                                                  monthly_income,
                                                                  stock_market_rate=stock_market_rate,
                                                                  down_payment_perc=down_payment_perc,
                                                                  house_cost=house_cost,
                                                                  plot=False)
df['house_investment'] = house_invest
df['stock_investment'] = down_payment_invest

st.line_chart(df['montlhy_income'])
st.line_chart(df['equity'])
st.line_chart(df[['house_investment', 'stock_investment']])
