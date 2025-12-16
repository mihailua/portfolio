import pandas as pd
from pathlib import Path

product_features_csv = Path(__file__).resolve().parents[2]/'data'/'processed'/'product_features.csv'

def build_product_features(order_products_prior:pd.DataFrame, Force_rewrite:bool = False)->pd.DataFrame:

    if product_features_csv.exists() and not Force_rewrite:
        return pd.read_csv(product_features_csv)

    product_features =( order_products_prior[['product_id','add_to_cart_order','reordered']]
                        .groupby(['product_id']).agg(
                        product_reorder_rate=('reordered', 'mean'),
                        add_to_cart_order=('add_to_cart_order', 'mean'))
                        .round({'product_reorder_rate':3, 'add_to_cart_order':3})
                        .reset_index()
    )

    product_features.to_csv(product_features_csv, index=False)
    return product_features
