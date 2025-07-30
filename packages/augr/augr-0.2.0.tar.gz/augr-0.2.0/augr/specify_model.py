def specify_ai_model(model: str) -> str:
    """
    Takes in a generic descriptor of a model name, and hydrates it with specifics details, as-necessary.

    For instance, "claude-3-7-sonnet" is invalid, but "us.anthropic.claude-3-7-sonnet-20250219" is valid.

    OpenAI and Gemini models do not need any translations.

    For now, this will just auto translate anything we detect that is being served from bedrock to the correct hyperspecific model name.
    """

    # If already fully qualified, return as-is
    if ":" in model and ("." in model or model.startswith("us.") or model.startswith("eu.") or model.startswith("apac.")):
        return model

    # Define mapping from generic names to specific Bedrock model identifiers
    # Always default to "us." prefixed versions when available
    model_mappings = {
        # Claude models (Anthropic)
        "claude-sonnet-4": "us.anthropic.claude-sonnet-4-20250514-v1:0",
        "claude-4-sonnet": "us.anthropic.claude-sonnet-4-20250514-v1:0",
        "claude-3-7-sonnet": "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        "claude-3.7-sonnet": "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        "claude-3-5-haiku": "us.anthropic.claude-3-5-haiku-20241022-v1:0",
        "claude-3.5-haiku": "us.anthropic.claude-3-5-haiku-20241022-v1:0",
        "claude-3-5-sonnet": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        "claude-3.5-sonnet": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        "claude-opus-4": "us.anthropic.claude-opus-4-20250514-v1:0",
        "claude-4-opus": "us.anthropic.claude-opus-4-20250514-v1:0",
        "claude-3-opus": "us.anthropic.claude-3-opus-20240229-v1:0",
        "claude-3-sonnet": "us.anthropic.claude-3-sonnet-20240229-v1:0",
        "claude-3-haiku": "us.anthropic.claude-3-haiku-20240307-v1:0",

        # Amazon Nova models
        "nova-pro": "us.amazon.nova-pro-v1:0",
        "nova-micro": "us.amazon.nova-micro-v1:0",
        "nova-lite": "us.amazon.nova-lite-v1:0",

        # Amazon Titan models
        "titan-text-premier": "amazon.titan-text-premier-v1:0",
        "titan-text-express": "amazon.titan-text-express-v1",
        "titan-text-lite": "amazon.titan-text-lite-v1",

        # Meta Llama models
        "llama3-3-70b": "us.meta.llama3-3-70b-instruct-v1:0",
        "llama3.3-70b": "us.meta.llama3-3-70b-instruct-v1:0",
        "llama3-2-90b": "us.meta.llama3-2-90b-instruct-v1:0",
        "llama3.2-90b": "us.meta.llama3-2-90b-instruct-v1:0",
        "llama3-2-11b": "us.meta.llama3-2-11b-instruct-v1:0",
        "llama3.2-11b": "us.meta.llama3-2-11b-instruct-v1:0",
        "llama3-2-3b": "us.meta.llama3-2-3b-instruct-v1:0",
        "llama3.2-3b": "us.meta.llama3-2-3b-instruct-v1:0",
        "llama3-2-1b": "us.meta.llama3-2-1b-instruct-v1:0",
        "llama3.2-1b": "us.meta.llama3-2-1b-instruct-v1:0",
        "llama3-1-405b": "us.meta.llama3-1-405b-instruct-v1:0",
        "llama3.1-405b": "us.meta.llama3-1-405b-instruct-v1:0",
        "llama3-1-70b": "us.meta.llama3-1-70b-instruct-v1:0",
        "llama3.1-70b": "us.meta.llama3-1-70b-instruct-v1:0",
        "llama3-1-8b": "us.meta.llama3-1-8b-instruct-v1:0",
        "llama3.1-8b": "us.meta.llama3-1-8b-instruct-v1:0",
        "llama3-70b": "meta.llama3-70b-instruct-v1:0",
        "llama3-8b": "meta.llama3-8b-instruct-v1:0",

        # Mistral models
        "mistral-large": "mistral.mistral-large-2402-v1:0",
        "mistral-small": "mistral.mistral-small-2402-v1:0",
        "mixtral-8x7b": "mistral.mixtral-8x7b-instruct-v0:1",
        "mistral-7b": "mistral.mistral-7b-instruct-v0:2",

        # Cohere models
        "command-r-plus": "cohere.command-r-plus-v1:0",
        "command-r": "cohere.command-r-v1:0",
        "command-text": "cohere.command-text-v14",
        "command-light": "cohere.command-light-text-v14",
    }

    # Normalize the input model name
    model_lower = model.lower().strip()

    # Try exact match first
    if model_lower in model_mappings:
        return model_mappings[model_lower]

    # Try partial matching for more flexible input
    for generic_name, specific_name in model_mappings.items():
        if generic_name in model_lower:
            return specific_name

    # If no mapping found, return the original model name
    return model
