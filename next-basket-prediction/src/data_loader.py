from src.features.product_features import *
from src.features.user_features import *
from src.features.user_product_features import *
from src.features.target_builder import *
import numpy as np

data_dir = Path(__file__).resolve().parents[1]/'data'
feature_target_train = Path(__file__).resolve().parents[1]/'data'/'processed'/'feature_target_train.csv'
feature_target_validate = Path(__file__).resolve().parents[1]/'data'/'processed'/'feature_target_validate.csv'

orders_all = pd.read_csv(data_dir/'raw'/'orders.csv')
orders_prior = orders_all.loc[orders_all['eval_set'] == 'prior']
orders_train = orders_all.loc[orders_all['eval_set'] == 'train']
order_products_prior = pd.read_csv(data_dir/'raw'/'order_products__prior.csv')
order_products_train = pd.read_csv(data_dir/'raw'/'order_products__train.csv')
products = pd.read_csv(data_dir/'raw'/'products.csv')


def build_feature_target_csv(partition_for_training:float = 0.6,
                             Force_rewrite:bool = False)-> tuple[pd.DataFrame, pd.DataFrame]:

    if feature_target_train.exists() and feature_target_validate.exists() and not Force_rewrite:
        train = pd.read_csv(feature_target_train)
        validate = pd.read_csv(feature_target_validate)
        return train, validate

    user_features = build_user_features(orders_prior, order_products_prior,Force_rewrite)
    product_features = build_product_features(order_products_prior,Force_rewrite)
    user_product_features = build_user_product_features(orders_prior, order_products_prior, products, Force_rewrite)
    target = build_target(orders_all, order_products_train, Force_rewrite)

    features_combined =(user_product_features
                        .merge(product_features, on='product_id')
                        .merge(user_features, on='user_id')
                        .reset_index(drop=True)
    )
    target_users_mask = (features_combined['user_id']
                        .isin(target['user_id'])
    )
    features_combined = features_combined[target_users_mask]

    feature_target = (features_combined
                     .merge(target,
                     on=['user_id', 'product_id'],
                     how='left')
                     .reset_index(drop=True)
    )

    feature_target['reordered'] = feature_target['reordered'].fillna(0).astype(int)

    users_for_training = feature_target['user_id'].unique()

    np.random.seed(42)
    selected_users = np.random.choice(
        users_for_training,
        size=int(partition_for_training * len(users_for_training)),
        replace=False
    )

    train = feature_target[feature_target['user_id'].isin(selected_users)]
    validate = feature_target[~feature_target['user_id'].isin(selected_users)]

    train.to_csv(feature_target_train,index=False)
    validate.to_csv(feature_target_validate,index=False)

    return train, validate
