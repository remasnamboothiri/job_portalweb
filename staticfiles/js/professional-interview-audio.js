/**
 * Professional AI Interview Audio Management - FIXED ECHO ISSUE
 * Prevents speech recognition from hearing interviewer's voice
 */

class ProfessionalInterviewAudio {
    constructor() {
        this.audioContext = null;
        this.microphoneSource = null;
        this.gainNode = null;
        this.compressor = null;
        this.noiseGate = null;
        this.isAudioIsolationActive = false;
        this.speechRecognitionActive = false;
        this.aiAudioPlaying = false;
        this.userStream = null;
    }

    async initialize(userStream) {
        try {
            console.log('🎙️ Initializing professional interview audio...');
            
            this.userStream = userStream;
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            
            await this.setupAudioProcessing(userStream);
            this.setupAIAudioIsolation();
            
            this.isAudioIsolationActive = true;
            console.log('✅ Professional audio setup complete');
            
        } catch (error) {
            console.error('❌ Professional audio setup failed:', error);
        }
    }

    async setupAudioProcessing(userStream) {
        try {
            this.microphoneSource = this.audioContext.createMediaStreamSource(userStream);
            
            this.gainNode = this.audioContext.createGain();
            this.gainNode.gain.value = 1.2; // Boosted for better pickup
            
            this.compressor = this.audioContext.createDynamicsCompressor();
            this.compressor.threshold.value = -24;
            this.compressor.knee.value = 30;
            this.compressor.ratio.value = 12;
            this.compressor.attack.value = 0.003;
            this.compressor.release.value = 0.25;
            
            this.noiseGate = this.audioContext.createGain();
            this.noiseGate.gain.value = 1.0;
            
            this.microphoneSource
                .connect(this.gainNode)
                .connect(this.compressor)
                .connect(this.noiseGate);
            
            console.log('🔊 Audio processing chain established');
            
        } catch (error) {
            console.error('❌ Audio processing setup failed:', error);
        }
    }

    setupAIAudioIsolation() {
        const aiAudio = document.getElementById('aiAudio');
        if (!aiAudio) {
            console.warn('⚠️ AI audio element not found');
            return;
        }

        // CRITICAL: Pause speech recognition BEFORE audio starts
        aiAudio.addEventListener('loadstart', () => {
            console.log('🔇 AI audio loading - pausing speech recognition immediately');
            this.handleAIAudioStart();
        });

        aiAudio.addEventListener('play', () => {
            console.log('🔊 AI audio playing - ensuring speech recognition is paused');
            this.aiAudioPlaying = true;
            this.handleAIAudioStart(); // Double-ensure it's paused
        });

        aiAudio.addEventListener('ended', () => {
            console.log('🔇 AI audio ended - will resume speech recognition');
            this.aiAudioPlaying = false;
            this.handleAIAudioEnd();
        });

        aiAudio.addEventListener('pause', () => {
            console.log('⏸️ AI audio paused - will resume speech recognition');
            this.aiAudioPlaying = false;
            this.handleAIAudioEnd();
        });

        // Reduce volume to prevent feedback
        aiAudio.volume = 0.4; // Lower volume to reduce echo

        console.log('🔇 AI audio isolation configured with echo prevention');
    }

    handleAIAudioStart() {
        console.log('🚫 BLOCKING speech recognition - AI is about to speak');
        
        // IMMEDIATE blocking - don't wait
        window.speechRecognitionBlocked = true;
        window.isProcessingResponse = true;
        window.isAISpeaking = true;
        
        // Pause the professional speech recognition IMMEDIATELY
        if (window.professionalSpeech && window.professionalSpeech.isActive) {
            window.professionalSpeech.pauseForAI();
        }
        
        // Clear any pending speech timeout
        if (window.speechTimeout) {
            clearTimeout(window.speechTimeout);
            window.speechTimeout = null;
        }
        
        // Clear collected text to prevent contamination
        window.collectedText = '';
        
        console.log('✅ Speech recognition BLOCKED - AI can speak safely');
    }

    handleAIAudioEnd() {
        console.log('⏰ AI audio finished - preparing to resume speech recognition');
        
        // IMPORTANT: Wait longer before resuming to ensure complete silence
        setTimeout(() => {
            console.log('🎙️ Resuming speech recognition after AI silence period');
            
            window.isAISpeaking = false;
            window.speechRecognitionBlocked = false;
            
            // Clear any collected AI echo
            window.collectedText = '';
            
            if (window.professionalSpeech) {
                window.professionalSpeech.resumeFromAI();
            }
            
            // Clear processing flag after additional delay
            setTimeout(() => {
                window.isProcessingResponse = false;
                console.log('✅ Ready for candidate response');
            }, 1000);
            
        }, 2000); // Longer delay to ensure AI audio is completely finished
    }

    cleanup() {
        try {
            if (this.microphoneSource) {
                this.microphoneSource.disconnect();
            }
            if (this.audioContext && this.audioContext.state !== 'closed') {
                this.audioContext.close();
            }
            console.log('🧹 Audio resources cleaned up');
        } catch (error) {
            console.error('❌ Audio cleanup failed:', error);
        }
    }
}

class ProfessionalSpeechRecognition {
    constructor() {
        this.recognition = null;
        this.isActive = false;
        this.autoRestart = true;
        this.restartAttempts = 0;
        this.maxRestartAttempts = 5;
        this.finalTranscript = '';
        this.interimTranscript = '';
        this.isPausedForAI = false;
        this.lastProcessedText = '';
    }

    initialize() {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            console.error('❌ Speech recognition not supported in this browser');
            this.showBrowserCompatibilityWarning();
            return false;
        }

        try {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            this.recognition.continuous = true;
            this.recognition.interimResults = true;
            this.recognition.lang = 'en-US';
            this.recognition.maxAlternatives = 1;

            this.setupEventHandlers();
            
            // Don't start immediately - wait for proper initialization
            setTimeout(() => {
                this.startRecognition();
            }, 1000);
            
            // Make globally available for HTML template compatibility
            window.recognition = this.recognition;
            window.isListening = false;
            
            console.log('✅ Professional speech recognition initialized');
            return true;
        } catch (error) {
            console.error('❌ Failed to initialize speech recognition:', error);
            return false;
        }
    }

    setupEventHandlers() {
        this.recognition.onstart = () => {
            this.isActive = true;
            window.isListening = true;
            this.restartAttempts = 0;
            console.log('🎙️ Speech recognition started and listening');
            this.updateMicrophoneUI(true);
        };

        this.recognition.onend = () => {
            this.isActive = false;
            window.isListening = false;
            console.log('🎙️ Speech recognition ended');
            
            // Only auto-restart if not paused for AI and not manually stopped
            if (this.autoRestart && !this.isPausedForAI && this.restartAttempts < this.maxRestartAttempts) {
                setTimeout(() => {
                    if (this.autoRestart && !this.isPausedForAI && !window.speechRecognitionBlocked && !window.isAISpeaking) {
                        console.log('🔄 Auto-restarting speech recognition');
                        this.startRecognition();
                    }
                }, 500); // Longer delay for stability
            }
        };

        this.recognition.onerror = (event) => {
            console.log('⚠️ Speech recognition error:', event.error);
            
            switch (event.error) {
                case 'no-speech':
                    console.log('📢 No speech detected, continuing to listen...');
                    break;
                case 'audio-capture':
                    console.error('🎤 Audio capture failed - check microphone permissions');
                    this.showMicrophoneError();
                    break;
                case 'network':
                    console.error('🌐 Network error in speech recognition');
                    this.restartAttempts++;
                    if (this.restartAttempts < this.maxRestartAttempts) {
                        setTimeout(() => {
                            if (this.autoRestart && !this.isPausedForAI) {
                                this.startRecognition();
                            }
                        }, 3000);
                    }
                    break;
                case 'not-allowed':
                case 'service-not-allowed':
                    console.error('🚫 Microphone permission denied');
                    this.autoRestart = false;
                    this.showPermissionError();
                    break;
                default:
                    console.error('❌ Speech recognition error:', event.error);
                    break;
            }
        };

        this.recognition.onresult = (event) => {
            this.handleSpeechResult(event);
        };
    }

    handleSpeechResult(event) {
        // CRITICAL: Block ALL speech recognition when AI is speaking
        if (window.isProcessingResponse || window.speechRecognitionBlocked || window.isAISpeaking) {
            console.log('🚫 BLOCKED: AI is speaking - ignoring speech input completely');
            return;
        }

        let interimTranscript = '';
        let finalTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            
            if (event.results[i].isFinal) {
                finalTranscript += transcript + ' ';
                console.log('✅ Candidate final transcript:', transcript);
            } else {
                interimTranscript += transcript;
                console.log('⏳ Candidate interim transcript:', transcript);
            }
        }

        // ENHANCED: Filter out AI voice patterns and common interviewer phrases
        const aiPhrases = [
            'tell me about', 'can you describe', 'what are your', 'how do you', 
            'thank you for', 'that sounds great', 'excellent', 'interesting',
            'hello', 'hi there', 'welcome', 'thanks for joining', 'could you start',
            'wonderful to meet', 'pleasure to meet', 'great to have you',
            'next question', 'moving on', 'let me ask', 'i would like to know',
            'can you walk me through', 'tell us about', 'describe your experience',
            'what interests you about', 'why are you interested', 'what drew you to'
        ];
        
        const fullText = (finalTranscript + interimTranscript).toLowerCase().trim();
        
        // Check if this sounds like AI interviewer speech
        if (aiPhrases.some(phrase => fullText.includes(phrase))) {
            console.log('🚫 FILTERED: AI interviewer speech detected, ignoring:', fullText.substring(0, 50));
            return;
        }

        // Check for duplicate processing
        if (finalTranscript && finalTranscript.trim() === this.lastProcessedText.trim()) {
            console.log('🚫 DUPLICATE: Same text already processed, ignoring');
            return;
        }

        // Update HTML template variables
        if (finalTranscript) {
            this.finalTranscript += finalTranscript;
            this.lastProcessedText = finalTranscript.trim();
            
            // Integration with HTML template's collectedText system
            window.collectedText += finalTranscript;
            window.lastSpeechTime = Date.now();
            
            // Clear existing timeout and set new one
            if (window.speechTimeout) {
                clearTimeout(window.speechTimeout);
            }
            
            window.speechTimeout = setTimeout(() => {
                if (window.collectedText.trim() && !window.isProcessingResponse && !window.isAISpeaking && typeof window.autoSubmitResponse === 'function') {
                    console.log('📤 Auto-submitting candidate response:', window.collectedText.trim());
                    window.autoSubmitResponse();
                }
            }, 1500); // Longer delay for complete sentences
        }
        
        if (interimTranscript) {
            this.interimTranscript = interimTranscript;
            window.lastSpeechTime = Date.now();
        }

        // Display the text in the conversation area (only candidate speech)
        const displayText = window.collectedText + (interimTranscript ? ' ' + interimTranscript : '');
        if (displayText.trim()) {
            this.updateConversationArea(displayText, interimTranscript ? true : false);
        }

        // Update audio level indicator
        if (typeof window.updateAudioLevelIndicator === 'function') {
            window.updateAudioLevelIndicator(interimTranscript ? 70 : 30);
        }
    }

    updateConversationArea(text, isInterim = false) {
        const conversationArea = document.getElementById('conversationArea');
        if (!conversationArea) {
            console.warn('⚠️ Conversation area not found');
            return;
        }

        // Only update with candidate speech - never show AI speech here
        conversationArea.innerHTML = text;
        
        if (isInterim) {
            conversationArea.className = 'conversation-text live-transcription';
        } else {
            conversationArea.className = 'conversation-text candidate-response';
        }
        
        console.log('📝 Candidate speaking - updated conversation area:', text.substring(0, 50) + '...');
    }

    pauseForAI() {
        if (this.isActive) {
            console.log('⏸️ PAUSING speech recognition for AI audio');
            this.isPausedForAI = true;
            try {
                this.recognition.stop();
            } catch (e) {
                console.log('Speech recognition already stopped');
            }
        }
        this.isPausedForAI = true; // Set flag even if not active
    }

    resumeFromAI() {
        console.log('▶️ RESUMING speech recognition after AI audio');
        this.isPausedForAI = false;
        
        // Clear any AI contamination
        window.collectedText = '';
        this.finalTranscript = '';
        this.interimTranscript = '';
        this.lastProcessedText = '';
        
        if (this.autoRestart) {
            setTimeout(() => {
                if (!window.speechRecognitionBlocked && !window.isAISpeaking) {
                    this.startRecognition();
                }
            }, 1000);
        }
    }

    startRecognition() {
        // CRITICAL: Don't start if AI is speaking
        if (!this.recognition || this.isActive || window.speechRecognitionBlocked || window.isAISpeaking) {
            console.log('🚫 Cannot start recognition - AI is speaking or blocked');
            return;
        }

        try {
            console.log('🎯 Starting speech recognition for candidate...');
            this.recognition.start();
        } catch (error) {
            console.error('❌ Failed to start speech recognition:', error);
        }
    }

    stopRecognition() {
        if (this.recognition && this.isActive) {
            console.log('🛑 Stopping speech recognition');
            this.autoRestart = false;
            this.recognition.stop();
            this.updateMicrophoneUI(false);
        }
    }

    restartRecognition() {
        console.log('🔄 Manually restarting speech recognition');
        this.autoRestart = true;
        this.restartAttempts = 0;
        this.clearTranscripts();
        
        if (this.isActive) {
            this.recognition.stop();
        } else {
            this.startRecognition();
        }
    }

    clearTranscripts() {
        this.finalTranscript = '';
        this.interimTranscript = '';
        this.lastProcessedText = '';
        
        // Also clear HTML template variables
        window.collectedText = '';
        
        // Clear conversation area
        const conversationArea = document.getElementById('conversationArea');
        if (conversationArea) {
            conversationArea.innerHTML = '';
            conversationArea.className = 'conversation-text';
        }
    }

    updateMicrophoneUI(active) {
        const micBtn = document.getElementById('micBtn');
        if (!micBtn) {
            console.warn('⚠️ Microphone button not found');
            return;
        }

        if (active) {
            micBtn.classList.add('recording');
            micBtn.innerHTML = '🔴';
            micBtn.title = 'Microphone ON - Listening for your response';
        } else {
            micBtn.classList.remove('recording');
            micBtn.innerHTML = '🎤';
            micBtn.title = 'Microphone ON - Speech recognition paused';
        }
    }

    showPermissionError() {
        this.showError(
            'Microphone permission required for interview',
            'Please allow microphone access and refresh the page'
        );
    }

    showMicrophoneError() {
        this.showError(
            'Microphone access failed',
            'Please check your microphone connection and try again'
        );
    }

    showBrowserCompatibilityWarning() {
        this.showError(
            'Browser not supported',
            'Please use Chrome, Edge, or Safari for speech recognition'
        );
    }

    showError(title, message) {
        let errorDiv = document.getElementById('speechRecognitionError');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.id = 'speechRecognitionError';
            errorDiv.style.cssText = `
                position: fixed;
                top: 20px;
                left: 50%;
                transform: translateX(-50%);
                background: #f44336;
                color: white;
                padding: 15px 25px;
                border-radius: 8px;
                z-index: 10000;
                font-weight: bold;
                text-align: center;
                max-width: 400px;
            `;
            document.body.appendChild(errorDiv);
        }
        
        errorDiv.innerHTML = `${title}<br><small>${message}</small>`;

        setTimeout(() => {
            if (errorDiv && errorDiv.parentNode) {
                errorDiv.parentNode.removeChild(errorDiv);
            }
        }, 10000);
    }
}

// Global instances
window.professionalAudio = new ProfessionalInterviewAudio();
window.professionalSpeech = new ProfessionalSpeechRecognition();

// Global variables for HTML template compatibility
window.speechRecognitionBlocked = false;
window.isAISpeaking = false;
window.isListening = false;

// Override HTML template functions to use professional system
window.startMicrophone = function() {
    if (window.professionalSpeech && !window.isAISpeaking) {
        window.professionalSpeech.startRecognition();
    }
};

// Enhanced DOM ready handler
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Professional interview audio system loading - ECHO FIXED VERSION...');
    
    // Wait for HTML template to initialize its variables
    setTimeout(() => {
        initializeProfessionalSystem();
    }, 1000);
    
    function initializeProfessionalSystem() {
        // Initialize professional audio if stream is available
        if (window.userStream) {
            window.professionalAudio.initialize(window.userStream);
        } else {
            // Check periodically for user stream
            const checkUserMedia = setInterval(() => {
                if (window.userStream) {
                    clearInterval(checkUserMedia);
                    window.professionalAudio.initialize(window.userStream);
                }
            }, 200);
            
            // Stop checking after 10 seconds
            setTimeout(() => clearInterval(checkUserMedia), 10000);
        }
        
        // Initialize professional speech recognition with delay
        setTimeout(() => {
            window.professionalSpeech.initialize();
        }, 2000); // Longer delay to ensure everything is ready
        
        console.log('✅ Professional interview audio system - ECHO PROTECTION ACTIVE');
    }
    
    // Cleanup on page unload
    window.addEventListener('beforeunload', () => {
        if (window.professionalAudio) {
            window.professionalAudio.cleanup();
        }
        if (window.professionalSpeech) {
            window.professionalSpeech.stopRecognition();
        }
    });
});

console.log('📁 Professional interview audio module loaded - ECHO FIXED VERSION');
console.log('🎙️ Interview mode: Microphone stays ON, but speech recognition pauses during AI speech');
console.log('🔇 Enhanced echo prevention - AI voice will NOT be transcribed as candidate response');
console.log('🛡️ AI phrase filtering active to prevent interviewer speech contamination');