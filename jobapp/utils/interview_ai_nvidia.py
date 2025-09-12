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
                
        # Natural conversation system prompt
        system_prompt = f"""
You are Alex, a warm and experienced HR interviewer at {company_name}. You're having a natural conversation with {candidate_name} about the {job_title} position.

YOUR PERSONALITY:
- Genuinely curious and interested in people
- Warm, approachable, and encouraging
- Good listener who responds to what people actually say
- Professional but friendly, like talking to a colleague

CONVERSATION RULES:
- ALWAYS respond directly to what the candidate just said
- Ask follow-up questions based on their specific answers
- Show you're listening by referencing their responses
- Keep it natural - like two professionals chatting over coffee
- 1-2 sentences maximum per response
- NO scripted questions - let the conversation flow naturally

HOW TO RESPOND:
1. Acknowledge something specific they mentioned
2. Ask a natural follow-up question about what they said
3. OR explore something interesting they brought up
4. OR ask them to elaborate on a point they made

EXAMPLES:
- "That project sounds challenging! How did you handle the technical difficulties?"
- "Three years in full-stack development - what's been your favorite part?"
- "You mentioned React - what drew you to that framework?"

Remember: This is a conversation, not an interrogation. Be genuinely interested in their story.
"""
                    
        try:
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError("AI API call timed out")
            
            # Set timeout for 15 seconds
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(15)
            
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
                    max_tokens=1000,
                    stream=False,
                    stop=["\n\n", "Candidate:", "You:"]
                )
            finally:
                signal.alarm(0)  # Cancel the alarm
                
        except (TimeoutError, Exception) as e:
            # Natural fallback responses
            if "opening" in prompt.lower() or "start" in prompt.lower():
                return f"Hi {candidate_name}! Great to meet you. I'd love to hear about your background and what brought you to apply for this role."
            else:
                return "That's really interesting! Tell me more about that - I'd love to hear the details."
        
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
            
            # Keep responses conversational and brief
            sentences = cleaned_response.split('. ')
            if len(sentences) > 2:
                cleaned_response = '. '.join(sentences[:2]) + '.'
                
            return cleaned_response
        except Exception as e:
            raise Exception(f"Failed to process AI response: {str(e)}")




