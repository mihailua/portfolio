import pandas as pd
import numpy as np
from pathlib import Path
from .target_builder import build_target

user_product_features_csv = Path(__file__).resolve().parents[2]/'data'/'processed'/'user_product_features.csv'
baseline_csv = Path(__file__).resolve().parents[2]/'data'/'processed'/'baseline.csv'

def build_baseline(orders:pd.DataFrame,
                   order_products_prior:pd.DataFrame,
                   order_products_train:pd.DataFrame,
                   Force_rewrite:bool = False)->pd.DataFrame:
    if baseline_csv.exists() and not Force_rewrite:
        return pd.read_csv(baseline_csv)

    user_product_baseline = (orders[['user_id','order_id']]
                            .merge(order_products_prior, on='order_id')
                            [['user_id','product_id']]
    )
    user_product_baseline['bought_times'] = (user_product_baseline
                                             .groupby(['user_id','product_id'])['product_id']
                                             .transform('count')
    )
    user_product_baseline['rank'] = (
        user_product_baseline
        .groupby('user_id')['bought_times']
        .rank(method='first', ascending=False)
    )
    user_product_baseline['pred_reordered'] = np.where(
        user_product_baseline['rank'] <= 20, 1, 0
    )
    reordered_truth = build_target(orders, order_products_train)

    target_users_mask = (user_product_baseline['user_id']
                        .isin(reordered_truth['user_id'])
    )
    user_product_baseline = user_product_baseline[target_users_mask]

    user_product_baseline = (user_product_baseline
                     .merge(reordered_truth,
                     on=['user_id', 'product_id'],
                     how='left')
                     .reset_index(drop=True)
                     [['user_id','product_id','pred_reordered', 'reordered']]
    )

    user_product_baseline['reordered'] = user_product_baseline['reordered'].fillna(0).astype(int)
    user_product_baseline.to_csv(baseline_csv, index=False)

    return user_product_baseline

def build_user_product_features(orders:pd.DataFrame,
                                order_products_prior:pd.DataFrame,
                                products,
                                Force_rewrite:bool = False)->pd.DataFrame:

    if user_product_features_csv.exists() and not Force_rewrite:
        return pd.read_csv(user_product_features_csv)

    user_product_prior = (orders[['user_id', 'order_id', 'order_number']]
                    .merge(order_products_prior, on='order_id')
                    .merge(products[['product_id', 'aisle_id', 'department_id']], on='product_id')
                    [['user_id', 'product_id', 'order_number', 'aisle_id', 'department_id', 'add_to_cart_order', 'reordered']]
                          )

    user_max_order = (
        user_product_prior
        .groupby('user_id')['order_number']
        .max()
        .rename('user_max_order')
    )

    user_product_prior = user_product_prior.merge(
        user_max_order,
        on='user_id',
        how='left'
    )

    user_product_prior['one_of_last_5'] = (
            user_product_prior['user_max_order']
            - user_product_prior['order_number']
            <= 4
    )

    user_product_prior = (user_product_prior
                          .groupby(['user_id','product_id'])
                          .agg(
                          user_max_order=('user_max_order', 'first'),
                          aisle_id=('aisle_id', 'first'),
                          department_id=('department_id', 'first'),
                          avg_position_in_cart = ('add_to_cart_order', 'mean'),
                          bought_times = ('product_id', 'count'),
                          user_product_last_order=('order_number', 'max'),
                          bought_in_last_5=('one_of_last_5', 'any'),
                          times_in_last_5_orders = ('one_of_last_5', 'sum'))
                          .round({'avg_position_in_cart':3})
                          .reset_index()
    )


    user_product_prior['time_since_last_order_score'] = (
            1.0 - 1/user_product_prior['user_max_order']*(user_product_prior['user_max_order']
            - user_product_prior['user_product_last_order'])).round(3)


    user_product_prior['user_aisle_freq'] = (
                         user_product_prior
                         .groupby(['user_id','aisle_id'])['aisle_id']
                         .transform('count')/
                         user_product_prior
                         .groupby('user_id')['aisle_id']
                         .transform('count')).round(3)

    user_product_prior['user_department_freq'] = (
            user_product_prior
            .groupby(['user_id', 'department_id'])['department_id']
            .transform('count') /
            user_product_prior
            .groupby('user_id')['department_id']
            .transform('count')).round(3)

    user_product_prior = user_product_prior.drop('bought_in_last_5', axis=1)
    user_product_prior = user_product_prior.drop('aisle_id', axis = 1)
    user_product_prior = user_product_prior.drop('department_id', axis=1)
    user_product_prior = user_product_prior.drop('user_max_order', axis=1)
    user_product_prior = user_product_prior.drop('user_product_last_order', axis=1)
    user_product_prior.to_csv(user_product_features_csv, index=False)
    return user_product_prior



