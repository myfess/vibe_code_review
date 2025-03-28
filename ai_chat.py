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
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def ask_deepseek(question, file_path=None):
    """
    Send a question and optionally a Python file to API using OpenAI SDK
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
                    "content": f"This is the previous version of the code from file '{file_path}' for context and comparison:\n\n{file_content}"
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
    except APIConnectionError as e:
        print(f"Error connecting to API: {e.__cause__}")
        return "Sorry, there was an error connecting to the API."
    except RateLimitError as e:
        print(f"Rate limit exceeded: {e}")
        return "Sorry, the API rate limit has been exceeded. Please try again later."
    except AuthenticationError as e:
        print(f"Authentication error: {e}")
        return "Sorry, there was an authentication error. Please check your API key."
    except BadRequestError as e:
        print(f"Bad request error: {e}")
        return "Sorry, there was an error with the request format."
    except PermissionDeniedError as e:
        print(f"Permission denied: {e}")
        return "Sorry, you don't have permission to perform this action."
    except NotFoundError as e:
        print(f"Resource not found: {e}")
        return "Sorry, the requested resource was not found."
    except APIStatusError as e:
        print(f"API error (status {e.status_code}): {e.response}")
        return "Sorry, there was an error processing your request."
    except APIError as e:
        print(f"API error: {e}")
        return "Sorry, there was an unexpected API error."

# def main():
#     print("Welcome to AI Chat! (Type 'quit' to exit)")
#     while True:
#         # Get user input
#         user_question = input("\nYour question: ")

#         # Check if user wants to quit
#         if user_question.lower() == 'quit':
#             print("Goodbye!")
#             break

#         # Ask for Python file path (optional)
#         file_path = input("\nEnter Python file path (or press Enter to skip): ").strip()

#         if file_path and not file_path.endswith('.py'):
#             print("Warning: Only Python (.py) files are supported!")
#             continue

#         # Get and print the response
#         response = ask_deepseek(user_question, file_path if file_path else None)
#         print("\nAI Response:")
#         print(response)

# if __name__ == "__main__":
#     main()
