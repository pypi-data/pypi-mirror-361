from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
import pandas as pd

class ChurnPreprocessor:
    """
    ChurnPreprocessor — tailored for the refined churn dataset

    Features:
    - OneHotEncodes all object-type (categorical) features
    - Scales all numerical features
    - Handles missing values with safe defaults
    - Splits into train/test sets
    - Stores scaler and encoder for reuse
    """

    def __init__(self, df, target_column='Churn'):
        self.df = df.copy()                                      # Make a copy of the input DataFrame to avoid altering original
        self.df.columns = self.df.columns.str.strip()            # Strip leading/trailing spaces from column names
        self.target_column = target_column.strip()               # Clean the target column name

        # To store fitted components
        self.pipeline = None                                     # Will store the preprocessing pipeline
        self.scaler = None                                       # Will store the fitted scaler for reuse
        self.ohe = None                                          # Will store the fitted OneHotEncoder for reuse

        # Outputs
        self.X_train = None                                      # Placeholder for training features
        self.X_test = None                                       # Placeholder for testing features
        self.y_train = None                                      # Placeholder for training labels
        self.y_test = None                                       # Placeholder for testing labels

    def preprocess(self, test_size=0.2, random_state=42):
        """
        Full preprocessing:
        - Identify feature types
        - Handle nulls (even if none present)
        - Encode categorical features
        - Scale numerical features
        - Split into train and test sets
        """
        # Separate input features and target label
        X = self.df.drop(columns=[self.target_column])           # Extract features by dropping the target column
        y = self.df[self.target_column]                          # Isolate the target variable

        # Identify feature types
        numeric_cols = X.select_dtypes(include=['int64', 'float64']).columns.tolist()  # List of numerical columns
        categorical_cols = X.select_dtypes(include=['object']).columns.tolist()        # List of categorical columns

        # Force all categorical to string to avoid mixed-type errors
        for col in categorical_cols:
            X[col] = X[col].astype(str)                          # Ensure all categorical values are of string type

        # Pipeline for numeric: impute (mean), then scale
        numeric_pipeline = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='mean')),         # Replace missing numeric values with column mean
            ('scaler', StandardScaler())                         # Scale numeric features to zero mean and unit variance
        ])

        # Categorical pipeline: Impute + OneHotEncode
        categorical_pipeline = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='most_frequent')),                   # Replace missing categorical values with the most frequent value
            ('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False))  # Encode categories into binary variables, ignore unseen categories
        ])

        # Combine into a column transformer
        self.pipeline = ColumnTransformer(transformers=[
            ('num', numeric_pipeline, numeric_cols),             # Apply numeric pipeline to numeric columns
            ('cat', categorical_pipeline, categorical_cols)      # Apply categorical pipeline to categorical columns
        ])

        # Train-test split
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state  # Split the data while preserving reproducibility
        )

        # Fit-transform training features and transform test features
        self.X_train = self.pipeline.fit_transform(self.X_train)  # Fit the pipeline on training data and transform it
        self.X_test = self.pipeline.transform(self.X_test)        # Transform the test data using the same pipeline

        # Store fitted components
        self.scaler = self.pipeline.named_transformers_['num'].named_steps['scaler']      # Retrieve and store the fitted scaler
        self.ohe = self.pipeline.named_transformers_['cat'].named_steps['encoder']        # Retrieve and store the fitted encoder

        return self.X_train, self.X_test, self.y_train, self.y_test  # Return preprocessed data splits

    def get_clean_dataframe(self):
        """
        Returns the internal cleaned DataFrame prior to transformation.
        Useful for applying additional analysis like journey classification.
        """
        return self.df.copy()
