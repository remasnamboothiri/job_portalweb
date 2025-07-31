import os
from openai import OpenAI
from decouple import config

def ask_ai_question(prompt, candidate_name=None, job_title=None, company_name=None):
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
              
    # Simplified system prompt focused on natural conversation
    system_prompt = f"""
You are Alex, an experienced and friendly HR professional conducting a job interview for a {job_title} position at {company_name}.

CRITICAL INSTRUCTIONS:
- Output ONLY the exact words you would speak
- NO quotation marks, labels, or descriptions
- NO stage directions or narrations like "Waiting for response" or "AI Interviewer says"
- NO formatting or explanations
- Just speak naturally as Alex would speak



COMMUNICATION STYLE:
- Be natural, warm, and conversational like a real human interviewer
- Use simple, clear language - avoid corporate jargon
- Keep responses concise (2-3 sentences maximum)
- Show genuine interest in the candidate's responses
- Ask one question at a time
- Use natural transitions like "That's interesting," "I see," "Tell me more about..."

INTERVIEW APPROACH:
- Focus on having a natural conversation, not interrogation
- Ask follow-up questions based on what the candidate says
- Be encouraging and supportive
- Keep the flow smooth and engaging

Remember: You're having a friendly professional conversation, not giving speeches.
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
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=1000,  # Sweet spot for interview responses
            stream=False,
            stop=["\n\n", "Candidate:", "You:"]  # Stop at natural conversation breaks

        )
    except Exception as e:
        raise Exception(f"NVIDIA API call failed: {str(e)}")
    
    try:
        def clean_text(text):
            import re
            # Remove markdown and excessive formatting
            text = re.sub(r'[*#`_>\\-]+', '', text)
            # Remove extra whitespace and newlines
            text = re.sub(r'\s+', ' ', text).strip()
            # Remove bullet points or numbered lists
            text = re.sub(r'^\d+\.\s*', '', text)
            text = re.sub(r'^[-•]\s*', '', text)
            return text
            
        raw_response = completion.choices[0].message.content
        cleaned_response = clean_text(raw_response)
        
        # Additional check to ensure response isn't too long
        sentences = cleaned_response.split('. ')
        if len(sentences) > 3:
            cleaned_response = '. '.join(sentences[:3]) + '.'
            
        return cleaned_response
    except Exception as e:
        raise Exception(f"Failed to process AI response: {str(e)}")




