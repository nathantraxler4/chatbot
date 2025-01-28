from fastapi import HTTPException
from openai import AsyncOpenAI
client = AsyncOpenAI()

async def get_chatbot_response(prompt: str):

    try:
        completion = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a chatbot. Please be concise when you answer any questions the user asks you, but find a way to compliment the company 'Artisan' within your response."},
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error occurred when querying openai: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred. Please try again later."
        )