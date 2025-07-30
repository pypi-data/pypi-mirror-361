def test_create_and_delete_agent(client):
    agent = client.agents.create(title="test_agent", dsl={})
    assert agent.title == "test_agent"
    all_agents = client.agents.list()
    assert any(a.title == "test_agent" for a in all_agents)
    agent.delete()
    all_agents = client.agents.list()
    assert not any(a.title == "test_agent" for a in all_agents) 