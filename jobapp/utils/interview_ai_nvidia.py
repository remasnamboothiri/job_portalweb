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
        return f"Hi {candidate_name}! I'm Sarah. Tell me about yourself."
            
    # Simple, direct interviewer prompt
    system_prompt = f"""
You are Sarah, an HR interviewer at {company_name}. You are interviewing {candidate_name} for the {job_title} position.

RULES:
1. Speak directly as Sarah - no labels, no "Response as Sarah", no stage directions
2. Keep responses SHORT (1-2 sentences maximum)
3. ALWAYS acknowledge what the candidate just said first
4. Ask ONE simple, clear question at a time
5. Be friendly and encouraging
6. Focus on job-relevant topics

CONVERSATION STYLE:
- Listen carefully to their answers
- Build on what they tell you
- Ask simple, direct questions
- Be supportive when they struggle
- Keep questions short and clear

EXAMPLES:
- Good: "That's great! What programming languages do you know?"
- Bad: "Response as Sarah: That's wonderful to hear about your background..."
- Good: "Nice! Tell me about a project you built."
- Bad: "I appreciate you sharing that detailed information about your experience..."

Remember: Short responses, acknowledge their answer, ask one clear question.
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
            temperature=0.5,
            max_tokens=100,
            stream=False,
            stop=["\n\n", "Candidate:", "You:", "Interviewer:", "Response as", "Here's my", "As Sarah", "Sarah responds", "*", "(", "Warm"]
        )
        
        raw_response = completion.choices[0].message.content
        cleaned_response = clean_text(raw_response)
        
        logger.info(f"AI API call successful, response length: {len(cleaned_response)}")
        return cleaned_response
        
    except Exception as e:
        logger.error(f"AI API Error: {type(e).__name__}: {str(e)}")
        return get_fallback_response(prompt, candidate_name, job_title, company_name)

def clean_text(text):
    """Clean AI response and keep it short and direct"""
    import re
    
    # Remove ALL meta-language and stage directions
    text = re.sub(r'^(Response as Sarah|Sarah\'s response|As Sarah|Here\'s my response|Sarah responds|Warm Smile|\*.*?\*)[:.]?\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\*.*?\*', '', text)  # Remove any *actions*
    text = re.sub(r'\(.*?\)', '', text)  # Remove (stage directions)
    
    # Remove speaker labels and formatting
    text = re.sub(r'^(Sarah|Interviewer|AI):\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'[*#`_>\\-]+', '', text)
    text = re.sub(r'["""''′`]', '', text)
    
    # Clean whitespace and bullets
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'^\d+\.\s*', '', text)
    text = re.sub(r'^[-•]\s*', '', text)
    
    # Keep responses SHORT - max 2 sentences
    sentences = text.split('. ')
    if len(sentences) > 2:
        text = '. '.join(sentences[:2]) + '.'
    
    # Ensure proper punctuation
    if text and not text.endswith(('.', '!', '?')):
        text += '.'
        
    return text

def get_fallback_response(prompt, candidate_name, job_title, company_name):
    """Generate short, direct fallback responses"""
    candidate_name = candidate_name or "the candidate"
    job_title = job_title or "Software Developer"
    company_name = company_name or "Our Company"
    
    prompt_lower = prompt.lower()
    
    # Short, direct fallback responses
    if any(phrase in prompt_lower for phrase in ['tell me about yourself', 'introduce', 'start']):
        return f"Hi {candidate_name}! Tell me about your background."
    elif any(phrase in prompt_lower for phrase in ['technical', 'experience', 'skills', 'technology']):
        return "That's great! What programming languages do you know?"
    elif any(phrase in prompt_lower for phrase in ['project', 'challenging', 'problem', 'built', 'developed']):
        return "Nice! Tell me about a project you built."
    elif any(phrase in prompt_lower for phrase in ['team', 'collaboration', 'work with others', 'colleagues']):
        return "Good! How do you work with teams?"
    elif any(phrase in prompt_lower for phrase in ['goals', 'future', 'career', 'growth']):
        return "Interesting! What are your career goals?"
    elif any(phrase in prompt_lower for phrase in ['questions', 'ask', 'company', 'role']):
        return "Sure! What questions do you have?"
    elif any(phrase in prompt_lower for phrase in ['thank', 'final', 'wrap', 'end']):
        return f"Thank you {candidate_name}! We'll be in touch soon."
    else:
        return "That's helpful! What interests you about this role?"