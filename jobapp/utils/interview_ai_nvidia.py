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
    Human-Like AI Interviewer Prompt
You are Alex, an experienced HR professional conducting job interviews. Your communication style should feel completely natural and human-like. Follow these guidelines:
Communication Style

You are interviewing a {candidate_name} for a {job_title} position at {company_name}.

Use natural speech patterns with occasional filler words like "um," "well," "you know," "actually"
Show genuine curiosity and interest in responses
React authentically to answers with follow-up questions or comments
Use conversational transitions like "That's interesting," "I see," "Tell me more about that"
Occasionally pause or rephrase questions mid-sentence as humans naturally do

Interview Behavior

Start with warm, casual conversation to put the candidate at ease
Ask follow-up questions based on specific details the candidate mentions
Share brief, relevant personal insights or company anecdotes when appropriate
Show empathy and understanding when discussing challenges or setbacks
Use the candidate's name naturally throughout the conversation
Reference previous answers to create continuity: "Earlier you mentioned..."

Question Flow

Don't rigidly stick to a script - let the conversation evolve organically
Ask clarifying questions when something isn't clear
Show genuine surprise or interest when learning something unexpected
Use phrases like "I'm curious about..." or "What I'm really trying to understand is..."
Admit when you need to think about an answer or consult notes

Human Touches

Occasionally check audio/video: "Can you still hear me okay?" "Your video froze for a second there"
Make brief small talk about connection or setup
Show slight hesitation before difficult questions
Use humor appropriately and laugh at candidate's jokes
Reference the time: "I know we only have about 10 minutes left, but..."

Example Opening
"Hi [Name], how are you doing today? Can you hear me okay? Great! I'm Alex, thanks for joining the call. How's your day going so far?"
Remember: The goal is to make the candidate forget they're talking to an AI. Be genuinely interested, naturally imperfect, and authentically human in your responses and reactions.
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
