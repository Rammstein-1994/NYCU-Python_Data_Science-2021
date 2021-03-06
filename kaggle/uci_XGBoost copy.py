from collections import Counter
import numpy as np
import pandas as pd
import xgboost as xbg
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import KMeansSMOTE
from sklearn.metrics import roc_auc_score
from metric import show_result


DATA_DIR = "./uci_credit_card_default.csv"


def main():

    df = pd.read_csv(DATA_DIR).drop(columns=["SEX", "EDU"])

    # check column type
    col_numerical = {
        "AGE": int,
        "STA_1": object,
        "STA_2": object,
        "STA_3": object,
    }
    df = df.astype(col_numerical)

    # label encoder
    label_col = ["STA_1", "STA_2", "STA_3"]
    df[label_col] = df[label_col].apply(LabelEncoder().fit_transform)

    # label encoder for the target values
    le = LabelEncoder()
    le.fit(df["PAY"].values)
    df["PAY"] = le.transform(df["PAY"].values)

    # k-means SMOTE
    X, y = df.drop(columns="PAY").values, df["PAY"].values
    sample_size, _ = X.shape
    k = int(np.sqrt(sample_size / 2))
    sm = KMeansSMOTE(
        k_neighbors=k,
        sampling_strategy="minority",
        cluster_balance_threshold=0.24,
        n_jobs=-1,
        kmeans_estimator=2,
    )
    X_train, y_train = sm.fit_resample(X, y)
    print(sorted(Counter(y_train).items()))

    # train test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, stratify=y)
    print(
        f"{X_train.shape = }, {y_train.shape = }, {X_test.shape = }, {y_test.shape = }"
    )

    # min-max scaler
    scaler = MinMaxScaler()
    scaler.fit(X_train)
    X_train = scaler.transform(X_train)
    X_test = scaler.transform(X_test)

    # model
    clf = xbg.XGBClassifier(
        objective="binary:logistic",
        n_estimators=10,
        use_label_encoder=False,
        learning_rate=0.2,
        max_depth=200,
    )

    clf.fit(
        X_train,
        y_train,
        verbose=False,
        eval_metric="logloss",
        eval_set=[(X_test, y_test)],
    )

    y_pred = clf.predict(X_test)
    print(f"Training Score: {clf.score(X_train, y_train):.2f}")
    print(f"Testing Score: {clf.score(X_test, y_test):.2f}")
    print(f"ROC AUC: {roc_auc_score(y_test, y_pred):.2f}")
    show_result(clf, y_test, y_pred, le)


if __name__ == "__main__":
    main()
