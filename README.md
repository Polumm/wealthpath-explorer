# 💼 WealthPath Explorer

**WealthPath Explorer** is an interactive financial modeling dashboard designed to simulate and compare personalized life asset accumulation paths. Built with [Dash](https://dash.plotly.com/), [Plotly](https://plotly.com/), and [NumPy](https://numpy.org/), it offers a highly visual way to explore how income, savings, investment, and spending decisions shape long-term wealth.

---

## 📚 Table of Contents

- [💼 WealthPath Explorer](#-wealthpath-explorer)
  - [📚 Table of Contents](#-table-of-contents)
  - [🚀 Features](#-features)
  - [🛠 Installation](#-installation)
  - [▶️ Usage](#️-usage)
  - [🧠 Model Design](#-model-design)
  - [📁 Project Structure](#-project-structure)
  - [🧰 Customization](#-customization)
  - [🤝 Contributing](#-contributing)
  - [📄 License](#-license)

---

## 🚀 Features

- 📊 **Interactive Asset Simulations**  
  Visualize compound growth of assets across multiple financial scenarios with hover insights and real-time updates.

- 🧠 **Scenario Breakdown**  
  Compare outcomes like final age and asset value, and understand how each parameter influences the trajectory.

- 🛠 **Flexible Form-Based Input**  
  Enter initial assets, income, savings/investment/consumption fractions, and returns—all from a clean UI.

- 📉 **Dynamic Plot & Table Sync**  
  Toggling scenario visibility dynamically updates both the chart and comparison table.

- 🧮 **Parameter Differentiation Logic**  
  Automatically highlights shared vs. differing inputs across active scenarios.

---

## 🛠 Installation

Clone the repository:

```bash
git clone https://github.com/your-username/wealthpath-explorer.git
cd wealthpath-explorer
```

---

## ▶️ Usage

To start the app locally via Docker:

```bash
./build.sh
```

This launches:
- A Dash web app for simulation and visualization
- A PostgreSQL container to persist user-defined scenarios

Environment variables and volume mappings are pre-configured in `docker-compose.yml`.

---

In code, the workflow uses:

```python
import numpy as np
import plotly.graph_objs as go
from model import advanced_asset_model
```

For each scenario:
- Inputs are passed to `advanced_asset_model()` to compute year-by-year asset trajectories.
- A Plotly figure displays results with interactive hover templates.
- Common parameters across scenarios are extracted and displayed.
- Dash callbacks handle updates from the user interface in real time.

---

## 🧠 Model Design

At the core of the application lies a powerful simulation engine:

```python
from model import advanced_asset_model
```

This function models:

- **Growth from initial assets**
- **Ongoing contributions from income**, split between investing and saving
- **Nominal returns** on investment and savings
- **Customizable time horizon** and **starting age**

Returns include:

- `total_assets`: total net worth across time
- `investment_account` and `savings_account`: tracked separately
- `initial_asset_only` and `income_contribution_only`: helpful for decomposition
- `incomes`: nominal income per year

> *Note: Inflation is accepted as input but not applied in current calculations.*

---

## 📁 Project Structure

```bash
wealthpath-explorer/
├── app.py                # Main Dash app
├── plots.py              # Plotly layout, scenario comparison logic
├── model.py              # Core simulation model
├── database.py           # CRUD operations for scenarios
├── utils.py              # Helper parsing / formatting utilities
├── requirements.txt      # Python dependencies
├── docker-compose.yml    # Docker configuration
├── Dockerfile            # Container build file
└── README.md             # Project documentation
```

---

## 🧰 Customization

You can tailor the app to your needs:

- `model.py`: adjust assumptions, returns, or structure of the simulation
- `plots.py`: add more metrics, adjust hover logic, or change the layout
- `database.py`: switch from in-memory or file-based to a cloud database

---

## 🤝 Contributing

We welcome contributions!  
Fork the repo and submit a pull request, or open an issue to start a discussion.

---

## 📄 License

Licensed under the [Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0).  
