from openai import OpenAI

conversation_history = {}
max_history = 20
system_prompt = ""

tools = [
    {"type": "web_search"},
    {"type": "web_fetch"},
    {"type": "datetime"}
]


def ask_ai(prompt, phone_number, client):

    # Create new list if first message from this phone number
    if phone_number not in conversation_history:
        conversation_history[phone_number] = [
            {"role": "system", "content": system_prompt}
        ]

    conversation_history[phone_number].append({
        "role": "user",
        "content" : prompt
    })

    response = client.chat.completions.create(
        model="google/gemini-3.1-flash-lite",
        max_tokens=400,
        messages=conversation_history[phone_number]
        #tools=tools
        # Removed due to twilio latency limitations, the tools would take too long to formulate a response
    )

    AI_response = response.choices[0].message.content

    conversation_history[phone_number].append({
        "role": "assistant",
        "content" : AI_response
    })
    
    if len(conversation_history[phone_number]) > max_history:
        conversation_history[phone_number] = [conversation_history[phone_number][0]] + conversation_history[phone_number][-(max_history - 1):]

    return AI_response


def clear_history(phone_number):
    if phone_number in conversation_history:
        del conversation_history[phone_number]
        return "Conversation history cleared!"
    return "No history to clear."

