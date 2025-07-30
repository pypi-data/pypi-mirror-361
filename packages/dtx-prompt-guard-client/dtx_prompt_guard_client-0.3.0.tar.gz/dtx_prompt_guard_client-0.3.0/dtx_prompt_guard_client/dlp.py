import requests
from typing import List, Optional
from pydantic import BaseModel
import json

class HaskInput(BaseModel):
    text: str
    context_id: Optional[str] = None

class FieldMapping(BaseModel):
    original_value: str
    masked_value: str

class HaskOutput(BaseModel):
    output: str
    context_id: str
    fields: List[FieldMapping]

class DehaskInput(BaseModel):
    text: str
    context_id: str

class DehaskOutput(BaseModel):
    output: str
    fields: List[FieldMapping]

class DLPClient:
    """
    Client for interacting with the Data Loss Prevention (DLP) API.
    """
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
    
    def _post_request(self, endpoint: str, data: BaseModel):
        """
        Sends a POST request to the given API endpoint with the provided data.
        """
        url = f"{self.base_url}{endpoint}"
        response = requests.post(url, json=data.model_dump(exclude_none=True))
        if response.status_code != 200:
            raise Exception(f"API request failed: {response.status_code}, {response.text}")
        return response.json()

    def hask(self, input_data: HaskInput) -> HaskOutput:
        """
        Hashes sensitive data and returns masked values.
        """
        response = self._post_request("/api/data/hask", input_data)
        response["fields"] = [FieldMapping(**field) for field in response.get("fields", [])]
        return HaskOutput(**response)
    
    def dehask(self, input_data: DehaskInput) -> DehaskOutput:
        """
        De-hashes sensitive data using stored context.
        """
        response = self._post_request("/api/data/dehask", input_data)
        response["fields"] = [FieldMapping(**field) for field in response.get("fields", [])]
        return DehaskOutput(**response)

    def get_masking_rules(self):
        """
        Retrieves available masking rules.
        """
        url = f"{self.base_url}/api/data/hask/rules"
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch masking rules: {response.status_code}, {response.text}")
        return response.json()

if __name__ == "__main__":
    client = DLPClient(base_url="http://localhost:8000")
    

    # text = "securaa.io/path, gaurav.chauhan@securaa.io,{\"tasks_tag\":\"\",\"tenantcode\":\"tenant\",\"isdemo\":false,\"token\":\"c8e2fd20-8e92-41fe-458d-c36faeaf15cc-1569221037671\",\"jwttoken\":\"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3N0b2tlbiI6ImM4ZTJmZDIwLThlOTItNDFmZS00NThkLWMzNmZhZWFmMTVjYy0xNTY5MjIxMDM3NjcxIiwiZXhwIjoxNzIxNDUxMjU3fQ.AAFiUoRqRVXig5PuPF3_6gSrXo6K-ONl7Y1_HlTi0TA\",\"inputfields\":[{\"name\":\"to_mail_address\",\"label\":\"To\",\"type\":\"textbox\",\"id\":\"\",\"required\":false,\"maxLength\":0,\"value\":\"pratibha@securaa.io\",\"host\":\"\",\"filters\":null,\"transformers\":null},{\"name\":\"cc_mail_address\",\"label\":\"CC\",\"type\":\"textbox\",\"id\":\"\",\"required\":false,\"maxLength\":0,\"value\":\"gaurav.chauhan@securaa.io\",\"host\":\"\",\"filters\":null,\"transformers\":null},{\"name\":\"bcc_mail_address\",\"label\":\"BCC\",\"type\":\"textbox\",\"id\":\"\",\"required\":false,\"maxLength\":0,\"value\":\"\",\"host\":\"\",\"filters\":null,\"transformers\":null},{\"name\":\"teamname\",\"label\":\"TeamName\",\"type\":\"textbox\",\"id\":\"\",\"required\":false,\"maxLength\":0,\"value\":\"\",\"host\":\"\",\"filters\":null,\"transformers\":null},{\"name\":\"subject\",\"label\":\"Subject\",\"type\":\"textbox\",\"id\":\"\",\"required\":false,\"maxLength\":0,\"value\":\"Action Details Performed on Case ID : 2\",\"host\":\"\",\"filters\":null,\"transformers\":null},{\"name\":\"template\",\"label\":\"Select Template\",\"type\":\"select\",\"id\":\"\",\"required\":false,\"maxLength\":0,\"value\":\"\",\"host\":\"\",\"filters\":null,\"transformers\":null},{\"name\":\"message\",\"label\":\"Message\",\"type\":\"textarea\",\"id\":\"\",\"required\":false,\"maxLength\":0,\"value\":\"\\u003cdiv style=\\\"white-space: pre-line\\\"\\u003eHi Team,\\n\\nBelow sharing the incident details :-\\n\\nCase ID : 2\\nSource IP : 114.234.162.153,114.234.162.153, 219.74.19.70, 93.114.205.169\\nReputation : 1, 4, 4\\nDestination IP : 172.31.15.73, 172.31.26.173\\nUser : Rebecca Harrington\\n\\nAction Taken :-\\n1) AD User password reset.\\n2) Source IP reputation Checked\\n3) Destinations Machine isolated. \\n\\nRegards\\nSecuraa\\n\\u003c/div\\u003e\",\"host\":\"\",\"filters\":null,\"transformers\":null},{\"name\":\"file_path\",\"label\":\"File Path for Sending Attachment\",\"type\":\"textbox\",\"id\":\"\",\"required\":false,\"maxLength\":0,\"value\":\"\",\"host\":\"\",\"filters\":null,\"transformers\":null}],\"filename\":\"\",\"functionname\":\"\"}"
    text = "example.com, phishtank.org, 198.41.0.4, google.com, Suggest what command should a network admin run to access the router at IP 203.0.113.5 with credentials admin@company.com to connect with the internal system at http://intranet.company.com and my password password123. https://app.slack.com/client/T07H6LYPE7Q/C08CKJ8TE1G, https://slack.com/client/T07H6LYPE7Q/C08CKJ8TE1G, http://93.114.205.169/MNabhFOj/bhwb9GUfG0xhaHqb9H/DBpHVSGfW5xz, http://93.114.205.169/MNabhFOj/bhwb9GUfG0xhaHqb9H/DBpHVSGfW5xz"
    hask_input = HaskInput(text=text)
    hask_output = client.hask(hask_input)
    print(json.dumps(hask_output.model_dump(), indent=4))
    
    dehask_input = DehaskInput(text=hask_output.output, context_id=hask_output.context_id)
    dehask_output = client.dehask(dehask_input)
    print(json.dumps(dehask_output.model_dump(), indent=4))
    
    # Fetch and print masking rules
    masking_rules = client.get_masking_rules()
    print(json.dumps(masking_rules, indent=4))



