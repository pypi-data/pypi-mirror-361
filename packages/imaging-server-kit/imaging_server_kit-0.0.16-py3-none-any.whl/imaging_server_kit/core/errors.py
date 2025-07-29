class AlgorithmNotFoundError(Exception):
    """Exception raised when a specified algorithm is not found."""

    def __init__(self, algorithm_name, message="Algorithm not found"):
        self.algorithm_name = algorithm_name
        self.message = f"{message}: {algorithm_name}"
        super().__init__(self.message)


class AlgorithmServerError(Exception):
    """Exception raised when a request to an algorithm server returns an unexpected status code."""

    def __init__(self, status_code, response_body, message="Algorithm server returned an unexpected status_code"):
        self.status_code = status_code
        self.response_body = response_body
        self.message = f"{message}: {status_code}\nResponse: {response_body}"
        super().__init__(self.message)


class AlgorithmTimeoutError(Exception):
    """Exception raised when a request to an algorithm server exceeds the time limit."""

    def __init__(self, status_code, response_text, message="Algorithm server returned an unexpected status_code"):
        self.status_code = status_code
        self.response_text = response_text
        self.message = f"{message}: {status_code}\nResponse: {response_text}"
        super().__init__(self.message)


class InvalidAlgorithmParametersError(Exception):
    """Exception raised when a request to an algorithm server is made with invalid algorithm parameters."""

    def __init__(self, status_code, response_text, message="Algorithm parameters were invalidated by the server"):
        self.status_code = status_code
        self.response_text = response_text
        pydantic_details = response_text.get("detail")[0]
        pydantic_validation_msg = pydantic_details.get("msg")
        pydantic_failing_param = pydantic_details.get("loc")[1]
        pydantic_failing_param_value = pydantic_details.get("input")
        self.message = f"{message}: Parameter: {pydantic_failing_param}. {pydantic_validation_msg}. Received: {pydantic_failing_param_value}."
        super().__init__(self.message)


class ServerRequestError(Exception):
    """Exception raised when HTTP requests fail."""

    def __init__(self, url: str, error: Exception, message="Request to server failed"):
        self.url = url
        self.error = error
        self.message = f"{message} ({url=}): {error}"
        super().__init__(self.message)