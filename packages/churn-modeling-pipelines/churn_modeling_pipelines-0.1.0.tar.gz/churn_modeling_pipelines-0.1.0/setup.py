from setuptools import setup, find_packages

setup(
    name='churn_modeling_pipelines',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy',
        'matplotlib',
        'seaborn',
        'scikit-learn',
        'xgboost',
        'statsmodels'
    ],
    author='Ebikake',
    description='Modular churn modeling pipelines.',
    long_description='Tools for churn prediction, evaluation, and visualization.',
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
)
