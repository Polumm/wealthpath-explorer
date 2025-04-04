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
  - [🐳 Docker Support](#-docker-support)
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

Clone the repo and install dependencies:

```bash
git clone https://github.com/your-username/wealthpath-explorer.git
cd wealthpath-explorer
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## ▶️ Usage

Launch the app locally with:

```bash
python app.py
```

Then navigate to [http://0.0.0.0:8050](http://0.0.0.0:8050) in your browser.

Behind the scenes, this workflow is driven by:

```python
import numpy as np
import plotly.graph_objs as go
from model import advanced_asset_model
```

For each user-defined scenario:
- Inputs are passed to `advanced_asset_model()` to compute total asset values over time.
- The resulting series is plotted with Plotly (`go.Figure`, `go.Scatter`), with differences embedded in hover templates.
- Common parameters across scenarios are extracted and shown as annotations above the chart.
- Dash callbacks dynamically update visuals and form states based on user interaction.

---

## 🧠 Model Design

At the core of the application lies a powerful simulation engine:

```python
from model import advanced_asset_model
```

This function simulates wealth accumulation over time, using:

- **Nominal returns** on both investment and savings accounts
- **Income growth** with controllable fractions directed toward consumption, savings, and investment
- **Time horizon** and **starting age** to determine age-based asset projections

It returns multiple time series including:
- Total asset balance
- Separate investment and savings accounts
- Initial lump-sum growth vs. new income contributions
- Nominal incomes per year

This separation allows for **fine-grained analysis** and traceable sources of asset growth.

> Inflation is accepted as input but currently unused—allowing for future extensions to real-return modeling.

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

You can easily extend or adapt the app:

- `model.py`: modify the accumulation logic, add inflation-adjusted modeling, or include taxes
- `plots.py`: enhance layout or interactivity, e.g., add confidence bands or alternate views
- `database.py`: replace the default database layer or connect to cloud storage

---

## 🐳 Docker Support

You can spin up the full application using Docker:

```bash
docker-compose up --build
```

This launches both the web app and a PostgreSQL container to persist user-defined scenarios. Environment variables and volume mounting are already configured in `docker-compose.yml`.

---

## 🤝 Contributing

Contributions are welcome! Feel free to fork the repo and submit a pull request. For large changes, open an issue first to discuss your ideas with the maintainers.

---

## 📄 License

Licensed under the [Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0).  
You may use, modify, and distribute this software under the terms of that license.

---

> **Developed by Polumm** — empowering financial literacy through interactive simulation.