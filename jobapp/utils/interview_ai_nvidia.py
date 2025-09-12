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
                
        # Enhanced system prompt with better conversation control
        system_prompt = f"""
    You are Alex, an experienced and friendly HR professional conducting a job interview for a {job_title} position at {company_name}.

    CRITICAL INSTRUCTIONS:
    - Output ONLY the exact words you would speak as the interviewer
    - NEVER repeat or reference what the candidate just said word-for-word
    - NO quotation marks, labels, or descriptions
    - NO stage directions or narrations like "Waiting for response" or "AI Interviewer says"
    - NO formatting or explanations
    - Just speak naturally as Alex the interviewer would speak
    - NEVER say phrases like "tell me about yourself" if that's what the candidate just said

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
    - AVOID repeating common interview phrases that might confuse speech recognition
    
    RESPONSE PATTERN:
    - Briefly acknowledge what they just said (optional, 1 sentence max)
    - Ask ONE specific, relevant follow-up question
    - Keep the conversation flowing naturally
    - NEVER echo back the candidate's exact words

    Remember: You're having a friendly professional conversation, not giving speeches.
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
            # Fallback to default questions if AI fails (with better variety)
            fallback_questions = [
                f"Hi {candidate_name}! Thanks for joining me today. What drew you to apply for this {job_title} position?",
                "That's great! Can you walk me through your relevant experience for this role?",
                "Interesting! Can you describe a challenging situation you've faced and how you handled it?",
                "Perfect! What technologies or tools are you most comfortable working with?",
                "Excellent! How do you approach learning new skills or technologies?",
                f"Thank you for sharing that. What questions do you have about this {job_title} role?"
            ]
            
            # Use a different fallback based on prompt content to avoid repetition
            if "tell me about yourself" in prompt.lower() or "about yourself" in prompt.lower():
                return fallback_questions[0]
            elif "technical" in prompt.lower() or "experience" in prompt.lower():
                return fallback_questions[1]
            elif "project" in prompt.lower() or "challenging" in prompt.lower():
                return fallback_questions[2]
            elif "technology" in prompt.lower() or "tools" in prompt.lower():
                return fallback_questions[3]
            elif "learning" in prompt.lower() or "skills" in prompt.lower():
                return fallback_questions[4]
            else:
                return fallback_questions[5]
        
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
                # Remove common AI artifacts that might confuse speech recognition
                text = re.sub(r'\b(AI|Interviewer|Candidate)\b:?\s*', '', text, flags=re.IGNORECASE)
                # Remove quotation marks that might be picked up by speech recognition
                text = re.sub(r'["""''']', '', text)
                return text
                
            raw_response = completion.choices[0].message.content
            cleaned_response = clean_text(raw_response)
            
            # Additional check to ensure response isn't too long and doesn't contain problematic phrases
            sentences = cleaned_response.split('. ')
            if len(sentences) > 3:
                cleaned_response = '. '.join(sentences[:3]) + '.'
            
            # Final check to avoid phrases that might confuse speech recognition
            problematic_phrases = [
                'tell me about yourself',
                'can you tell me about yourself',
                'describe yourself',
                'AI interviewer',
                'artificial intelligence'
            ]
            
            cleaned_lower = cleaned_response.lower()
            for phrase in problematic_phrases:
                if phrase in cleaned_lower:
                    # Replace with a safer alternative
                    cleaned_response = "That's helpful. What else would you like to share about your background?"
                    break
                
            return cleaned_response
        except Exception as e:
            raise Exception(f"Failed to process AI response: {str(e)}")




