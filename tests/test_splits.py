from src.credit_risk.__main__ import WORKBOOK, ensure_workbook
from src.credit_risk.data import load_clients, split_clients


def test_customer_splits_are_disjoint_and_cover_the_workbook():
    ensure_workbook()
    clients = load_clients(WORKBOOK)
    train, validation, test = split_clients(clients)

    assert (len(train), len(validation), len(test)) == (18_000, 6_000, 6_000)

    train_ids = set(train["ID"])
    validation_ids = set(validation["ID"])
    test_ids = set(test["ID"])

    assert train_ids.isdisjoint(validation_ids), "Customer shared by train and validation"
    assert train_ids.isdisjoint(test_ids), "Customer shared by train and test"
    assert validation_ids.isdisjoint(test_ids), "Customer shared by validation and test"

    assert train_ids | validation_ids | test_ids == set(clients["ID"])