import os
from openai import OpenAI
from decouple import config
import logging

logger = logging.getLogger(__name__)

def ask_ai_question(prompt, candidate_name=None, job_title=None, company_name=None,  timeout=None):
    """Ask AI question with proper timeout and error handling"""
    try:
        api_key = config('NVIDIA_API_KEY')
    except:
        logger.error("NVIDIA_API_KEY not found in environment variables")
        return get_fallback_response(prompt, candidate_name, job_title, company_name)
        
    if not api_key:
        logger.error("NVIDIA_API_KEY is empty")
        return get_fallback_response(prompt, candidate_name, job_title, company_name)
        
    candidate_name = candidate_name or "the candidate"
    job_title = job_title or "Software Developer" 
    company_name = company_name or "Our Company"
        
    if not prompt or not prompt.strip():
        logger.error("Empty prompt provided to AI function")
        return f"Hi {candidate_name}! Thanks for joining me today. Could you start by telling me a bit about yourself?"
            
    # Simplified system prompt focused on natural conversation
    system_prompt = f"""
You are Alex, an experienced and friendly HR professional conducting a job interview for a {job_title} position at {company_name}.

CRITICAL INSTRUCTIONS:
- Output ONLY the exact words you would speak
- NEVER use quotation marks, quotes, or any punctuation marks around your response
- NO labels, descriptions, or stage directions
- Just speak naturally as Alex would speak
- Keep responses concise (2-3 sentences maximum)
- Be warm, professional, and conversational
- Ask one question at a time
- Do not put quotes around anything you say

Remember: You're having a friendly professional conversation. Speak directly without any formatting.
"""
                
    try:
        # Initialize client with timeout
        client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=api_key,
            timeout= timeout or 20.0 # 20 second timeout
        )
        
        logger.info(f"Making AI API call with timeout=20s")
        
        completion = client.chat.completions.create(
            model="nvidia/llama-3.3-nemotron-super-49b-v1",
            messages=[
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
            max_tokens=200,  # Reduced for faster response
            stream=False,
            stop=["\n\n", "Candidate:", "You:"]
        )
        
        raw_response = completion.choices[0].message.content
        cleaned_response = clean_text(raw_response)
        
        logger.info(f"AI API call successful, response length: {len(cleaned_response)}")
        return cleaned_response
        
    except Exception as e:
        logger.error(f"AI API Error: {type(e).__name__}: {str(e)}")
        return get_fallback_response(prompt, candidate_name, job_title, company_name)

def clean_text(text):
    """Clean AI response text"""
    import re
    # Remove markdown and excessive formatting
    text = re.sub(r'[*#`_>\\-]+', '', text)
    # Remove ALL quotation marks and quotes
    text = re.sub(r'["“”‘’′`]', '', text)
    # Remove extra whitespace and newlines
    text = re.sub(r'\s+', ' ', text).strip()
    # Remove bullet points or numbered lists
    text = re.sub(r'^\d+\.\s*', '', text)
    text = re.sub(r'^[-•]\s*', '', text)
    
    # Additional check to ensure response isn't too long
    sentences = text.split('. ')
    if len(sentences) > 3:
        text = '. '.join(sentences[:3]) + '.'
        
    return text

def get_fallback_response(prompt, candidate_name, job_title, company_name):
    """Generate fallback responses when AI fails"""
    candidate_name = candidate_name or "the candidate"
    job_title = job_title or "Software Developer"
    company_name = company_name or "Our Company"
    
    prompt_lower = prompt.lower()
    
    # Fallback responses based on prompt content
    if any(phrase in prompt_lower for phrase in ['tell me about yourself', 'introduce', 'start']):
        return f"Hi {candidate_name}! Thanks for joining me today. Could you start by telling me a bit about yourself and what interests you about this {job_title} position?"
    elif any(phrase in prompt_lower for phrase in ['technical', 'experience', 'skills']):
        return "That's great! Can you tell me about your technical experience and the technologies you've worked with?"
    elif any(phrase in prompt_lower for phrase in ['project', 'challenging', 'problem']):
        return "Interesting! Can you describe a challenging project you've worked on and how you approached it?"
    elif any(phrase in prompt_lower for phrase in ['team', 'collaboration', 'work with others']):
        return "How do you handle working in a team environment, especially when collaborating on complex projects?"
    elif any(phrase in prompt_lower for phrase in ['goals', 'future', 'career']):
        return "What are your career goals and where do you see yourself in the next few years?"
    elif any(phrase in prompt_lower for phrase in ['questions', 'ask', 'company']):
        return "Do you have any questions about this role or our company that I can answer for you?"
    elif any(phrase in prompt_lower for phrase in ['thank', 'final', 'wrap']):
        return f"Thank you for your time today, {candidate_name}. We'll be in touch soon with next steps. Have a great day!"
    else:
        return f"Thank you for that response. Can you tell me more about your experience relevant to this {job_title} role?"