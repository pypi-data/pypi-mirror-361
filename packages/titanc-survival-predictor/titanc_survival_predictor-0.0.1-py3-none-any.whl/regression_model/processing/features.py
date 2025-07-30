import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class DebugTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, message="Debugging Step"):
        self.message = message

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        if isinstance(X, pd.DataFrame):
            print(self.message)
            print(X.head())
        else:
            print(X[:5])
        return X


class ExtractLetterTransformer(BaseEstimator, TransformerMixin):
    # Extract fist letter of variable

    def __init__(self, variable: str):
        if not isinstance(variable, str):
            raise ValueError('variables should be a string')
        self.feature = variable

    def fit(self, X, y=None):
        # we need this step to fit the sklearn pipeline
        return self

    def transform(self, X):

        # so that we do not over-write the original dataframe
        X = X.copy()
        # for feature in self.variables:
        X[self.feature] = X[self.feature].str[0]

        return X
