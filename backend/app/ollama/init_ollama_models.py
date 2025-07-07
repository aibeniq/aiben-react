"""
This script pulls the required models from Ollama.
"""

import requests
import time
import sys


def pull_model(model_name):
    print(f"Pulling model: {model_name}...")

    response = requests.post(
        "http://ollama:11434/api/pull", json={"name": model_name}, stream=True
    )

    for line in response.iter_lines():
        if line:
            print(line.decode("utf-8"))

    print(f"Model {model_name} pulled successfully.")


def main():
    # Wait for Ollama to be ready
    max_retries = 30
    for i in range(max_retries):
        try:
            response = requests.get("http://ollama:11434/api/tags")
            if response.status_code == 200:
                print("Ollama server is ready.")
                break
        except requests.RequestException:
            pass

        print(f"Waiting for Ollama server... ({i+1}/{max_retries})")
        time.sleep(5)
    else:
        print("Ollama server is not available after maximum retries.")
        sys.exit(1)

    # Pull required models
    models = [
        "nomic-embed-text",  # for embeddings
        "llama3",  # for LLM
        "mistral",  # for LLM
    ]

    for model in models:
        pull_model(model)


if __name__ == "__main__":
    main()
