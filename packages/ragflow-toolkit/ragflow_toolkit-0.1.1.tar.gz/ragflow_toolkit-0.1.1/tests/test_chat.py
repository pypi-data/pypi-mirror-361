def test_create_and_delete_chat(client):
    ds = client.datasets.create(name="chat_kb")
    chat = client.chats.create(name="chat_test", dataset_ids=[ds.id])
    assert chat.name == "chat_test"
    all_chats = client.chats.list()
    assert any(c.name == "chat_test" for c in all_chats)
    chat.delete()
    all_chats = client.chats.list()
    assert not any(c.name == "chat_test" for c in all_chats) 