import pandas as pd
from pathlib import Path

user_features_csv = Path(__file__).resolve().parents[2]/'data'/'processed'/'user_features.csv'

def build_user_features(orders:pd.DataFrame,
                        order_products:pd.DataFrame,
                        Force_rewrite:bool = False)->pd.DataFrame:

    if user_features_csv.exists() and not Force_rewrite:
        return pd.read_csv(user_features_csv)

    avg_gap = (orders.groupby('user_id')
        ['days_since_prior_order']
        .mean()
        .round(3)
        .rename('avg_time_between_orders')
        .reset_index()
        [['user_id', 'avg_time_between_orders']]
        )


    reorder_stats = (order_products.merge(
        orders[['user_id', 'order_id']], on='order_id')
        .groupby('user_id')
        .agg(total_products=('product_id', 'count'),
             total_reordered=('reordered', 'sum'))
        .reset_index()
        [['user_id', 'total_products', 'total_reordered']]
                     )

    reorder_stats['user_reorder_rate'] = (reorder_stats['total_reordered'] /
                                     reorder_stats['total_products']).round(3)

    per_user_features = (avg_gap.merge(
        reorder_stats, on='user_id')
        .reset_index()
        [['user_id','avg_time_between_orders', 'user_reorder_rate']]
    )

    per_user_features.to_csv(user_features_csv, index=False)

    return per_user_features
