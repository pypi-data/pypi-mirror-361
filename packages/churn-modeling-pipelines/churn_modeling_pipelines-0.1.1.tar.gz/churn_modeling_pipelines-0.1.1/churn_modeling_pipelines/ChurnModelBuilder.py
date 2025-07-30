from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

class ChurnModelBuilder:
    """
    ChurnModelBuilder — Generates model variants for churn prediction

    Features:
    - Accepts preprocessed training and testing data
    - Builds multiple hyperparameter variants for each model type
    - Supports modular expansion (Logistic Regression, KNN, SVM, etc.)
    - Returns a list of (parameters, trained model) pairs for evaluation
    """

    def __init__(self, X_train, X_test, y_train):
        self.X_train = X_train                      # Training features
        self.X_test = X_test                        # Test features (not used during model fitting here)
        self.y_train = y_train                      # Training labels

    def build_logistic_regression(self):
        """
        Logistic Regression Model Variants:
        - Explores different values of regularization strength (C)
        - Tests use of class weighting for imbalance
        - Returns list of (params, trained model) pairs
        """
        combinations = [
            {'C': 0.01, 'class_weight': None},
            {'C': 0.1, 'class_weight': 'balanced'},
            {'C': 1.0, 'class_weight': None},
            {'C': 10.0, 'class_weight': 'balanced'},
            {'C': 100.0, 'class_weight': {0: 1, 1: 2}},
        ]
        models = []
        for params in combinations:
            model = LogisticRegression(**params, max_iter=1000, random_state=42)
            model.fit(self.X_train, self.y_train)
            models.append((params, model))
        return models

    def build_decision_tree(self):
        """
        Decision Tree Model Variants:
        - Tests different tree depths
        - Applies class weights for imbalance
        - Returns list of (params, trained model) pairs
        """
        combinations = [
            {'max_depth': 3, 'class_weight': None},
            {'max_depth': 5, 'class_weight': 'balanced'},
            {'max_depth': 7, 'class_weight': None},
            {'max_depth': 9, 'class_weight': 'balanced'},
            {'max_depth': None, 'class_weight': {0: 1, 1: 2}},
        ]
        models = []
        for params in combinations:
            model = DecisionTreeClassifier(**params, random_state=42)
            model.fit(self.X_train, self.y_train)
            models.append((params, model))
        return models

    def build_knn(self):
        """
        K-Nearest Neighbors Model Variants:
        - Varies the number of neighbors (k)
        - No need for class weights or regularization
        - Returns list of (params, trained model) pairs
        """
        models = []
        for k in [3, 5, 7, 9, 11]:
            model = KNeighborsClassifier(n_neighbors=k)
            model.fit(self.X_train, self.y_train)
            models.append(({'n_neighbors': k}, model))
        return models

    def build_naive_bayes(self):
        """
        Naive Bayes Model Variants (GaussianNB):
        - Explores different smoothing levels
        - Suitable for small, clean, numeric datasets
        - Returns list of (params, trained model) pairs
        """
        models = []
        for smoothing in [1e-9, 1e-8, 1e-7, 1e-6, 1e-5]:
            model = GaussianNB(var_smoothing=smoothing)
            model.fit(self.X_train, self.y_train)
            models.append(({'var_smoothing': smoothing}, model))
        return models

    def build_svm(self):
        """
        Support Vector Machine Model Variants:
        - Tunes regularization (C), kernel scaling (gamma), and class weighting
        - Uses `probability=True` for probability predictions
        - Returns list of (params, trained model) pairs
        """
        combinations = [
            {'C': 0.1, 'gamma': 'scale', 'class_weight': None},
            {'C': 1.0, 'gamma': 'scale', 'class_weight': 'balanced'},
            {'C': 10.0, 'gamma': 'auto', 'class_weight': 'balanced'},
            {'C': 0.5, 'gamma': 'auto', 'class_weight': None},
            {'C': 5.0, 'gamma': 'scale', 'class_weight': {0: 1, 1: 2}},
        ]
        models = []
        for params in combinations:
            model = SVC(**params, probability=True, random_state=42)
            model.fit(self.X_train, self.y_train)
            models.append((params, model))
        return models

    def build_random_forest(self):
        """
        Random Forest Model Variants:
        - Varies tree count (n_estimators) and depth (max_depth)
        - Suitable for reducing overfitting or underfitting
        - Returns list of (params, trained model) pairs
        """
        combinations = [
            {'n_estimators': 100, 'max_depth': 3},
            {'n_estimators': 200, 'max_depth': 5},
            {'n_estimators': 300, 'max_depth': 7},
            {'n_estimators': 100, 'max_depth': None},
            {'n_estimators': 200, 'max_depth': 10},
        ]
        models = []
        for params in combinations:
            model = RandomForestClassifier(**params, random_state=42)
            model.fit(self.X_train, self.y_train)
            models.append((params, model))
        return models

    def build_xgboost(self):
        """
        XGBoost Model Variants:
        - Combines number of trees, tree depth, and learning rate
        - Uses `logloss` as evaluation metric for binary classification
        - Returns list of (params, trained model) pairs
        """
        combinations = [
            {'n_estimators': 100, 'max_depth': 3, 'learning_rate': 0.1},
            {'n_estimators': 200, 'max_depth': 4, 'learning_rate': 0.1},
            {'n_estimators': 150, 'max_depth': 5, 'learning_rate': 0.05},
            {'n_estimators': 300, 'max_depth': 3, 'learning_rate': 0.01},
            {'n_estimators': 100, 'max_depth': 6, 'learning_rate': 0.2},
        ]
        models = []
        for params in combinations:
            model = XGBClassifier(**params, use_label_encoder=False, eval_metric='logloss', random_state=42)
            model.fit(self.X_train, self.y_train)
            models.append((params, model))
        return models
