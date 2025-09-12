/**
 * Speech Isolation Fix for AI Interview System
 * Prevents Mike's (AI interviewer) questions from being transcribed as candidate responses
 */

class SpeechIsolationManager {
    constructor() {
        this.isAISpeaking = false;
        this.speechBuffer = [];
        this.lastAIResponse = '';
        this.candidateResponseStartTime = null;
        this.minimumResponseGap = 2000; // 2 seconds minimum gap after AI speech
    }

    // Initialize the speech isolation system
    initialize() {
        console.log('🛡️ Speech Isolation Manager initialized');
        this.setupAIAudioMonitoring();
        this.setupSpeechFiltering();
    }

    // Monitor AI audio playback
    setupAIAudioMonitoring() {
        const aiAudio = document.getElementById('aiAudio');
        if (!aiAudio) return;

        aiAudio.addEventListener('play', () => {
            this.isAISpeaking = true;
            this.candidateResponseStartTime = null;
            console.log('🔊 AI started speaking - candidate input blocked');
        });

        aiAudio.addEventListener('ended', () => {
            this.isAISpeaking = false;
            this.candidateResponseStartTime = Date.now() + this.minimumResponseGap;
            console.log('🔇 AI stopped speaking - candidate input will be allowed after gap');
        });

        aiAudio.addEventListener('pause', () => {
            this.isAISpeaking = false;
            this.candidateResponseStartTime = Date.now() + this.minimumResponseGap;
        });
    }

    // Setup advanced speech filtering
    setupSpeechFiltering() {
        // Override the global speech result handler
        const originalHandler = window.handleSpeechResult;
        window.handleSpeechResult = (event) => {
            if (this.shouldBlockSpeechInput()) {
                console.log('🚫 Speech input blocked by isolation manager');
                return;
            }
            
            // Filter the speech results before processing
            const filteredEvent = this.filterSpeechEvent(event);
            if (filteredEvent && originalHandler) {
                originalHandler(filteredEvent);
            }
        };
    }

    // Determine if speech input should be blocked
    shouldBlockSpeechInput() {
        // Block if AI is currently speaking
        if (this.isAISpeaking) {
            return true;
        }

        // Block if we're still in the minimum gap period after AI speech
        if (this.candidateResponseStartTime && Date.now() < this.candidateResponseStartTime) {
            return true;
        }

        return false;
    }

    // Filter speech recognition event to remove AI-like content
    filterSpeechEvent(event) {
        const filteredResults = [];
        
        for (let i = 0; i < event.results.length; i++) {
            const result = event.results[i];
            const transcript = result[0].transcript;
            
            if (this.isLikelyCandidateSpeech(transcript)) {
                filteredResults.push(result);
            } else {
                console.log('🗑️ Filtered out AI-like speech:', transcript);
            }
        }

        // If no valid results remain, return null
        if (filteredResults.length === 0) {
            return null;
        }

        // Create a new event-like object with filtered results
        return {
            results: filteredResults,
            resultIndex: event.resultIndex
        };
    }

    // Determine if speech is likely from candidate vs AI
    isLikelyCandidateSpeech(transcript) {
        if (!transcript || transcript.trim().length < 2) {
            return false;
        }

        const text = transcript.toLowerCase().trim();
        
        // AI interviewer phrases that should be filtered out
        const aiIndicators = [
            // Greetings and introductions
            'hello', 'hi there', 'welcome', 'thanks for joining',
            'good morning', 'good afternoon', 'good evening',
            
            // Common interviewer questions
            'tell me about yourself', 'can you tell me about',
            'describe your experience', 'what interests you',
            'why do you want', 'what drew you to',
            
            // Interviewer responses and transitions
            'that\'s great', 'that\'s interesting', 'excellent',
            'perfect', 'wonderful', 'fantastic',
            'i see', 'i understand', 'that makes sense',
            'moving on', 'next question', 'let\'s talk about',
            
            // Interview structure phrases
            'any questions for me', 'questions about the role',
            'questions about the company', 'thank you for your time',
            'we\'ll be in touch', 'next steps',
            
            // AI/System identifiers
            'alex', 'ai interviewer', 'artificial intelligence',
            'interviewer', 'hr professional'
        ];

        // Check for AI indicators
        let aiScore = 0;
        for (const indicator of aiIndicators) {
            if (text.includes(indicator)) {
                aiScore++;
            }
        }

        // If multiple AI indicators found, likely AI speech
        if (aiScore >= 2) {
            return false;
        }

        // Check for very short responses that might be audio artifacts
        if (text.length < 5 && !this.isValidShortResponse(text)) {
            return false;
        }

        // Check if it's too similar to the last AI response
        if (this.lastAIResponse && this.calculateSimilarity(text, this.lastAIResponse.toLowerCase()) > 0.7) {
            return false;
        }

        return true;
    }

    // Check if short response is valid (like "yes", "no", "okay")
    isValidShortResponse(text) {
        const validShortResponses = [
            'yes', 'no', 'okay', 'ok', 'sure', 'right',
            'well', 'so', 'um', 'uh', 'ah', 'hmm'
        ];
        return validShortResponses.includes(text);
    }

    // Calculate similarity between two strings
    calculateSimilarity(str1, str2) {
        const longer = str1.length > str2.length ? str1 : str2;
        const shorter = str1.length > str2.length ? str2 : str1;
        
        if (longer.length === 0) {
            return 1.0;
        }
        
        const editDistance = this.levenshteinDistance(longer, shorter);
        return (longer.length - editDistance) / longer.length;
    }

    // Calculate Levenshtein distance
    levenshteinDistance(str1, str2) {
        const matrix = [];
        
        for (let i = 0; i <= str2.length; i++) {
            matrix[i] = [i];
        }
        
        for (let j = 0; j <= str1.length; j++) {
            matrix[0][j] = j;
        }
        
        for (let i = 1; i <= str2.length; i++) {
            for (let j = 1; j <= str1.length; j++) {
                if (str2.charAt(i - 1) === str1.charAt(j - 1)) {
                    matrix[i][j] = matrix[i - 1][j - 1];
                } else {
                    matrix[i][j] = Math.min(
                        matrix[i - 1][j - 1] + 1,
                        matrix[i][j - 1] + 1,
                        matrix[i - 1][j] + 1
                    );
                }
            }
        }
        
        return matrix[str2.length][str1.length];
    }

    // Store the last AI response for comparison
    setLastAIResponse(response) {
        this.lastAIResponse = response;
        console.log('📝 Stored AI response for filtering:', response.substring(0, 50) + '...');
    }

    // Reset the isolation state
    reset() {
        this.isAISpeaking = false;
        this.candidateResponseStartTime = null;
        this.lastAIResponse = '';
        console.log('🔄 Speech isolation state reset');
    }
}

// Global instance
window.speechIsolationManager = new SpeechIsolationManager();

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    if (window.speechIsolationManager) {
        window.speechIsolationManager.initialize();
    }
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SpeechIsolationManager;
}

console.log('🛡️ Speech Isolation Fix loaded');