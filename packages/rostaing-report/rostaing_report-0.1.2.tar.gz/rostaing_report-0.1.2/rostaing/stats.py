# rostaing/stats.py : V2

import pandas as pd
import numpy as np
from scipy import stats
from tabulate import tabulate

# ### CORRIGÉ : Nom de la classe pour correspondre à l'importation de l'utilisateur ###
class rostaing_report:
    """
    Main class for Exploratory Data Analysis (EDA) and statistical tests.
    Takes a Pandas DataFrame as input and generates a comprehensive report.
    """

    def __init__(self, df: pd.DataFrame):
        """
        Initializes the analyzer with a DataFrame.
        Args:
            df (pd.DataFrame): The DataFrame to be analyzed.
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Input must be a Pandas DataFrame.")
        self.df = df
        self.report = {}
        self._analyze()

    def _analyze(self):
        """Runs all descriptive analysis methods."""
        self._overview_analysis()
        self._numerical_analysis()
        self._categorical_analysis()
        self._correlations_analysis()

    def _overview_analysis(self):
        """General analysis of the DataFrame and its composition."""
        self.report['overview'] = {
            "Number of Observations (Rows)": self.df.shape[0],
            "Number of Variables (Columns)": self.df.shape[1],
            "Total Missing Values (NA)": self.df.isna().sum().sum(),
            "Overall Missing Values Rate (%)": f"{(self.df.isna().sum().sum() / self.df.size) * 100:.2f}",
            "Duplicated Rows Count": self.df.duplicated().sum(),
            "Duplicated Rows Rate (%)": f"{(self.df.duplicated().sum() / len(self.df)) * 100:.2f}",
            # ### RÉINTÉGRÉ : Taille mémoire du DataFrame ###
            "Memory Usage": f"{self.df.memory_usage(deep=True).sum() / 1024**2:.2f} MB"
        }

        variable_types_df = pd.DataFrame(self.df.dtypes.value_counts())
        variable_types_df.columns = ['Count']
        variable_types_df.index.name = 'Variable Type'
        self.report['variable_types'] = variable_types_df

    @staticmethod
    def _detect_outliers(series: pd.Series) -> str:
        """Detects outliers in a numerical series using the IQR method."""
        if not pd.api.types.is_numeric_dtype(series):
            return "N/A"
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        if iqr == 0:
            return "No" # Cannot determine outliers if IQR is zero
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        return "Yes" if any((series < lower_bound) | (series > upper_bound)) else "No"

    def _numerical_analysis(self):
        """Descriptive analysis of numerical variables."""
        num_df = self.df.select_dtypes(include=np.number)
        if num_df.empty:
            self.report['numerical'] = None
            return

        desc = num_df.describe().T
        desc['variance'] = num_df.var()
        desc['skewness'] = num_df.skew()
        desc['kurtosis'] = num_df.kurtosis()
        desc['sem'] = num_df.sem()
        desc['mad'] = num_df.apply(lambda x: (x - x.mean()).abs().mean())
        desc['missing_count'] = num_df.isna().sum()
        desc['missing_percent'] = (desc['missing_count'] / len(num_df)) * 100
        desc['unique_count'] = num_df.nunique()
        desc['duplicated_count'] = num_df.apply(lambda x: x.duplicated().sum())
        desc['has_outliers'] = num_df.apply(self._detect_outliers)

        self.report['numerical'] = desc[[
            'count', 'missing_count', 'missing_percent', 'unique_count', 'duplicated_count', 'has_outliers',
            'mean', 'std', 'sem', 'mad', 'min', '25%', '50%', '75%', 'max', 'variance', 'skewness', 'kurtosis'
        ]].rename(columns={'std': 'std_dev', '25%': 'Q1', '50%': 'median', '75%': 'Q3'})

    def _categorical_analysis(self):
        """Descriptive analysis of categorical variables."""
        cat_df = self.df.select_dtypes(include=['object', 'category', 'bool'])
        if cat_df.empty:
            self.report['categorical'] = None
            return

        desc = cat_df.describe(include=['object', 'category', 'bool']).T
        desc['missing_count'] = cat_df.isna().sum()
        desc['missing_percent'] = (desc['missing_count'] / len(cat_df)) * 100
        desc['duplicated_count'] = cat_df.apply(lambda x: x.duplicated().sum())

        self.report['categorical'] = desc[['count', 'missing_count', 'missing_percent', 'unique', 'duplicated_count', 'top', 'freq']]
        
    @staticmethod
    def _interpret_correlation(r: float) -> str:
        """Provides a textual interpretation of a correlation coefficient."""
        r_abs = abs(r)
        if r_abs >= 0.9:
            strength = "Very Strong"
        elif r_abs >= 0.7:
            strength = "Strong"
        elif r_abs >= 0.5:
            strength = "Moderate"
        elif r_abs >= 0.3:
            strength = "Weak"
        else:
            return "Negligible"
            
        direction = "Positive" if r > 0 else "Negative"
        return f"{strength} {direction}"

    def _correlations_analysis(self, top_n=10):
        """Calculates and reports the most correlated variable pairs with interpretation."""
        num_df = self.df.select_dtypes(include=np.number)
        if num_df.shape[1] < 2:
            self.report['correlations'] = None
            return
            
        corr_matrix = num_df.corr()
        corr_pairs = corr_matrix.unstack().reset_index()
        corr_pairs.columns = ['var1', 'var2', 'correlation']
        corr_pairs = corr_pairs[corr_pairs['var1'] != corr_pairs['var2']]
        corr_pairs['pair_key'] = corr_pairs.apply(lambda row: tuple(sorted((row['var1'], row['var2']))), axis=1)
        corr_pairs = corr_pairs.drop_duplicates(subset=['pair_key'])
        corr_pairs['abs_correlation'] = corr_pairs['correlation'].abs()
        corr_pairs = corr_pairs.sort_values('abs_correlation', ascending=False).drop(columns=['pair_key', 'abs_correlation'])
        corr_pairs['interpretation'] = corr_pairs['correlation'].apply(self._interpret_correlation)

        self.report['correlations'] = corr_pairs.head(top_n)

    def _format_html(self):
        """Generates the report in HTML format for Jupyter/notebooks."""
        html = "<h1>Rostaing Report</h1>"

        html += "<h2>Overview Statistics</h2>"
        html += tabulate(self.report['overview'].items(), headers=['Statistic', 'Value'], tablefmt='html')

        if self.report.get('variable_types') is not None:
            html += "<h2>Variable Types</h2>"
            html += self.report['variable_types'].to_html(classes='table table-striped')

        if self.report.get('numerical') is not None:
            html += "<h2>Numerical Variables Analysis</h2>"
            html += self.report['numerical'].to_html(classes='table table-striped', float_format='{:.3f}'.format)
        
        if self.report.get('categorical') is not None:
            html += "<h2>Categorical Variables Analysis</h2>"
            html += self.report['categorical'].to_html(classes='table table-striped')
            
        if self.report.get('correlations') is not None and not self.report['correlations'].empty:
            html += "<h2>Top Correlations</h2>"
            html += self.report['correlations'].to_html(classes='table table-striped', float_format='{:.3f}'.format, index=False)

        style = "<style> table { width: auto; border-collapse: collapse; margin-bottom: 20px; font-family: sans-serif; } th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; } tr:hover { background-color: #f5f5f5; } th { background-color: #007BFF; color: white; } h1, h2 { color: #333; border-bottom: 2px solid #007BFF; padding-bottom: 5px; } </style>"
        return f"{style}{html}"

    def _format_str(self):
        """Generates the report in plain text format for the console."""
        output = "--- Rostaing Report ---\n\n"

        output += "=== Overview Statistics ===\n"
        output += tabulate(self.report['overview'].items(), headers=['Statistic', 'Value'], tablefmt='grid')
        output += "\n\n"
        
        if self.report.get('variable_types') is not None:
            output += "=== Variable Types ===\n"
            output += tabulate(self.report['variable_types'], headers='keys', tablefmt='grid')
            output += "\n\n"

        if self.report.get('numerical') is not None:
            output += "=== Numerical Variables Analysis ===\n"
            output += tabulate(self.report['numerical'], headers='keys', tablefmt='grid', floatfmt=".3f")
            output += "\n\n"

        if self.report.get('categorical') is not None:
            output += "=== Categorical Variables Analysis ===\n"
            output += tabulate(self.report['categorical'], headers='keys', tablefmt='grid')
            output += "\n\n"
            
        if self.report.get('correlations') is not None and not self.report['correlations'].empty:
            output += "=== Top Correlations ===\n"
            output += tabulate(self.report['correlations'], headers='keys', tablefmt='grid', floatfmt=".3f", showindex=False)
            output += "\n"

        return output

    def __repr__(self):
        return self._format_str()

    def _repr_html_(self):
        return self._format_html()

    # --- INFERENTIAL STATISTICS METHODS ---

    def normality_test(self, col: str, test: str = 'shapiro', alpha: float = 0.05):
        """
        Performs a normality test on a column. H0: The sample comes from a normal distribution.
        
        Args:
            col (str): The column to test.
            test (str): The test to use. One of 'shapiro', 'jarque_bera', or 'normaltest'.
            alpha (float): The significance level.
        """
        data = self.df[col].dropna()
        if test.lower() == 'shapiro':
            stat, p_value = stats.shapiro(data)
            test_name = "Shapiro-Wilk"
        elif test.lower() == 'jarque_bera':
            stat, p_value = stats.jarque_bera(data)
            test_name = "Jarque-Bera"
        ### MODIFIÉ : Ajout du test de D'Agostino et Pearson comme option ###
        elif test.lower() == 'normaltest':
            stat, p_value = stats.normaltest(data)
            test_name = "D'Agostino & Pearson's test"
        else:
            ### MODIFIÉ : Mise à jour du message d'erreur pour inclure la nouvelle option ###
            raise ValueError("Unsupported test. Choose 'shapiro', 'jarque_bera', or 'normaltest'.")
        
        conclusion = f"The null hypothesis (normality) is rejected (p < {alpha})." if p_value < alpha else f"The null hypothesis (normality) cannot be rejected (p >= {alpha})."
        return {"test": test_name, "column": col, "statistic": stat, "p_value": p_value, f"conclusion (alpha={alpha})": conclusion}

    ### AJOUT : Nouvelle méthode pour le test de Kolmogorov-Smirnov ###
    def ks_test(self, col: str, dist: str = 'norm', alpha: float = 0.05):
        """
        Performs the Kolmogorov-Smirnov test for goodness of fit.
        H0: The data comes from the specified distribution.
        
        Interpretation: This test checks if the distribution of data in a column is
        significantly different from a theoretical distribution (e.g., 'norm' for normal).
        A low p-value suggests the data does not follow that distribution.
        
        Args:
            col (str): The column of data to test.
            dist (str or callable): The name of the distribution to test against (e.g., 'norm', 'expon').
            alpha (float): The significance level for the conclusion.
        """
        data = self.df[col].dropna()
        stat, p_value = stats.kstest(data, dist)
        
        conclusion = f"The data does not follow a '{dist}' distribution (p < {alpha})." if p_value < alpha else f"The data may follow a '{dist}' distribution (p >= {alpha})."
        return {"test": "Kolmogorov-Smirnov Test", "column": col, "distribution_tested": dist, "statistic": stat, "p_value": p_value, f"conclusion (alpha={alpha})": conclusion}


    def ttest_ind(self, col1: str, col2: str, equal_var: bool = True, alpha: float = 0.05):
        """
        Performs an independent two-sample T-test. H0: The means of the two samples are equal.
        
        Interpretation: Used to determine if there is a significant difference between the
        means of two independent groups. A low p-value indicates the means are likely different.
        """
        data1 = self.df[col1].dropna()
        data2 = self.df[col2].dropna()
        stat, p_value = stats.ttest_ind(data1, data2, equal_var=equal_var)
        conclusion = f"Statistically significant difference in means (p < {alpha})." if p_value < alpha else f"No statistically significant difference in means (p >= {alpha})."
        return {"test": "T-test (independent)", "columns": f"{col1} vs {col2}", "t_statistic": stat, "p_value": p_value, f"conclusion (alpha={alpha})": conclusion}

    def chi2_test(self, col1: str, col2: str, alpha: float = 0.05):
        """
        Performs a Chi-squared test of independence. H0: The two variables are independent.
        """
        contingency_table = pd.crosstab(self.df[col1], self.df[col2])
        chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
        conclusion = f"The variables are dependent (p < {alpha})." if p_value < alpha else f"The variables are independent (p >= {alpha})."
        return {"test": "Chi-squared Test of Independence", "variables": f"{col1} and {col2}", "chi2_statistic": chi2, "p_value": p_value, "degrees_of_freedom": dof, f"conclusion (alpha={alpha})": conclusion, "contingency_table": contingency_table}

    def mann_whitney_u_test(self, col: str, group_col: str, alpha: float = 0.05):
        """
        Performs the Mann-Whitney U test for two independent distributions. H0: The distributions are equal.
        """
        groups = self.df[group_col].unique()
        if len(groups) != 2:
            raise ValueError(f"The grouping column '{group_col}' must have exactly 2 unique groups.")
        
        group1_data = self.df[self.df[group_col] == groups[0]][col].dropna()
        group2_data = self.df[self.df[group_col] == groups[1]][col].dropna()
        
        stat, p_value = stats.mannwhitneyu(group1_data, group2_data)
        conclusion = f"The distributions are significantly different (p < {alpha})." if p_value < alpha else f"No significant difference between distributions (p >= {alpha})."
        return {"test": "Mann-Whitney U", "compared_variable": col, "groups": f"{groups[0]} vs {groups[1]}", "U_statistic": stat, "p_value": p_value, f"conclusion (alpha={alpha})": conclusion}

    def kruskal_wallis_test(self, col: str, group_col: str, alpha: float = 0.05):
        """
        Performs the Kruskal-Wallis test for k independent distributions. H0: The medians of all groups are equal.
        """
        groups_data = [self.df[self.df[group_col] == g][col].dropna() for g in self.df[group_col].unique()]
        
        stat, p_value = stats.kruskal(*groups_data)
        conclusion = f"At least one group median is significantly different (p < {alpha})." if p_value < alpha else f"No significant difference between group medians (p >= {alpha})."
        return {"test": "Kruskal-Wallis H", "compared_variable": col, "group_column": group_col, "H_statistic": stat, "p_value": p_value, f"conclusion (alpha={alpha})": conclusion}

    def correlation_matrix(self, method: str = 'pearson'):
        """
        Calculates the full correlation matrix for numerical variables.
        """
        num_df = self.df.select_dtypes(include=np.number)
        return num_df.corr(method=method)