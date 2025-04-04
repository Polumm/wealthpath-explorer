import os
from sqlalchemy import create_engine, text

DB_HOST = os.getenv("DATABASE_HOST", "localhost")
DB_USER = os.getenv("DATABASE_USER", "postgres")
DB_PASSWORD = os.getenv("DATABASE_PASSWORD", "mysecretpassword")
DB_NAME = os.getenv("DATABASE_NAME", "assetdb")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
engine = create_engine(DATABASE_URL, echo=False)

with engine.connect() as conn:
    create_table_stmt = text("""
    CREATE TABLE IF NOT EXISTS scenarios (
        id SERIAL PRIMARY KEY,
        label TEXT UNIQUE NOT NULL,
        initial_asset DOUBLE PRECISION,
        annual_income_initial DOUBLE PRECISION,
        invest_fraction DOUBLE PRECISION,
        save_fraction DOUBLE PRECISION,
        consumption_fraction DOUBLE PRECISION,
        annual_return_investment DOUBLE PRECISION,
        annual_return_savings DOUBLE PRECISION,
        income_growth_rate DOUBLE PRECISION,
        inflation_rate DOUBLE PRECISION,
        years INTEGER
    );
    """)
    conn.execute(create_table_stmt)
    conn.commit()


def insert_scenario(params):
    insert_stmt = text("""
    INSERT INTO scenarios (
        label, initial_asset, annual_income_initial, invest_fraction, 
        save_fraction, consumption_fraction, annual_return_investment,
        annual_return_savings, income_growth_rate, inflation_rate, years
    ) VALUES (
        :label, :initial_asset, :annual_income_initial, :invest_fraction,
        :save_fraction, :consumption_fraction, :annual_return_investment,
        :annual_return_savings, :income_growth_rate, :inflation_rate, :years
    ) RETURNING id
    """)
    with engine.connect() as conn:
        result = conn.execute(insert_stmt, params)
        new_id = result.fetchone()[0]
        conn.commit()
    return new_id

def get_all_scenarios():
    select_stmt = text("SELECT * FROM scenarios ORDER BY label ASC")
    with engine.connect() as conn:
        result = conn.execute(select_stmt)
        rows = result.fetchall()
    scenarios = []
    for row in rows:
        scenario_dict = dict(row._mapping)  # or row.items() in older versions
        scenarios.append(scenario_dict)
    return scenarios

def get_scenario_by_label(label):
    select_stmt = text("SELECT * FROM scenarios WHERE label = :lbl")
    with engine.connect() as conn:
        row = conn.execute(select_stmt, {"lbl": label}).fetchone()
    return dict(row._mapping) if row else None

def delete_scenario(scenario_id):
    delete_stmt = text("DELETE FROM scenarios WHERE id = :id")
    with engine.connect() as conn:
        conn.execute(delete_stmt, {"id": scenario_id})
        conn.commit()

def update_scenario(params):
    """
    Expects params with all columns (including 'id'), or we can do an update by label if you prefer.
    We'll do it by ID here.
    """
    update_stmt = text("""
    UPDATE scenarios
    SET
        initial_asset = :initial_asset,
        annual_income_initial = :annual_income_initial,
        invest_fraction = :invest_fraction,
        save_fraction = :save_fraction,
        consumption_fraction = :consumption_fraction,
        annual_return_investment = :annual_return_investment,
        annual_return_savings = :annual_return_savings,
        income_growth_rate = :income_growth_rate,
        inflation_rate = :inflation_rate,
        years = :years
    WHERE id = :id
    """)
    with engine.connect() as conn:
        conn.execute(update_stmt, params)
        conn.commit()
