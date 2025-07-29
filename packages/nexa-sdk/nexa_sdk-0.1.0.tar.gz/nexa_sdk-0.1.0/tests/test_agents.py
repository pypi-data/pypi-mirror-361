from nexa_sdk.agents import AgentAPI, Agent, CreateAgentDto, UpdateAgentDto

class DummyClient:
    def request(self, method, path, **kwargs):
        if method == "GET" and path == "/agents":
            return [{"id": 1, "organization_id": 1, "folder_id": 1, "current_version_number": 1, "is_deleted": False, "createdAt": "now", "updatedAt": "now"}]
        if method == "PATCH":
            return {"id": 1, "organization_id": 1, "folder_id": 1, "current_version_number": 1, "is_deleted": False, "createdAt": "now", "updatedAt": "now"}
        if method == "DELETE":
            return None
        if method == "GET" and "/versions" in path:
            return [1, 2, 3]
        if method == "GET":
            return {"id": 1, "organization_id": 1, "folder_id": 1, "current_version_number": 1, "is_deleted": False, "createdAt": "now", "updatedAt": "now"}
        if method == "POST":
            return {"id": 1, "organization_id": 1, "folder_id": 1, "current_version_number": 1, "is_deleted": False, "createdAt": "now", "updatedAt": "now"}
        return {}

def test_create_agent():
    api = AgentAPI(DummyClient())
    dto = CreateAgentDto(
        folder_id=1, title="Agent1", description=None, phone_number_id=1, language_id=1, voice_id=1,
        prompt_text="hi", conversation_start_type="auto", welcome_message=None, allow_interruptions=True,
        json_output_instructions=None, llm_id=None, version_title=None, knowledge_base_merged_document_id=None
    )
    agent = api.create_agent(dto, "org1")
    assert isinstance(agent, Agent)

def test_get_agent():
    api = AgentAPI(DummyClient())
    agent = api.get_agent(1, "org1")
    assert isinstance(agent, Agent)

def test_list_agents():
    api = AgentAPI(DummyClient())
    agents = api.list_agents(page=1, limit=10)
    assert isinstance(agents, list)
    assert isinstance(agents[0], Agent)

def test_update_agent():
    api = AgentAPI(DummyClient())
    dto = UpdateAgentDto(title="Updated")
    agent = api.update_agent(1, dto, "org1")
    assert isinstance(agent, Agent)

def test_delete_agent():
    api = AgentAPI(DummyClient())
    result = api.delete_agent(1, "org1")
    assert result is None

def test_get_agent_versions():
    api = AgentAPI(DummyClient())
    versions = api.get_agent_versions(1, "org1")
    assert versions == [1, 2, 3]
