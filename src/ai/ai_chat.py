import os
from openai import OpenAI
from openai import (
    APIError,
    APIConnectionError,
    RateLimitError,
    APIStatusError,
    BadRequestError,
    AuthenticationError,
    PermissionDeniedError,
    NotFoundError
)


from src.utils.logger import logger

def ask_openai_router(question, file_path=None):
    """
    Send a question and optionally a Python file to API using OpenAI SDK through OpenRouter
    """
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv('OPENROUTER_API_KEY'),
    )

    try:
        messages = []

        # If we have a file, read it and add as system message
        if file_path and os.path.exists(file_path) and file_path.endswith('.py'):
            with open(file_path, 'r', encoding='utf-8') as file:
                file_content = file.read()
                messages.append({
                    "role": "system",
                    "content": (
                        f"This is the previous version of the code from file "
                        f"'{file_path}' for context and comparison:\n\n{file_content}"
                    )
                })

        # Add user question
        messages.append({
            "role": "user",
            "content": question
        })

        completion = client.chat.completions.create(
            model=os.getenv('MODEL_NAME', 'openai/gpt-4-mini'),  # Use default if not set
            messages=messages
        )

        return completion.choices[0].message.content

    except APIConnectionError as connection_error:
        logger.log(f"Error connecting to API: {connection_error.__cause__}")
        error_message = "Sorry, there was an error connecting to the API."
    except RateLimitError as rate_error:
        logger.log(f"Rate limit exceeded: {rate_error}")
        error_message = "Sorry, the API rate limit has been exceeded. Please try again later."
    except AuthenticationError as auth_error:
        logger.log(f"Authentication error: {auth_error}")
        error_message = "Sorry, there was an authentication error. Please check your API key."
    except BadRequestError as request_error:
        logger.log(f"Bad request error: {request_error}")
        error_message = "Sorry, there was an error with the request format."
    except PermissionDeniedError as perm_error:
        logger.log(f"Permission denied: {perm_error}")
        error_message = "Sorry, you don't have permission to perform this action."
    except NotFoundError as not_found_error:
        logger.log(f"Resource not found: {not_found_error}")
        error_message = "Sorry, the requested resource was not found."
    except APIStatusError as status_error:
        logger.log(f"API error (status {status_error.status_code}): {status_error.response}")
        error_message = "Sorry, there was an error processing your request."
    except APIError as api_error:
        logger.log(f"API error: {api_error}")
        error_message = "Sorry, there was an unexpected API error."
    else:
        return completion.choices[0].message.content

    return error_message
