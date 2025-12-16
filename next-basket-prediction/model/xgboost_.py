from typing import List, Dict, Tuple
import xgboost as xgb
import pandas as pd
import numpy as np

DEFAULT_XGB_PARAMS: Dict = {
    'objective': 'binary:logistic',
    'eval_metric': 'auc',
    'max_depth': 4,
    'min_child_weight': 5,
    'gamma': 0.1,
    'learning_rate': 0.05,
    'n_estimators': 400,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'reg_alpha': 0.1,
    'reg_lambda': 1.0,
    'n_jobs': -1,
    'random_state': 42,
}


def xgb_train(
    train_df: pd.DataFrame,
    feature_columns: List[str],
    target_column: str,
    params:Dict | None = None)\
    -> xgb.XGBClassifier:

    if params is None:
        params = DEFAULT_XGB_PARAMS.copy()

    X = train_df[feature_columns]
    y = train_df['reordered']

    model = xgb.XGBClassifier(**params)
    model.fit(X, y)

    return model

def xgb_validate(
    model: xgb.XGBClassifier,
    validate_df: pd.DataFrame,
    feature_columns: List[str],
    target_column: str) -> pd.DataFrame:

    '''
    Evaluate trained model using AUC.
    '''

    X = validate_df[feature_columns]
    y_true = validate_df[target_column].to_numpy()

    y_pred = model.predict_proba(X)[:, 1]
    
    output_df = pd.DataFrame({'user_id':validate_df['user_id'], 'y_true': y_true, 'score': y_pred})

    return output_df
