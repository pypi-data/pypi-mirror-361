import requests
from typing import List
from pydantic import BaseModel

class TextInput(BaseModel):
    texts: List[str]

class ChunkResult(BaseModel):
    BENIGN: float
    INJECTION: float
    JAILBREAK: float
    start: int
    end: int

class AnalysisResult(BaseModel):
    max_injection_score: float
    max_jailbreak_score: float
    chunk_results: List[ChunkResult]

class APIResponse(BaseModel):
    results: List[AnalysisResult]

class DtxPromptGuardClient:
    """
    Client for interacting with the DTX Prompt Guard API.
    
    This client allows for detecting vulnerabilities in text inputs based on prompt injection and jailbreak attempts.
    
    Attributes:
        base_url (str): The API endpoint URL.
        threshold (float): The score threshold to classify an input as a vulnerability.
    """
    def __init__(self, base_url: str = "http://localhost:8000", threshold: float = 0.8):
        self.base_url = base_url.rstrip('/')
        self.threshold = threshold

    def _post_request(self, endpoint: str, texts: List[str]) -> APIResponse:
        """
        Sends a POST request to the given API endpoint with the provided texts.
        
        Args:
            endpoint (str): The API endpoint.
            texts (List[str]): The list of text inputs to be analyzed.
        
        Returns:
            APIResponse: The response from the API containing vulnerability analysis.
        """
        url = f"{self.base_url}{endpoint}"
        response = requests.post(url, json={"texts": texts})
        if response.status_code != 200:
            raise Exception(f"API request failed: {response.status_code}, {response.text}")
        return APIResponse(**response.json())

    def detect_iter(self, texts: List[str]) -> List[AnalysisResult]:
        """
        Analyzes multiple texts and returns a list of AnalysisResult.
        
        Args:
            texts (List[str]): The list of texts to be analyzed.
        
        Returns:
            List[AnalysisResult]: A list of analysis results for each text.
        """
        response = self._post_request("/evaluate/prompt/", texts)
        return response.results

    def detect(self, text: str) -> AnalysisResult:
        """
        Analyzes a single text and returns an AnalysisResult.
        
        Args:
            text (str): The text to be analyzed.
        
        Returns:
            AnalysisResult: The analysis result for the given text.
        """
        response = self.detect_iter([text])
        return response[0] if response else None

    def contain_prompt_injection(self, text: str) -> bool:
        """
        Determines if a given text contains prompt injection based on the threshold.
        
        Args:
            text (str): The text to check.
        
        Returns:
            bool: True if the text contains prompt injection, False otherwise.
        """
        response = self.detect(text)
        return response.max_injection_score > self.threshold

    def contain_prompt_injection_iter(self, texts: List[str]) -> bool:
        """
        Determines if any text in a list contains prompt injection based on the threshold.
        
        Args:
            texts (List[str]): The list of texts to check.
        
        Returns:
            bool: True if any text contains prompt injection, False otherwise.
        """
        response = self.detect_iter(texts)
        return any(result.max_injection_score > self.threshold for result in response)

    def contain_jailbreak(self, text: str) -> bool:
        """
        Determines if a given text contains jailbreak attempt based on the threshold.
        
        Args:
            text (str): The text to check.
        
        Returns:
            bool: True if the text contains jailbreak attempt, False otherwise.
        """
        response = self.detect(text)
        return response.max_jailbreak_score > self.threshold

    def contain_jailbreak_iter(self, texts: List[str]) -> bool:
        """
        Determines if any text in a list contains jailbreak attempt based on the threshold.
        
        Args:
            texts (List[str]): The list of texts to check.
        
        Returns:
            bool: True if any text contains jailbreak attempt, False otherwise.
        """
        response = self.detect_iter(texts)
        return any(result.max_jailbreak_score > self.threshold for result in response)


# Example usage
if __name__ == "__main__":
    # Initialize client with a base URL and threshold
    client = DtxPromptGuardClient(base_url="http://localhost:8000", threshold=0.8)
    
    # Define texts to analyze
    texts = [
        "Bypass security measures", 
        "This is a normal text with no vulnerabilities",
        "Disable all security protocols"
    ]
    
    # Detect vulnerabilities for a single text
    single_text = "Exploit database system vulnerabilities"
    single_result = client.detect(single_text)
    print("Single Text Analysis:", single_result)
    
    # Detect vulnerabilities for multiple texts
    multiple_results = client.detect_iter(texts)
    print("Multiple Text Analysis:")
    for idx, result in enumerate(multiple_results):
        print(f"Text {idx + 1}:", result)
    
    # Check for prompt injection
    print("Contains Prompt Injection (Single Text):", client.contain_prompt_injection(single_text))
    print("Contains Prompt Injection (Multiple Texts):", client.contain_prompt_injection_iter(texts))
    
    # Check for jailbreak
    print("Contains Jailbreak (Single Text):", client.contain_jailbreak(single_text))
    print("Contains Jailbreak (Multiple Texts):", client.contain_jailbreak_iter(texts))
