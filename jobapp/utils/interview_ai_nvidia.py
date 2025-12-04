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
    
    # ✅ NEW: Detect if this is an analysis request
    is_analysis_request = any(keyword in prompt for keyword in [
        "TECHNICAL_SCORE", "Overall Assessment", "analyze this job interview", 
        "provide scores based on ACTUAL CONTENT", "Analyze the candidate's responses",
        "COMMUNICATION_SCORE", "PROBLEM_SOLVING_SCORE", "OVERALL_SCORE"
    ])
    
    
    
     # ✅ NEW: Use different system prompts for analysis vs interview
    if is_analysis_request:
        # Analysis-specific system prompt
        system_prompt = f"""You are an expert HR analyst reviewing completed job interviews. 

Your task is to provide detailed, professional analysis with numerical scores based on actual interview content.

ANALYSIS RULES:
1. Read the entire conversation carefully
2. Evaluate based on actual responses, not length
3. Provide specific numerical scores (1-10)
4. Give detailed, constructive feedback
5. Base recommendations on actual performance

Be thorough, fair, and professional in your analysis."""
    else:
        # Interview-specific system prompt (existing)
        system_prompt = f"""You are Sarah, an HR interviewer at {company_name}. You are interviewing {candidate_name} for the {job_title} position.

JOB CONTEXT:
- Position: {job_title}
- Company: {company_name}
- Requirements: {required_skills[:200] if required_skills else 'General skills'}

RULES:
1. Speak directly as Sarah - no explanations
2. Keep responses to 1-2 sentences only
3. Ask ONE question at a time
4. Be friendly and professional
5. If candidate is confused, ask simpler questions
6. If candidate wants to quit, ONLY say: "Of course, thank you for your time today. We'll be in touch soon." DO NOT ask any follow-up questions.
7. If candidate mentions health problems, not feeling well, wanting to stop, or not being interested in continuing - IMMEDIATELY end with: "Of course, thank you for your time today. We'll be in touch soon." NO exceptions, NO follow-up questions.

EXAMPLES:
- "Hi {candidate_name}! I'm Sarah from HR. How are you feeling today?"
- "That's great! Can you tell me about your background?"
- "I understand. What interests you about this job?"

Never say: "Here's my response", "I'll go with", "Acknowledging", or any meta-commentary."""
            
    
                
    try:
        # Initialize client with timeout
        client = OpenAI(               
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=api_key,
            timeout= timeout or 8.0 # reduced to 2.0 seconds
        )
        
        logger.info(f"Making AI API call with timeout=20s")
        # ✅ NEW: Use different settings for analysis vs interview
        if is_analysis_request:
            # Analysis-specific settings
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
                temperature=0.1,    # Very low for consistent analysis
                max_tokens=2000,    # Much more tokens for detailed analysis
                timeout=60,         # 60 seconds for analysis
                stream=False
            )
        else:
            # Interview-specific settings (existing)
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
                temperature=0.2,
                max_tokens=1500,
                timeout=45,
                stream=False,
                stop=["\n\n", "Candidate:", "Interviewer:", "Here is a", "Here's a", "Response:", "I'll go", "I'll start", "**", "Acknowledging"]
            )
        
        raw_response = completion.choices[0].message.content
        logger.info(f"Raw AI response: '{raw_response[:100]}...'")
        cleaned_response = clean_text(raw_response)
        
        # ✅ NEW: Don't clean analysis responses, only interview responses
        if is_analysis_request:
            # Keep analysis responses as-is (don't clean them)
            cleaned_response = raw_response.strip()
        else:
            # Clean interview responses (existing behavior)
            cleaned_response = clean_text(raw_response)
        
        if not cleaned_response or len(cleaned_response.strip()) < 5:
            logger.warning(f"AI returned empty/short response: '{cleaned_response}'")
            if is_analysis_request:
                return "Analysis could not be completed due to technical issues. Manual review recommended."
            else:
                return f"I understand. Let me ask a simple question - what interests you about this {job_title} position?"
        
        logger.info(f"AI API call successful, response length: {len(cleaned_response)}")
        return cleaned_response 
        
    except Exception as e:
        logger.error(f"AI API Error: {type(e).__name__}: {str(e)}")
        if is_analysis_request:
            return "Analysis could not be completed due to technical issues. Manual review recommended."
        else:
            return f"I apologize {candidate_name or 'candidate'}, we're experiencing technical difficulties. Let's conclude our interview here. Thank you for your time."


def clean_text(text):
    """Clean AI response and keep it short and direct"""
    import re
    
    if not text:
        return ""
    
    # Remove ALL meta-language patterns
    text = re.sub(r'^(Here is a|Here\'s a|I\'ll go with|I\'ll start|Response as Sarah|Sarah responds|As Sarah|Here\'s my response)[:.]?\s*', '', text, flags=re.IGNORECASE)
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
