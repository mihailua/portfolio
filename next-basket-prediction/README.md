# Building and Evaluating Reorder Prediction Model

This project builds a machine-learning ranking model to predict which products a user is likely to reorder. An XGBoost model is trained on user-, product-, and user–product interaction features and evaluated against a heuristic baseline using ROC-AUC and Mean Recall@K. The goal is to improve top-K reorder recommendations by learning from historical purchase behavior.


## Project Structure
```
data/raw
├─ products.csv               Raw product metadata
├─ orders.csv                 Order-level information
├─ order_products__train.csv  Training labels for reordered products
├─ order_products__prior.csv  Historical user–product interactions
├─ departments.csv            Product department mapping
├─ aisles.csv                 Product aisle mapping
├─ model_output.csv           Saved model predictions

data/processed
├─ product_features.csv       Engineered product-level features
├─ user_features.csv          Engineered user-level features
├─ user_product_features.csv  Engineered user–product interaction features
├─ target.csv                 Target variable (reordered)
├─ baseline.csv               Baseline predictions (top-20 most ordered products per user)
├─ feature_target_train.csv   Training dataset with features and target
├─ feature_target_validate.csv Validation dataset with features and target

model
├─ xgboost_.py                XGBoost model training and validation utilities

src
├─ data_loader.py             Dataset loading, preprocessing, and feature–target table construction
├─ __init__.py                Package initialization

src/features
├─ user_features.py           User-level feature engineering
├─ product_features.py        Product-level feature engineering
├─ user_product_features.py   User–product interaction feature engineering
├─ target_builder.py          Target variable construction
├─ __init__.py                Feature module initialization

notebooks
├─ experiment.ipynb           Model training, evaluation, and analysis notebook

.gitignore
README.md
requirements.txt
```

## Results
***
The XGBoost model substantially outperforms the heuristic baseline on both ranking and top-K recommendation metrics.
Giving **53% relative improvement** in ROC-AUC and **66% relative improvement** in Recall at 20.

Model Performance
- ROC-AUC: 0.8261
- Mean Recall@20 (per user): 0.7585

Baseline Performance
- ROC-AUC: 0.5768
- Mean Recall@20 (per user): 0.4576
***
## Model
The project uses an XGBoost binary logistic model trained on user-, product-, and user–product interaction features to rank products by reorder probability for each user.
## Baseline
The baseline recommends the 20 most frequently ordered products for each user using historical order counts. These products are marked as predicted reorders and used as a heuristic benchmark for comparison against the machine-learning model.
## Input Data
The model is trained and evaluated using the Instacart Market Basket Analysis dataset, which contains anonymized orders, products, and historical user–product interactions.
## License
This project is for educational and research purposes only.

