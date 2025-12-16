import pandas as pd
from pathlib import Path

targe_csv = Path(__file__).resolve().parents[2]/'data'/'processed'/'target.csv'

def build_target(orders_all:pd.DataFrame,
                 order_products_train:pd.DataFrame,
                 Force_rewrite:bool = False)->pd.DataFrame:

    if targe_csv.exists() and not Force_rewrite:
        return pd.read_csv(targe_csv)

    user_product_target = (
        orders_all[['user_id', 'order_id']]
        .merge(order_products_train[['order_id', 'product_id', 'reordered']],
        on='order_id')
        [['user_id', 'product_id', 'reordered']]
    )
    user_product_target = user_product_target[user_product_target['reordered'] == 1]

    user_product_target.to_csv(targe_csv, index=False)

    return user_product_target[user_product_target['reordered'] == 1]


