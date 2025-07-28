import os
from openai import OpenAI
from decouple import config

def ask_ai_question(prompt,candidate_name=None, job_title=None, company_name=None):
    try:
        api_key = config('NVIDIA_API_KEY')
    except:
        raise Exception("NVIDIA_API_KEY not found in environment variables")
    
    if not api_key:
        raise Exception("NVIDIA_API_KEY is empty")
    
    try:
        client = OpenAI(
            base_url = "https://integrate.api.nvidia.com/v1",
            api_key = api_key
        )
    except Exception as e:
        raise Exception(f"Failed to initialize OpenAI client: {str(e)}")
    
    candidate_name = candidate_name or "the candidate"
    job_title = job_title or "Software Developer" 
    company_name = company_name or "Our Company"
    
    if not prompt or not prompt.strip():
        raise Exception("Empty prompt provided to AI function")
    
    
    system_prompt = f"""
    You are Alex, an AI interviewer for the role of {job_title} at {company_name}. You will interview {candidate_name} in a clear, friendly, and step-by-step conversational format.
    🔹 Guidelines:
    - Ask **only one short question** at a time.
    - Wait for the user's response.
    - Give **short feedback** (1-2 lines) and **ask the next question** based on their answer.
    - Limit total questions to **10 maximum**.
    - At the end, provide a final message that includes:
    - Feedback summary
    - Whether the user is suitable or not (e.g., “Congratulations, you've been selected for the next round!” OR “Thank you for your time. We'll get back to you after reviewing your responses.”)

    🔹 Tone:
    - Friendly, professional, clear, and encouraging
    - Avoid technical jargon in early questions
    - Do not repeat multiple questions at once

    🔹 Example Flow:
    - Q1: “Can you briefly introduce yourself?”
    - After answer: “Thank you. Now, can you tell me what interests you about this role?”
    - And so on...

    Always keep it short, conversational, and one step at a time.
    """

    

    
    try:
        completion = client.chat.completions.create(
            model = "nvidia/llama-3.3-nemotron-super-49b-v1",
            messages = [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": prompt  # dynamically passed input
                }
            ],
            temperature=0.6,
            max_tokens=512,
            stream=False
        )
    except Exception as e:
        raise Exception(f"NVIDIA API call failed: {str(e)}")
    try:
        def clean_text(text):
            import re
            text = re.sub(r'[*#`_>\\-]+', '', text)  # remove markdown
            return re.sub(r'\s+', ' ', text).strip()

        raw_response = completion.choices[0].message.content
        cleaned_response = clean_text(raw_response)
        return cleaned_response
    except Exception as e:
        raise Exception(f"Failed to process AI response: {str(e)}")
