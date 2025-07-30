# Pychemist

The Alchemist of Data Science

**Transform raw data into insights.**

Pychemist is a lightweight Python library designed to simplify and enrich your data science workflow. Inspired by the transformation mindset of an alchemist, it helps you turn raw data into golden insights. Pychemist replaces complex, repetitive code with a clean and intuitive syntax that streamlines data cleaning, transformation, and preparation to reveal clear insights. It also enables clean and well-structured presentation of results, making it easier to communicate findings effectively.

---

## Features

- Create lagged or lead variables for time-series and panel data
- Run quick, readable t-tests on treatment groups
- Filter model summaries to hide fixed effects
- Conditional mutation of DataFrames
- Pandas accessor (`.pc`) for fluent, chainable workflows

## Installation

```bash
pip install pychemist
```

## Usage
```python
import pychemist as chem
```

# Example 1: Lagging a variable
```python
df = chem.time_shift(dataframe=df, variables=["sales","profit"], id="company", time="year", shift=1)
```

# Example 2: Conditional mutation
```python
df = chem.mutate(df, query_str='division == 24 & managerID==15014', "bonus", 1000)
```

# Example 3: Conditional mutation using the DataFrame accessor
```python
df=df.chem.mutate('company_id == "8ga62sav" & year==2025', "total_assets", 82000000)
```

# Example 4: T-test between treated and control groups
```python
chem.ttest(df, variable="outcome", treatment="treated")
```

# Example 5: Model summary without fixed effects
```python
import statsmodels.formula.api as smf
model = smf.ols("y ~ x + C(firm)", data=df).fit()
print(chem.summary_no_fe(model))
```


MIT License
Copyright (c) Jeroen van Raak (2025)