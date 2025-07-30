from feature_engine.imputation import AddMissingIndicator, CategoricalImputer, MeanMedianImputer
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from regression_model.config.core import config
from regression_model.processing.features import ExtractLetterTransformer

column_transformer = ColumnTransformer(
    transformers=[
        ('OneHot', Pipeline([
            ('encoder', OneHotEncoder())  # Apply OneHotEncoder
        ]), config.model_config.categorical_vars),
        ('Scaler', Pipeline([
            ('scaler', StandardScaler())  # Apply StandardScaler
        ]), config.model_config.numerical_vars)
    ])

titanic_pipe = Pipeline([

    # ===== IMPUTATION =====
    # impute categorical variables with string missing
    ('categorical_imputation', CategoricalImputer(
        imputation_method='missing', variables=config.model_config.categorical_vars)),

    # add missing indicator to numerical variables
    ('missing_indicator', AddMissingIndicator(variables=config.model_config.numerical_vars)),

    # impute numerical variables with the median
    ('median_imputation', MeanMedianImputer(
        imputation_method='median', variables=config.model_config.numerical_vars)),

    # Extract letter from cabin
    ('extract_letter', ExtractLetterTransformer(variable=config.model_config.cabin)),

    # == CATEGORICAL ENCODING ======
    # remove categories present in less than 5% of the observations (0.05)
    # group them in one category called 'Rare'

    # encode categorical variables using one hot encoding into k-1 variables
    ('column_transformer', column_transformer),

    ('Logit', LogisticRegression(C=0.001, random_state=0)),
])
