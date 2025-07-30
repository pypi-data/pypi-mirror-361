#!/usr/bin/env python3

import asyncio
import os
from universal_llm import get_client, Settings


async def main():
    settings = Settings(
        provider="google",
        model="gemini-2.0-flash",
        api_key=os.getenv("GOOGLE_API_KEY")
    )

    if not settings.api_key:
        print("Please set GOOGLE_API_KEY environment variable")
        return

    client = get_client(settings)

    print("Starting conversation with Gemini...")
    print("Type 'quit' to exit\n")

    conversation_history = []

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            break

        conversation_history.append({"role": "user", "content": user_input})

        try:
            response = await client.chat(conversation_history)
            print(f"Assistant: {response}\n")
            conversation_history.append({"role": "assistant", "content": response})
        except Exception as e:
            print(f"Error: {e}\n")


def test_sync():
    settings = Settings(
        provider="google",
        model="gemini-2.0-flash",
        api_key=os.getenv("GOOGLE_API_KEY")
    )

    if not settings.api_key:
        print("Please set GOOGLE_API_KEY environment variable")
        return

    client = get_client(settings)

    messages = [{"role": "user", "content": "Hello! Can you tell me a short joke?"}]

    print("Testing sync conversation...")
    try:
        response = client.chat_sync(messages)
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print("Choose test mode:")
    print("1. Interactive conversation (async)")
    print("2. Simple sync test")

    choice = input("Enter choice (1 or 2): ")

    if choice == "1":
        asyncio.run(main())
    elif choice == "2":
        test_sync()
    else:
        print("Invalid choice")
