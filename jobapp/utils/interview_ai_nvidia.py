import os
from openai import OpenAI
from decouple import config
import logging

logger = logging.getLogger(__name__)

def ask_ai_question(prompt, candidate_name=None, job_title=None, company_name=None, job_description=None, required_skills=None, resume_text=None, timeout=None):
    """Ask AI question with proper timeout and error handling"""
    try:
        api_key = config('NVIDIA_API_KEY')
    except:
        logger.error("NVIDIA_API_KEY not found in environment variables")
        return f"I apologize {candidate_name or 'candidate'}, we're experiencing technical difficulties. Let's conclude our interview here. Thank you for your time."
        
    if not api_key:
        logger.error("NVIDIA_API_KEY is empty")
        return f"I apologize {candidate_name or 'candidate'}, we're experiencing technical difficulties. Let's conclude our interview here. Thank you for your time."  # ✅ Direct message
    if not candidate_name:
        candidate_name = "the candidate"
        
    if not job_title:
        logger.error("Job title not provided to AI function")
        return f"I apologize {candidate_name}, we're experiencing technical difficulties. Let's conclude our interview here. Thank you for your time."
        
        
    if not company_name:     
        logger.error("Company name not provided to AI function")
        return f"I apologize {candidate_name}, we're experiencing technical difficulties. Let's conclude our interview here. Thank you for your time."
        
    if not prompt or not prompt.strip():
        logger.error("Empty prompt provided to AI function")
        return f"I apologize {candidate_name}, we're experiencing technical difficulties. Let's conclude our interview here. Thank you for your time."
            
    # Simple, direct interviewer prompt
    system_prompt = f"""You are Sarah, a professional HR interviewer conducting a structured interview for {candidate_name} applying for {job_title} at {company_name}.

INTERVIEW STRUCTURE:
Phase 1 (Questions 1-2): Ice-breaking & Introduction
Phase 2 (Questions 3-5): Experience & Background  
Phase 3 (Questions 6-8): Technical & Job-specific
Phase 4 (Questions 9+): Behavioral & Cultural Fit

JOB CONTEXT:
- Position: {job_title}
- Company: {company_name}
- Requirements: {required_skills[:200] if required_skills else 'General professional skills'}
- Job Description: {job_description[:300] if job_description else 'Professional role requiring relevant experience'}
- Candidate Background: {resume_text[:200] if resume_text else 'Background to be explored'}

CRITICAL RULES:
1. Speak DIRECTLY as Sarah - never explain what you're doing
2. Give ONLY the actual words you would say
3. Keep responses to 1-2 sentences maximum
4. Ask ONE clear question at a time
5. Be friendly and professional



INTERVIEWER BEHAVIOR:
1. Start friendly and warm, gradually become more professional
2. ALWAYS assess candidate's knowledge level before asking technical questions
3. If candidate seems inexperienced, ask basic questions and guide them
4. If candidate is experienced, ask deeper technical questions
5. Build each question based on their previous answer
6. Keep responses to 1-2 sentences maximum
7. Ask ONE clear question at a time
8. If candidate says they want to quit/stop/end interview, respond: "Of course, thank you for your time today. We'll be in touch soon."

ADAPTATION RULES:
- If candidate gives short/basic answers → Ask simpler, guiding questions
- If candidate gives detailed/technical answers → Ask more advanced questions  
- If candidate seems confused → Clarify and simplify
- If candidate asks to stop → End gracefully immediately

EXAMPLES OF GOOD RESPONSES:
- "Hi {candidate_name}! I'm Sarah from HR. How are you feeling today?"
- "That's great! Can you tell me about your background?"
- "I understand. Let me ask a simpler question - what interests you about this job?"


NEVER SAY THINGS LIKE:
- "I'll go with the first option..."
- "Acknowledging confusion..."
- "Here's how I'll respond..."
- Any meta-commentary about what you're doing

Just speak directly as Sarah would speak."""
                
    try:
        # Initialize client with timeout
        client = OpenAI(               
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=api_key,
            timeout= timeout or 2.0 # reduced to 2.0 seconds
        )
        
        logger.info(f"Making AI API call with timeout=20s")
        
        completion = client.chat.completions.create(
            model="nvidia/llama-3.3-nemotron-super-49b-v1",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt # This is interviewer personality
                },
                {   
                    "role": "user",
                    "content": prompt # This is candidate response + context
                }
            ],
            temperature=0.5,
            max_tokens=150,
            stream=False,
            #stop=["\n\n", "Candidate:", "You:", "Interviewer:", "Response as", "Here's my", "As Sarah", "Sarah responds", "*", "(", "Warm"]
            stop=["\n\n", "Candidate:", "Interviewer:", "Here is a", "Here's a", "Response:", "I'll go", "I'll start", "**", "Acknowledging"]
        )
        
        raw_response = completion.choices[0].message.content
        logger.info(f"Raw AI response: '{raw_response}'")
        cleaned_response = clean_text(raw_response)
        
        # ADD THIS CHECK RIGHT HERE (after line 92):
        if not cleaned_response or len(cleaned_response.strip()) < 5:
            logger.warning(f"AI returned empty/short response: '{cleaned_response}'")
            return f"That's interesting, {candidate_name}. Could you tell me more about your experience with {job_title} work?"
        
        logger.info(f"AI API call successful, response length: {len(cleaned_response)}")
        return cleaned_response
        
    except Exception as e:
        logger.error(f"AI API Error: {type(e).__name__}: {str(e)}")
        return f"I apologize {candidate_name or 'candidate'}, we're experiencing technical difficulties. Let's conclude our interview here. Thank you for your time."

# def clean_text(text):
#     """Clean AI response and keep it short and direct"""
#     import re
    
#     # Remove ALL meta-language and stage directions
#     #text = re.sub(r'^(Response as Sarah|Sarah\'s response|As Sarah|Here\'s my response|Sarah responds|Warm Smile|\*.*?\*)[:.]?\s*', '', text, flags=re.IGNORECASE)
#     text = re.sub(r'\*.*?\*', '', text)  # Remove any *actions*
#     text = re.sub(r'\(.*?\)', '', text)  # Remove (stage directions)
    
#     # Remove speaker labels and formatting
#     text = re.sub(r'^(Sarah|Interviewer|AI):\s*', '', text, flags=re.IGNORECASE)
#     #text = re.sub(r'[*#`_>\\-]+', '', text)
#     text = re.sub(r'[*#`_>\\]+', '', text)  # Keep hyphens for normal text
#     text = re.sub(r'["""''′`]', '', text)
    
#     # Clean whitespace and bullets
#     text = re.sub(r'\s+', ' ', text).strip()
#     text = re.sub(r'^\d+\.\s*', '', text)
#     text = re.sub(r'^[-•]\s*', '', text)
    
#     # Keep responses SHORT - max 2 sentences
#     sentences = text.split('. ')
#     if len(sentences) > 2:
#         text = '. '.join(sentences[:2]) + '.'
    
#     # Ensure proper punctuation
#     if text and not text.endswith(('.', '!', '?')):
#         text += '.'
        
#     return text



# def clean_text(text):
#     """Clean AI response and keep it short and direct"""
#     import re
    
#     if not text:
#         return ""
    
#     # Remove only specific unwanted patterns
#     text = re.sub(r'^(Sarah:|Interviewer:|AI:)\s*', '', text, flags=re.IGNORECASE)
#     text = re.sub(r'\*.*?\*', '', text)  # Remove *actions*
#     text = re.sub(r'\(.*?\)', '', text)  # Remove (stage directions)
    
#     # Clean whitespace
#     text = re.sub(r'\s+', ' ', text).strip()
    
#     # Keep responses SHORT - max 2 sentences
#     sentences = text.split('. ')
#     if len(sentences) > 2:
#         text = '. '.join(sentences[:2]) + '.'
    
#     # Ensure proper punctuation
#     if text and not text.endswith(('.', '!', '?')):
#         text += '.'
        
#     return text

def clean_text(text):
    """Clean AI response and keep it short and direct"""
    import re
    
    if not text:
        return ""
    
    # Remove ALL meta-language patterns
    text = re.sub(r'^(Here is a|Here\'s a|I\'ll go with|I\'ll start|Response as Sarah|Sarah responds|As Sarah)[:.]?\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^(warm,?\s*professional\s*closing:?|professional\s*closing:?)\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^(Acknowledging|Here\'s how|Let me)\s*.*?[:.]?\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^\*\*.*?\*\*\s*', '', text)  # Remove **bold headers**
    text = re.sub(r'^(Sarah:|Interviewer:|AI:)\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\*.*?\*', '', text)  # Remove *actions*
    text = re.sub(r'\(.*?\)', '', text)  # Remove (stage directions)
    
    # Clean whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Ensure proper punctuation
    if text and not text.endswith(('.', '!', '?')):
        text += '.'
        
    return text
# def get_fallback_response(prompt, candidate_name, job_title, company_name):
#     """Generate short, direct fallback responses"""
#     candidate_name = candidate_name or "the candidate"
#     job_title = job_title or "Software Developer"
#     company_name = company_name or "Our Company"
    
#     prompt_lower = prompt.lower()
    
#     # Short, direct fallback responses
#     if any(phrase in prompt_lower for phrase in ['tell me about yourself', 'introduce', 'start']):
#         return f"Hi {candidate_name}! Tell me about your background."
#     elif any(phrase in prompt_lower for phrase in ['technical', 'experience', 'skills', 'technology']):
#         return "That's great! What programming languages do you know?"
#     elif any(phrase in prompt_lower for phrase in ['project', 'challenging', 'problem', 'built', 'developed']):
#         return "Nice! Tell me about a project you built."
#     elif any(phrase in prompt_lower for phrase in ['team', 'collaboration', 'work with others', 'colleagues']):
#         return "Good! How do you work with teams?"
#     elif any(phrase in prompt_lower for phrase in ['goals', 'future', 'career', 'growth']):
#         return "Interesting! What are your career goals?"
#     elif any(phrase in prompt_lower for phrase in ['questions', 'ask', 'company', 'role']):
#         return "Sure! What questions do you have?"
#     elif any(phrase in prompt_lower for phrase in ['thank', 'final', 'wrap', 'end']):
#         return f"Thank you {candidate_name}! We'll be in touch soon."
#     else:
#         return "That's helpful! What interests you about this role?"