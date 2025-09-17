/**
 * Professional AI Interview Audio Management - INTEGRATED VERSION
 * Works seamlessly with existing HTML template
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

        aiAudio.addEventListener('play', () => {
            this.aiAudioPlaying = true;
            this.handleAIAudioStart();
        });

        aiAudio.addEventListener('ended', () => {
            this.aiAudioPlaying = false;
            this.handleAIAudioEnd();
        });

        aiAudio.addEventListener('pause', () => {
            this.aiAudioPlaying = false;
            this.handleAIAudioEnd();
        });

        aiAudio.volume = 0.6;
        console.log('🔇 AI audio isolation configured');
    }

    handleAIAudioStart() {
        console.log('🔇 AI audio starting - pausing speech recognition');
        
        // Pause the professional speech recognition
        if (window.professionalSpeech && window.professionalSpeech.isActive) {
            window.professionalSpeech.pauseForAI();
        }
        
        // Set global blocking flags for HTML template compatibility
        window.isProcessingResponse = true;
        window.speechRecognitionBlocked = true;
        window.isAISpeaking = true;
    }

    handleAIAudioEnd() {
        console.log('🎙️ AI audio ending - restoring speech recognition');
        
        setTimeout(() => {
            window.isAISpeaking = false;
            window.speechRecognitionBlocked = false;
            
            if (window.professionalSpeech) {
                window.professionalSpeech.resumeFromAI();
            }
            
            // Clear processing flag after delay
            setTimeout(() => {
                window.isProcessingResponse = false;
            }, 500);
        }, 1000);
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
            this.startRecognition();
            
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
            console.log('🎙️ Speech recognition started');
            this.updateMicrophoneUI(true);
        };

        this.recognition.onend = () => {
            this.isActive = false;
            window.isListening = false;
            console.log('🎙️ Speech recognition ended');
            
            if (this.autoRestart && !this.isPausedForAI && this.restartAttempts < this.maxRestartAttempts) {
                setTimeout(() => {
                    if (this.autoRestart && !this.isPausedForAI && !window.speechRecognitionBlocked) {
                        console.log('🔄 Auto-restarting speech recognition');
                        this.startRecognition();
                    }
                }, 100);
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
                        }, 2000);
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
        // Block speech recognition while AI is speaking
        if (window.isProcessingResponse) {
            console.log('🚫 AI is speaking - ignoring speech input');
            return;
        }

        let interimTranscript = '';
        let finalTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            
            if (event.results[i].isFinal) {
                finalTranscript += transcript + ' ';
                console.log('✅ Final transcript:', transcript);
            } else {
                interimTranscript += transcript;
                console.log('⏳ Interim transcript:', transcript);
            }
        }

        // Filter out AI voice patterns (from HTML template)
        const aiPhrases = ['tell me about', 'can you describe', 'what are your', 'how do you', 'thank you for', 'that sounds great', 'excellent', 'interesting'];
        const textLower = (finalTranscript + interimTranscript).toLowerCase();
        
        if (aiPhrases.some(phrase => textLower.includes(phrase))) {
            console.log('🚫 AI echo detected, ignoring');
            return;
        }

        // Update HTML template variables
        if (finalTranscript) {
            this.finalTranscript += finalTranscript;
            
            // Integration with HTML template's collectedText system
            window.collectedText += finalTranscript;
            window.lastSpeechTime = Date.now();
            
            // Clear existing timeout and set new one
            if (window.speechTimeout) {
                clearTimeout(window.speechTimeout);
            }
            
            window.speechTimeout = setTimeout(() => {
                if (window.collectedText.trim() && !window.isProcessingResponse && typeof window.autoSubmitResponse === 'function') {
                    window.autoSubmitResponse();
                }
            }, 1000);
        }
        
        if (interimTranscript) {
            this.interimTranscript = interimTranscript;
            window.lastSpeechTime = Date.now();
        }

        // Display the text in the conversation area
        const displayText = window.collectedText + (interimTranscript ? ' ' + interimTranscript : '');
        this.updateConversationArea(displayText, interimTranscript ? true : false);

        // Update audio level indicator
        if (typeof window.updateAudioLevelIndicator === 'function') {
            window.updateAudioLevelIndicator(interimTranscript ? 60 : 20);
        }
    }

    updateConversationArea(text, isInterim = false) {
        const conversationArea = document.getElementById('conversationArea');
        if (!conversationArea) {
            console.warn('⚠️ Conversation area not found');
            return;
        }

        conversationArea.innerHTML = text;
        
        if (isInterim) {
            conversationArea.className = 'conversation-text live-transcription';
        } else {
            conversationArea.className = 'conversation-text candidate-response';
        }
        
        console.log('📝 Updated conversation area:', text.substring(0, 50) + '...');
    }

    pauseForAI() {
        if (this.isActive) {
            console.log('⏸️ Pausing speech recognition for AI audio');
            this.isPausedForAI = true;
            this.recognition.stop();
        }
    }

    resumeFromAI() {
        console.log('▶️ Resuming speech recognition after AI audio');
        this.isPausedForAI = false;
        if (this.autoRestart) {
            setTimeout(() => {
                this.startRecognition();
            }, 500);
        }
    }

    startRecognition() {
        if (!this.recognition || this.isActive || window.speechRecognitionBlocked) {
            console.log('🚫 Cannot start recognition - blocked or already active');
            return;
        }

        try {
            console.log('🎯 Starting speech recognition...');
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
            micBtn.innerHTML = '🔴 ';
            micBtn.title = 'Microphone is ON - Speech recognition active';
        } else {
            micBtn.classList.remove('recording');
            micBtn.innerHTML = '🎤';
            micBtn.title = 'Microphone is ON - Speech recognition paused';
        }
    }

    showPermissionError() {
        this.showError(
            '🎙️ Microphone permission required for interview',
            'Please allow microphone access and refresh the page'
        );
    }

    showMicrophoneError() {
        this.showError(
            '🎤 Microphone access failed',
            'Please check your microphone connection and try again'
        );
    }

    showBrowserCompatibilityWarning() {
        this.showError(
            '🌐 Browser not supported',
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
        
        errorDiv.innerHTML = `
            ${title}<br>
            <small>${message}</small>
        `;

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
    if (window.professionalSpeech) {
        window.professionalSpeech.startRecognition();
    }
};

// Enhanced DOM ready handler
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Professional interview audio system loading...');
    
    // Wait a bit for HTML template to initialize its variables
    setTimeout(() => {
        initializeProfessionalSystem();
    }, 500);
    
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
        
        // Initialize professional speech recognition
        setTimeout(() => {
            window.professionalSpeech.initialize();
        }, 1000); // Delay to ensure HTML template is ready
        
        console.log('✅ Professional interview audio system integration complete');
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

console.log('📁 Professional interview audio module loaded - INTEGRATED VERSION');
console.log('🎙️ Interview mode: Microphone will stay ON throughout the interview');
console.log('🔇 Speech recognition will be temporarily blocked when AI is speaking');
console.log('🔗 Integrated with HTML template speech recognition system');