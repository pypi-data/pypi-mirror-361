import pandas as pd

class CustomerJourneyClassifier:
    """
    Classifies customers into journey stages based on tenure and contact frequency.
    Adds a new column 'JourneyStage' to the DataFrame.
    Also computes churn rate by stage and visualizes it.
    """

    @staticmethod
    def assign_journey_stage(df):
        """
        Assigns a customer journey stage based on Tenurebin and Cccontactedlybin.
        Adds a new column 'JourneyStage' to the DataFrame.
        """
        def classify(row):
            if row['Tenurebin'] == 'New' and row['Cccontactedlybin'] == 'Rare':
                return 'Awareness'
            elif row['Tenurebin'] == 'New' and row['Cccontactedlybin'] == 'Occasional':
                return 'Consideration'
            elif row['Tenurebin'] == 'New' and row['Cccontactedlybin'] == 'Frequent':
                return 'Acquisition'
            elif row['Tenurebin'] in ['Recent', 'Established']:
                return 'Engagement'
            elif row['Tenurebin'] == 'Loyal':
                return 'Loyalty'
            else:
                return 'Other'

        df['JourneyStage'] = df.apply(classify, axis=1)
        return df

    @staticmethod
    def compute_churn_by_stage(df):
        """
        Computes churn rate (%) grouped by JourneyStage.
        Returns a pandas Series indexed by stage.
        """
        return (
            df[df['JourneyStage'] != 'Other']
            .groupby('JourneyStage')['Churn']
            .mean()
            .multiply(100)
            .round(2)
            .sort_index()
        )

    @staticmethod
    def plot_churn_journey(churn_rate_by_stage):
        """
        Plots churn risk across customer journey stages.
        Input: churn_rate_by_stage – Series with churn % per stage
        """
        import matplotlib.pyplot as plt

        stages = churn_rate_by_stage.index.tolist()
        rates = churn_rate_by_stage.values

        plt.figure(figsize=(10, 6))
        plt.plot(stages, rates, marker='o', linewidth=2, color='royalblue')
        plt.title("Customer Churn Risk Across the Journey (Derived from Customer_churn_dataset)", fontsize=14)
        plt.xlabel("Customer Journey Stage", fontsize=12)
        plt.ylabel("Churn Risk (%)", fontsize=12)
        plt.ylim(0, max(rates) + 10)
        plt.grid(True)

        for i, value in enumerate(rates):
            plt.text(i, value + 1, f"{value:.2f}%", ha='center', fontsize=10)

        plt.tight_layout()
        plt.show()
