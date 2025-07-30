from ml_dataset_contract_tte import (
    # модельные данные (на входе инженерные признаки)
    TteFeatureRow,
    TteTargetRow,
    TtePredictRequest,
    # если требуется зафиксировать первичные данные
    SessionsRow,
    PurchasesRow,
    TteRawPredictRequest,
)


# Пример с инженерными данными

sample_row__input = {
    "expanding_tte_mean": 1.1,
    "tte_lag_1": 1.2,
}
sample_row__target = {"tte": 1.3}

feature_row = TteFeatureRow(**sample_row__input)
print(f"{feature_row=}")

target_row = TteTargetRow(**sample_row__target)
print(f"{target_row=}")

request = TtePredictRequest(rows=[feature_row])
payload = request.to_split_json()
print(f"payload:\n    {payload}")


# Пример с первичными данными

bronze_sessions = [
    SessionsRow(
        start="2025-07-07T10:00:00Z",
        end="2025-07-07T11:30:00Z",
    ),
    SessionsRow(
        start="2025-07-08T20:00:00Z",
        end="2025-07-08T21:30:00Z",
    )
]
bronze_purchase = PurchasesRow(
    time='2025-07-08T20:20:20Z',
    amount=100.0,
)

raw_request = TteRawPredictRequest(
    tables={
        "sessions":  [i.model_dump() for i in bronze_sessions],
        "purchases": [bronze_purchase.model_dump()],
    }
)
raw_payload = raw_request.model_dump_json()
print(f"raw-payload:\n    {raw_payload}")