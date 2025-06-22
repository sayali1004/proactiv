import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import classification_report, confusion_matrix
import shap
import matplotlib.pyplot as plt

# Load the synthetic dataset
df = pd.read_csv("user_sessions.csv")

# Aggregate session-level features
agg_df = df.groupby("user_id").agg({
    "latency_since_last_action": "mean",
    "geo_distance_from_last_ip": "sum",
    "device_switch_count": "max",
    "session_duration": "max",
    "label": "max"
}).reset_index()

# Features and label
X = agg_df.drop(columns=["user_id", "label"])
y = agg_df["label"]


# Debug: check label distribution
label_counts = y.value_counts()
print("Label distribution:\n", label_counts)


# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a Gradient Boosting Classifier
model = GradientBoostingClassifier(n_estimators=100, max_depth=4, random_state=42)
model.fit(X_train, y_train)

# Evaluation
y_pred = model.predict(X_test)
print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred))

# SHAP for model explainability
explainer = shap.Explainer(model, X_train)
shap_values = explainer(X_test)

shap.summary_plot(shap_values, X_test, plot_type="bar")


joblib.dump(model, "feature_modeling.joblib")
print("✅ Model saved as 'feature_modeling.joblib'")