from nexa_sdk.organizations import OrganizationAPI, Organization

class DummyClient:
    def request(self, method, path, **kwargs):
        if method == "GET" and path == "/organizations":
            return [{"id": 1, "name": "Org1"}]
        if method == "GET" and path.startswith("/organizations/"):
            return {"id": 1, "name": "Org1"}
        return []

def test_list_organizations():
    api = OrganizationAPI(DummyClient())  # type: ignore
    orgs = api.list_organizations()
    assert isinstance(orgs, list)
    assert isinstance(orgs[0], Organization)
    assert orgs[0].name == "Org1"

def test_list_organizations_empty():
    class EmptyClient:
        def request(self, method, path, **kwargs):
            return []
    api = OrganizationAPI(EmptyClient())  # type: ignore
    orgs = api.list_organizations()
    assert orgs == []

def test_get_organization():
    api = OrganizationAPI(DummyClient())  # type: ignore
    org = api.get_organization(1)
    assert isinstance(org, Organization)
    assert org.name == "Org1"
