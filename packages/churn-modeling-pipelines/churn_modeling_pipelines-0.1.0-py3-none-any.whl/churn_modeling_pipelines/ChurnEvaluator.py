import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)
from IPython.display import display, Markdown

# from churn_modeling_pipelines import ChurnPlotter  # Uncomment if needed

class ChurnEvaluator:
    """
    ChurnEvaluator – Evaluates all variants of a model using consistent metrics.

    Features:
    - Accepts a model builder method and evaluates each variant on test data
    - Computes key classification metrics: Accuracy, Precision, Recall, F1-Score
    - Computes a custom cost function based on business impact (FN and FP penalties)
    - Ranks and annotates best-performing variant by recall and cost
    - Optionally displays detailed visual analysis for each model

    Returns:
        - best_variant_name (str): Name identifier for the top-performing variant
        - best_model (fitted model): Trained model with the best performance
        - result_df (DataFrame): Annotated DataFrame of all variant evaluations
    """

    @staticmethod
    def evaluate_model(model_name, builder_method, X_train, X_test, y_train, y_test, plot_variant_level_charts=True):
        variants = builder_method()                           # List of (params, trained_model) pairs
        results = []                                          # Store performance results for each variant
        model_objects = {}                                    # Store models by variant name for later retrieval

        for i, (params, model) in enumerate(variants):
            y_pred = model.predict(X_test)                    # Generate predictions on the test set

            # Compute classification metrics
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred)
            recall = recall_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred)

            # Custom cost function
            fn_cost = 500
            fp_cost = 100
            confusion = confusion_matrix(y_test, y_pred)
            fp = confusion[0][1]
            fn = confusion[1][0]
            cost = (fp * fp_cost) + (fn * fn_cost)

            variant_name = f"Variant {i+1}"
            model_objects[variant_name] = model

            results.append({
                "Model": model_name,
                "Variant": variant_name,
                "Accuracy": accuracy,
                "Precision": precision,
                "Recall": recall,
                "F1-Score": f1,
                "Cost ($)": cost,
                "Params": params
            })

        result_df = pd.DataFrame(results)

        best_cost = result_df["Cost ($)"].min()
        result_df["is_best_cost"] = result_df["Cost ($)"].apply(
            lambda x: "🟩 True" if x == best_cost else "🟥 False"
        )

        best_idx = result_df.sort_values(
            by=["Recall", "Cost ($)", "F1-Score"],
            ascending=[False, True, False]
        ).index[0]

        result_df["is_best_variant"] = "❌"
        result_df.at[best_idx, "is_best_variant"] = "✅ Best"

        best_variant_name = result_df.loc[best_idx, "Variant"]
        best_model = model_objects[best_variant_name]

        if plot_variant_level_charts:
            display(Markdown(f"### Evaluation Summary – **{model_name}**"))
            display(result_df)

            print(f"\nConfusion Matrix – {model_name}: {best_variant_name}")
            # ChurnPlotter.plot_confusion_matrix(y_test, best_model.predict(X_test), model_name)

            print(f"\nROC Curve – All Variants: {model_name}")
            # ChurnPlotter.plot_all_roc_curves(variants, X_test, y_test, model_name)

            print(f"\nRadial Chart – All Variants: {model_name}")
            # ChurnPlotter.plot_composite_radial_chart(result_df, model_name)

        return best_variant_name, best_model, result_df
