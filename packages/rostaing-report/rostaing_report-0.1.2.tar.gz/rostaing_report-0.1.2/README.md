## Rostaing Report, created by Davila Rostaing.

**rostaing-report** is a powerful yet easy-to-use Python package designed to dramatically accelerate the Exploratory Data Analysis (EDA) process. In just one line of code, it generates a complete and beautifully formatted report from a Pandas DataFrame, covering everything from descriptive statistics to key inferential tests.

This toolkit is built for **Data Scientists** and **Data Analysts** who need to gain a deep, initial understanding of their data quickly and efficiently. By providing a holistic view of variable types, distributions, missing values, outliers, and correlations, **rostaing-report** empowers you to make informed, data-driven decisions about feature engineering, modeling strategy, and data cleaning priorities.

## Key Features

-   **📊 Detailed Overview:** Get a bird's-eye view of your dataset, including row/column counts, memory usage, duplicate rows, and a clear breakdown of variable types.
-   **🔢 In-depth Numerical Analysis:** For each numerical column, instantly see statistics like mean, standard deviation, quantiles, variance, skewness, kurtosis, standard error, and outlier detection.
-   **🔠 Insightful Categorical Analysis:** Understand your categorical variables with counts, unique values, top occurrences, and frequencies.
-   **🔗 Smart Correlation Analysis:** Instead of a giant matrix, view a clean, sorted table of the most significant variable correlations, complete with a plain-English interpretation (e.g., "Strong Positive Correlation").
-   **🧪 Built-in Statistical Tests:** Perform common inferential statistics tests directly from your EDA object, including:
    -   Normality Tests (Shapiro-Wilk, Jarque-Bera, **D'Agostino & Pearson**)
    -   **Goodness-of-fit Test (Kolmogorov-Smirnov)** to check if data follows a specific distribution.
    -   Independence Test (Chi-squared)
    -   Group Comparison Tests (T-test, Mann-Whitney U, Kruskal-Wallis)
-   **✨ Beautiful & Flexible Display:** The report is automatically rendered as a stylish HTML table in notebooks (Jupyter, VS Code) and as a clean, readable text table in terminals.

## Installation

Install the package from PyPI with a single command:

```bash
pip install rostaing-report
```

## Quick Start

Getting a full data profile is as simple as this:

```python
import pandas as pd
import numpy as np
from rostaing import rostaing_report

# 1. Create a sample DataFrame
data = {
    'product_id': range(100),
    'price': np.random.normal(150, 40, 100).round(2),
    'customer_age': np.random.normal(35, 8, 100).astype(int),
    'category': np.random.choice(['Electronics', 'Books', 'Home Goods', 'Apparel'], 100),
    'rating': np.random.choice([1, 2, 3, 4, 5, np.nan], 100, p=[0.05, 0.05, 0.1, 0.3, 0.4, 0.1]),
    'is_member': np.random.choice([True, False], 100)
}
df = pd.DataFrame(data)

# 2. Generate the full EDA report
report = rostaing_report(df)

# 3. Display the report
# In a Jupyter Notebook or similar environment, just run:
# report

# In a standard Python script or terminal, use print():
print(report)
```

## In-Depth Usage

Beyond the main report, you can access powerful statistical methods directly.

### The Main Report Breakdown

The `rostaing_report(df)` object provides several detailed sections:

-   **Overview Statistics:** Key metrics about the entire dataset.
-   **Variable Types:** A summary table of all data types (`int64`, `float64`, `object`, etc.) and their counts.
-   **Numerical Variables Analysis:** A deep dive into each number-based column. The `has_outliers` column (based on the IQR method) is especially useful for spotting anomalies.
-   **Categorical Variables Analysis:** A summary of all text-based, boolean, or categorical columns.
-   **Top Correlations:** A sorted list of the most correlated numerical variables, making it easy to spot multicollinearity or interesting relationships. The `interpretation` column saves you time.

### Performing Statistical Tests

Validate your hypotheses directly from the `report` object.

#### 1. Test for Normality
Check if a variable follows a normal distribution.

```python
# H0: The 'price' data is drawn from a normal distribution.
# Use test='shapiro', 'normaltest', or 'jarque_bera'.
normality_results = report.normality_test('price', test='normaltest')
print(pd.Series(normality_results))

# Output:
# test                       D'Agostino & Pearson's test
# column                                           price
# statistic                                     0.478335
# p_value                                       0.787285
# conclusion (alpha=0.05)    The null hypothesis (normality) cannot be r...
# dtype: object
```

#### 2. Test for Goodness-of-Fit (Kolmogorov-Smirnov)
Check if your data conforms to a specific theoretical distribution, like the normal distribution (`'norm'`).

```python
# H0: The 'price' data follows a normal ('norm') distribution.
ks_results = report.ks_test('price', dist='norm')
print(pd.Series(ks_results))

# Output:
# test                       Kolmogorov-Smirnov Test
# column                                       price
# distribution_tested                           norm
# statistic                                 0.081123
# p_value                                   0.518872
# conclusion (alpha=0.05)    The data may follow a 'norm' distribution (p...
# dtype: object
```

#### 3. Test for Independence (Categorical Variables)
Check if two categorical variables are independent.

```python
# H0: 'category' and 'is_member' are independent variables.
chi2_results = report.chi2_test('category', 'is_member')

print(f"P-value: {chi2_results['p_value']:.4f}")
print(f"Conclusion: {chi2_results['conclusion (alpha=0.05)']}")
# Output:
# P-value: 0.8876
# Conclusion: The variables are independent (p >= 0.05).
```

#### 4. Compare Two Independent Groups (Non-parametric)
Check if the distribution of a numerical variable is the same across two groups. This is useful when your data is not normally distributed.

```python
# H0: The distribution of 'price' is the same for members and non-members.
mw_results = report.mann_whitney_u_test(col='price', group_col='is_member')
print(pd.Series(mw_results))

# Output:
# test                                                 Mann-Whitney U
# compared_variable                                           price
# groups                                               False vs True
# U_statistic                                               1241.0
# p_value                                                   0.963973
# conclusion (alpha=0.05)    No significant difference between distributi...
# dtype: object
```

## Why rostaing-report?

-   **Speed:** Go from a raw DataFrame to a full, insightful report in seconds. Drastically reduce the time spent on boilerplate EDA code.
-   **Clarity:** The structured output, both in notebooks and terminals, is designed for maximum readability. The plain-English interpretations for correlations help you communicate findings faster.
-   **Completeness:** It bridges the gap between descriptive statistics and initial hypothesis testing by bundling both into one cohesive interface.
-   **Better Decision-Making:** By quickly identifying potential issues like outliers, high cardinality, skewness, or unexpected correlations, you can make smarter, evidence-backed decisions on how to proceed with your data modeling or business analysis.

## Contributing

Contributions are welcome! If you have ideas for new features, find a bug, or want to improve the documentation, please feel free to open an issue or submit a pull request on the project's repository.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Useful Links
- Github: https://github.com/Rostaing/rostaing-report
- PyPI: https://pypi.org/project/rostaing-report/
- LinkedIn: https://www.linkedin.com/in/davila-rostaing/
- YouTube: [youtube.com/@RostaingAI](https://youtube.com/@rostaingai?si=8wo5H5Xk4i0grNyH)
```