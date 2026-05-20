from openai import OpenAI

conversation_history = {}
max_history = 20
system_prompt = "You are a personal assistant inside an SMS bot. Use plain text only — no bold, no markdown. For conversational questions, keep answers to 1-3 sentences. For data like times, lists, or schedules, format clearly across multiple lines."

tools = [
    {"type": "openrouter:web_search"},
    {"type": "openrouter:web_fetch"},
    {"type": "openrouter:datetime"}
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
        max_tokens=350,
        messages=conversation_history[phone_number],
        tools=tools
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

