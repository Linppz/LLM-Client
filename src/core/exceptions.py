class PromptEngineError(Exception):
    def __init__(self, user_message: str, debug_info: str):
        super().__init__(user_message, debug_info)
        self.user_message = user_message
        self.debug_info = debug_info


class MissingVariableError(PromptEngineError):
    def __init__(self, template_name: str, missing_vars: set[str]):
        super().__init__(
            f"Template you are using is {template_name}, but you didn't provide values for variables: {', '.join(missing_vars)}",
            debug_info=f"template={template_name}, missing={missing_vars}",
        )


class TemplateNotFoundError(PromptEngineError):
    def __init__(self, template_name: str, template_dir: str):
        super().__init__(
            f"Template {template_name} not found.",
            debug_info=f"template={template_name}, available_templates file name = {template_dir}",
        )


class OutputParseError(PromptEngineError):
    def __init__(self, raw_output: str, error_message: str):
        super().__init__(
            f"Failed to parse the LLM output. Error: {error_message}",
            debug_info=f"raw_output={raw_output}",
        )


class LLMResponseError(PromptEngineError):
    def __init__(self, raw_response: str, provider: str, error_message: str):
        super().__init__(
            f"LLM returned an error response. Provider: {provider}, Message: {error_message}",
            debug_info=f"raw_response={raw_response}, provider={provider}, error_message={error_message}",
        )


class TokenBudgetExceededError(PromptEngineError):
    def __init__(self, usage_info: int, threshold: int):
        super().__init__(
            f"Token budget exceeded. Usage info: {usage_info}, threshold: {threshold}",
            debug_info=f"usage_info={usage_info}, threshold={threshold}",
        )
