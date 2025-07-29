import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, roc_curve, auc

class ChurnPlotter:
    """
    ChurnPlotter – Clean, Modular Visualization Utility

    Generates:
    - Confusion Matrix with annotations
    - ROC Curve for a single model
    - ROC Curve for all model variants
    - Radial Chart of performance metrics per model
    - Composite Radial Chart of all model variants
    """

    @staticmethod
    def plot_confusion_matrix(y_true, y_pred, model_name, dataset="Test Set"):
        cm = confusion_matrix(y_true, y_pred)
        labels = ["Not Churn", "Churn"]
        plt.figure(figsize=(5, 4))
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=labels, yticklabels=labels)
        plt.xlabel("Predicted Label")
        plt.ylabel("True Label")
        plt.title(f"{model_name} – Confusion Matrix ({dataset})")
        plt.tight_layout()
        plt.show()

    @staticmethod
    def plot_roc_curve(model, X_test, y_test, model_name):
        y_prob = model.predict_proba(X_test)[:, 1]
        fpr, tpr, _ = roc_curve(y_test, y_prob)
        roc_auc = auc(fpr, tpr)

        plt.figure(figsize=(6, 5))
        plt.plot(fpr, tpr, label=f'AUC = {roc_auc:.2f}')
        plt.plot([0, 1], [0, 1], 'k--')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title(f"{model_name} – ROC Curve")
        plt.legend(loc='lower right')
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    @staticmethod
    def plot_all_roc_curves(variant_list, X_test, y_test, model_name):
        plt.figure(figsize=(8, 6))
        for idx, (params, model) in enumerate(variant_list):
            if hasattr(model, "predict_proba"):
                y_prob = model.predict_proba(X_test)[:, 1]
                fpr, tpr, _ = roc_curve(y_test, y_prob)
                roc_auc = auc(fpr, tpr)
                plt.plot(fpr, tpr, label=f"Variant {idx+1} (AUC = {roc_auc:.2f})")

        plt.plot([0, 1], [0, 1], 'k--', color='gray')
        plt.title(f"ROC Curves – {model_name} Variants")
        plt.xlabel("False Positive Rate")
        plt.ylabel("True Positive Rate")
        plt.legend(loc="lower right")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    @staticmethod
    def plot_radial_chart(metrics_dict, model_name):
        metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
        values = [metrics_dict[m] for m in metrics]
        values += values[:1]

        angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        ax.plot(angles, values, marker='o')
        ax.fill(angles, values, alpha=0.3)

        ax.set_yticklabels([])
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(metrics)
        ax.set_title(f"{model_name} – Radial Performance Chart", y=1.08)
        plt.tight_layout()
        plt.show()

    @staticmethod
    def plot_composite_radial_chart(evaluation_df, model_name):
        metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
        angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
        for i in range(len(evaluation_df)):
            row = evaluation_df.iloc[i]
            values = [row[m] for m in metrics]
            values += values[:1]
            ax.plot(angles, values, marker='o', label=f"Variant {i+1}")
            ax.fill(angles, values, alpha=0.1)

        ax.set_yticklabels([])
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(metrics)
        ax.set_title(f"Radial Chart – {model_name} Variants", y=1.08)
        plt.legend(loc="upper right", bbox_to_anchor=(1.2, 1.1))
        plt.tight_layout()
        plt.show()
