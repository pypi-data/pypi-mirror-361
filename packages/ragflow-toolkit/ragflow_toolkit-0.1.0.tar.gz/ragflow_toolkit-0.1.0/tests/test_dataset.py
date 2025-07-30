import pytest

def test_create_and_list_dataset(client):
    ds = client.datasets.create(name="test_kb")
    assert ds.name == "test_kb"
    all_ds = client.datasets.list()
    assert any(d.name == "test_kb" for d in all_ds)

def test_update_and_delete_dataset(client):
    ds = client.datasets.create(name="test_kb2")
    ds.update({"description": "desc"})
    ds.delete()
    all_ds = client.datasets.list()
    assert not any(d.name == "test_kb2" for d in all_ds) 