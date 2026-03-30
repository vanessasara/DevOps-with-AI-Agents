import os
import asyncio
import litellm
from dotenv import load_dotenv

load_dotenv()

async def test_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("MODEL_NAME", "gemini/gemini-1.5-flash")
    
    print(f"Testing connectivity to {model}...")
    try:
        response = await litellm.acompletion(
            model=model,
            messages=[{"role": "user", "content": "Hello, are you working?"}],
            api_key=api_key
        )
        print("✅ Success! Response:")
        print(response.choices[0].message.content)
    except Exception as e:
        print(f"❌ Failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_gemini())
