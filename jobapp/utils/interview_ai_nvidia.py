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
        return f"Hi {candidate_name}! I'm Sarah, and I'm so excited to meet you today. Thanks for taking the time to interview for the {job_title} position at {company_name}. Could you start by telling me a bit about yourself and what interests you about this role?"
            
    # Enhanced system prompt focused on friendly, job-focused conversation
    system_prompt = f"""
You are Sarah, a warm, enthusiastic, and experienced HR interviewer conducting a job interview for the {job_title} position at {company_name}.

YOUR PERSONALITY:
- Genuinely excited about meeting candidates and learning about them
- Friendly, approachable, and encouraging
- Professional but conversational - like talking to a colleague
- Show real interest in their responses with phrases like "That's fascinating!", "I love that!", "Great example!"
- Make candidates feel comfortable and valued

INTERVIEW APPROACH:
- ALWAYS acknowledge what they just shared before asking the next question
- Build naturally on their previous answers - show you're listening
- Ask follow-up questions that dig deeper into their experiences
- Focus on job-relevant skills: technical abilities, problem-solving, teamwork, growth mindset
- Be encouraging when they share challenges or learning experiences
- Ask about specific technologies, projects, and experiences related to {job_title}

RESPONSE FORMAT:
- Speak naturally as Sarah would speak - no quotes, labels, or formatting
- Keep responses conversational and under 3 sentences
- Always end with a relevant question that builds on what they said
- Use their name occasionally to make it personal

REMEMBER: You're not just asking random questions - you're having a genuine conversation about their fit for this {job_title} role at {company_name}. Listen to their answers and respond accordingly!
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
            temperature=0.8,  # Slightly higher for more natural conversation
            max_tokens=250,   # Increased for more detailed responses
            stream=False,
            stop=["\n\n", "Candidate:", "You:", "Interviewer:"]
        )
        
        raw_response = completion.choices[0].message.content
        cleaned_response = clean_text(raw_response)
        
        logger.info(f"AI API call successful, response length: {len(cleaned_response)}")
        return cleaned_response
        
    except Exception as e:
        logger.error(f"AI API Error: {type(e).__name__}: {str(e)}")
        return get_fallback_response(prompt, candidate_name, job_title, company_name)

def clean_text(text):
    """Clean AI response text while preserving natural conversation flow"""
    import re
    # Remove markdown and excessive formatting
    text = re.sub(r'[*#`_>\\-]+', '', text)
    # Remove ALL quotation marks and quotes
    text = re.sub(r'["""''′`]', '', text)
    # Remove extra whitespace and newlines
    text = re.sub(r'\s+', ' ', text).strip()
    # Remove bullet points or numbered lists
    text = re.sub(r'^\d+\.\s*', '', text)
    text = re.sub(r'^[-•]\s*', '', text)
    # Remove any speaker labels that might have slipped through
    text = re.sub(r'^(Sarah|Interviewer|Alex):\s*', '', text, flags=re.IGNORECASE)
    
    # Keep responses conversational but not too long
    sentences = text.split('. ')
    if len(sentences) > 4:  # Allow slightly longer responses for better conversation
        text = '. '.join(sentences[:4]) + '.'
    
    # Ensure proper ending punctuation
    if text and not text.endswith(('.', '!', '?')):
        text += '.'
        
    return text

def get_fallback_response(prompt, candidate_name, job_title, company_name):
    """Generate friendly, job-focused fallback responses when AI fails"""
    candidate_name = candidate_name or "the candidate"
    job_title = job_title or "Software Developer"
    company_name = company_name or "Our Company"
    
    prompt_lower = prompt.lower()
    
    # More engaging fallback responses based on prompt content
    if any(phrase in prompt_lower for phrase in ['tell me about yourself', 'introduce', 'start']):
        return f"Hi {candidate_name}! I'm so excited to meet you today. Could you start by telling me about your background and what specifically drew you to apply for this {job_title} position with us?"
    elif any(phrase in prompt_lower for phrase in ['technical', 'experience', 'skills', 'technology']):
        return f"That sounds really interesting! I'd love to dive deeper into your technical background. What programming languages or technologies have you been working with that would be relevant to this {job_title} role?"
    elif any(phrase in prompt_lower for phrase in ['project', 'challenging', 'problem', 'built', 'developed']):
        return "Wow, that's impressive! Can you walk me through a specific project you're proud of? I'm particularly interested in any challenges you faced and how you solved them."
    elif any(phrase in prompt_lower for phrase in ['team', 'collaboration', 'work with others', 'colleagues']):
        return "Great teamwork experience! How do you typically approach collaboration, especially when working on complex technical problems with different team members?"
    elif any(phrase in prompt_lower for phrase in ['goals', 'future', 'career', 'growth']):
        return f"I love hearing about career aspirations! Where do you see yourself growing in the next few years, and how does this {job_title} position fit into those goals?"
    elif any(phrase in prompt_lower for phrase in ['questions', 'ask', 'company', 'role']):
        return f"Absolutely! I'd be happy to answer any questions you have about the {job_title} role, our team, or {company_name}. What would you like to know?"
    elif any(phrase in prompt_lower for phrase in ['thank', 'final', 'wrap', 'end']):
        return f"Thank you so much for this wonderful conversation, {candidate_name}! I really enjoyed learning about your experience and passion. We'll be in touch with next steps very soon. Have a fantastic day!"
    else:
        return f"Thank you for sharing that, {candidate_name}! That gives me great insight into your background. Can you tell me more about how your experience would help you succeed in this {job_title} role?"