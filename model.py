import numpy as np 

def advanced_asset_model(
    initial_asset: float,
    annual_income_initial: float,
    invest_fraction: float,
    save_fraction: float,
    consumption_fraction: float,
    annual_return_investment: float,
    annual_return_savings: float,
    income_growth_rate: float,
    inflation_rate: float,  # Not used in this nominal-only approach
    years: int
):
    """
    Computes asset accumulation over time, separating out:
      1) Growth from the initial asset (only).
      2) Growth from new income contributions (only), split between investment and savings.
      3) The total of both (investment + savings).

    This version ignores inflation_rate and uses purely nominal returns.
    If you want to handle inflation, see earlier real-return versions.

    Returns
    -------
    t : np.ndarray
        Time steps (0 ... years)
    total_assets : np.ndarray
        Total assets at each time step (investment + savings).
    investment_account : np.ndarray
        Investment account balance at each time step.
    savings_account : np.ndarray
        Savings account balance at each time step.
    incomes : np.ndarray
        Nominal income at each time step (before the split).
    initial_asset_only : np.ndarray
        The portion of assets attributable to the initial lump sum alone.
    income_contribution_only_inv : np.ndarray
        The portion of assets attributable to income contributions in the investment account.
    income_contribution_only_sav : np.ndarray
        The portion of assets attributable to income contributions in the savings account.
    income_contribution_only : np.ndarray
        The total portion of assets attributable to new income contributions (investment + savings).
    """

    # Time array
    t = np.arange(years + 1)

    # Prepare arrays
    investment_account = np.zeros(years + 1)
    savings_account    = np.zeros(years + 1)
    total_assets       = np.zeros(years + 1)
    incomes            = np.zeros(years + 1)
    initial_asset_only = np.zeros(years + 1)
    income_contribution_only_inv = np.zeros(years + 1)
    income_contribution_only_sav = np.zeros(years + 1)
    income_contribution_only     = np.zeros(years + 1)

    # --- Sanitize / clamp some inputs ---
    initial_asset         = max(initial_asset, 0.0)
    annual_income_initial = max(annual_income_initial, 0.0)
    invest_fraction       = np.clip(invest_fraction, 0, 1)
    save_fraction         = np.clip(save_fraction, 0, 1)
    consumption_fraction  = np.clip(consumption_fraction, 0, 1)
    # If you want to enforce invest_fraction + save_fraction + consumption_fraction = 1,
    # do it before calling this function or clamp the remainder.

    # We'll use the nominal returns directly (ignore inflation_rate)
    r_inv = annual_return_investment
    r_sav = annual_return_savings
    r_inc = income_growth_rate

    # --- Initialize (t = 0) ---
    # Split the initial asset between investment vs. savings
    init_invested = initial_asset * invest_fraction
    init_saved    = initial_asset * save_fraction

    investment_account[0] = init_invested
    savings_account[0]    = init_saved
    incomes[0]            = annual_income_initial

    # Assume that the initial asset (lump sum) sits entirely in the investment account,
    # though you could split it if desired.
    initial_asset_only[0] = init_invested + init_saved
    income_contribution_only_inv[0] = 0.0
    income_contribution_only_sav[0] = 0.0
    income_contribution_only[0]     = 0.0
    total_assets[0] = investment_account[0] + savings_account[0]

    # --- Simulation Loop (Years 1..years) ---
    for i in range(1, years + 1):
        # 1) Grow last year's balances by nominal returns
        investment_account[i] = investment_account[i - 1] * (1 + r_inv)
        savings_account[i]    = savings_account[i - 1]    * (1 + r_sav)

        # 2) Income grows nominally
        incomes[i] = incomes[i - 1] * (1 + r_inc)

        # 3) The portion of income not consumed
        leftover = incomes[i] * (1 - consumption_fraction)

        # 4) Split leftover into investment vs. savings contributions
        invest_contrib = leftover * invest_fraction
        save_contrib   = leftover * save_fraction

        # 5) Add new contributions to accounts
        investment_account[i] += invest_contrib
        savings_account[i]    += save_contrib

        # 6) Track the portion from the initial asset alone.
        # For the initial asset, we assume it grows at the investment return rate.
        initial_asset_only[i] = initial_asset_only[i-1] * (1 + r_inv)

        # Track new income contributions separately:
        # Investment contributions grow at r_inv.
        income_contribution_only_inv[i] = (
            income_contribution_only_inv[i-1] * (1 + r_inv) + invest_contrib
        )
        # Savings contributions grow at r_sav.
        income_contribution_only_sav[i] = (
            income_contribution_only_sav[i-1] * (1 + r_sav) + save_contrib
        )
        # The total income contributions is the sum of both.
        income_contribution_only[i] = (
            income_contribution_only_inv[i] + income_contribution_only_sav[i]
        )

        # 7) Sum total assets
        total_assets[i] = investment_account[i] + savings_account[i]

    return (
        t,
        total_assets,
        investment_account,
        savings_account,
        incomes,
        initial_asset_only,
        income_contribution_only_inv,
        income_contribution_only_sav,
        income_contribution_only
    )
