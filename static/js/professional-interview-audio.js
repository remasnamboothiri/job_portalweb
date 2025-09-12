/**
 * Professional AI Interview Audio Management
 * Ensures microphone is always on with proper audio isolation
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
    }

    // Initialize professional audio setup
    async initialize(userStream) {
        try {
            console.log('🎙️ Initializing professional interview audio...');
            
            // Create audio context
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            
            // Setup audio processing chain
            await this.setupAudioProcessing(userStream);
            
            // Setup AI audio isolation
            this.setupAIAudioIsolation();
            
            this.isAudioIsolationActive = true;
            console.log('✅ Professional audio setup complete');
            
        } catch (error) {
            console.error('❌ Professional audio setup failed:', error);
        }
    }

    // Setup audio processing chain for better quality
    async setupAudioProcessing(userStream) {
        try {
            // Create microphone source
            this.microphoneSource = this.audioContext.createMediaStreamSource(userStream);
            
            // Create gain node for volume control
            this.gainNode = this.audioContext.createGain();
            this.gainNode.gain.value = 1.0;
            
            // Create compressor for consistent audio levels
            this.compressor = this.audioContext.createDynamicsCompressor();
            this.compressor.threshold.value = -24;
            this.compressor.knee.value = 30;
            this.compressor.ratio.value = 12;
            this.compressor.attack.value = 0.003;
            this.compressor.release.value = 0.25;
            
            // Create noise gate (simple implementation)
            this.noiseGate = this.audioContext.createGain();
            this.noiseGate.gain.value = 1.0;
            
            // Connect audio processing chain
            this.microphoneSource
                .connect(this.gainNode)
                .connect(this.compressor)
                .connect(this.noiseGate);
            
            console.log('🔊 Audio processing chain established');
            
        } catch (error) {
            console.error('❌ Audio processing setup failed:', error);
        }
    }

    // Setup AI audio isolation to prevent feedback
    setupAIAudioIsolation() {
        const aiAudio = document.getElementById('aiAudio');
        if (!aiAudio) return;

        // Monitor AI audio playback
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

        // Set optimal volume to prevent feedback
        aiAudio.volume = 0.6;
        
        console.log('🔇 AI audio isolation configured');
    }

    // Handle AI audio start - completely disable speech recognition during AI speech
    handleAIAudioStart() {
        console.log('🔇 AI audio started - disabling speech recognition to prevent feedback');
        
        // Completely disable speech recognition during AI speech
        if (window.recognition && window.isListening) {
            try {
                window.recognition.stop();
                this.speechRecognitionActive = true;
                console.log('✅ Speech recognition stopped during AI speech');
            } catch (e) {
                console.log('Could not pause speech recognition:', e);
            }
        }
        
        // Also disable microphone processing to prevent any audio feedback
        if (this.gainNode) {
            this.gainNode.gain.setValueAtTime(0.0, this.audioContext.currentTime);
        }
        
        // Set global flag to ignore any speech input
        window.isProcessingResponse = true;
    }

    // Handle AI audio end - restore speech recognition after delay
    handleAIAudioEnd() {
        console.log('🎙️ AI audio ended - preparing to restore speech recognition');
        
        // Wait longer to ensure AI audio is completely finished
        setTimeout(() => {
            // Restore microphone gain
            if (this.gainNode) {
                this.gainNode.gain.setValueAtTime(1.0, this.audioContext.currentTime);
            }
            
            // Clear processing flag
            window.isProcessingResponse = false;
            
            // Restart speech recognition
            if (this.speechRecognitionActive && window.recognition && window.isListening) {
                try {
                    window.recognition.start();
                    this.speechRecognitionActive = false;
                    console.log('✅ Speech recognition restarted after AI speech');
                } catch (e) {
                    console.log('Could not resume speech recognition:', e);
                }
            }
        }, 1000); // Increased delay to 1 second to ensure clean separation
    }

    // Apply noise suppression
    applyNoiseSuppression(level = 0.5) {
        if (this.noiseGate) {
            this.noiseGate.gain.value = Math.max(0.1, 1.0 - level);
        }
    }

    // Adjust microphone sensitivity
    adjustMicrophoneSensitivity(level = 1.0) {
        if (this.gainNode) {
            this.gainNode.gain.setValueAtTime(level, this.audioContext.currentTime);
        }
    }

    // Get audio levels for monitoring
    getAudioLevel() {
        // This would require an analyser node for real-time monitoring
        // Implementation depends on specific requirements
        return 0;
    }

    // Cleanup audio resources
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

// Enhanced Speech Recognition Manager
class ProfessionalSpeechRecognition {
    constructor() {
        this.recognition = null;
        this.isActive = false;
        this.autoRestart = true;
        this.restartAttempts = 0;
        this.maxRestartAttempts = 5;
    }

    // Initialize speech recognition with professional settings
    initialize() {
        if (!('webkitSpeechRecognition' in window)) {
            console.error('Speech recognition not supported');
            return false;
        }

        this.recognition = new webkitSpeechRecognition();
        this.recognition.continuous = true;
        this.recognition.interimResults = true;
        this.recognition.lang = 'en-US';
        this.recognition.maxAlternatives = 1;

        this.setupEventHandlers();
        this.startRecognition();
        
        return true;
    }

    // Setup event handlers for robust operation
    setupEventHandlers() {
        this.recognition.onstart = () => {
            this.isActive = true;
            this.restartAttempts = 0;
            console.log('🎙️ Speech recognition started');
            this.updateMicrophoneUI(true);
        };

        this.recognition.onend = () => {
            this.isActive = false;
            console.log('🎙️ Speech recognition ended');
            
            // Auto-restart if enabled and not manually stopped
            if (this.autoRestart && this.restartAttempts < this.maxRestartAttempts) {
                setTimeout(() => {
                    if (this.autoRestart) {
                        this.startRecognition();
                    }
                }, 100);
            }
        };

        this.recognition.onerror = (event) => {
            console.log('🎙️ Speech recognition error:', event.error);
            
            // Handle specific errors
            switch (event.error) {
                case 'no-speech':
                case 'audio-capture':
                case 'network':
                    // Restart on recoverable errors
                    this.restartAttempts++;
                    if (this.restartAttempts < this.maxRestartAttempts) {
                        setTimeout(() => {
                            if (this.autoRestart) {
                                this.startRecognition();
                            }
                        }, 1000);
                    }
                    break;
                case 'not-allowed':
                case 'service-not-allowed':
                    // Don't restart on permission errors
                    this.autoRestart = false;
                    this.showPermissionError();
                    break;
            }
        };

        this.recognition.onresult = (event) => {
            // Ignore speech recognition results during AI speech
            if (window.isProcessingResponse || window.professionalAudio?.aiAudioPlaying) {
                console.log('🚫 Ignoring speech input - AI is currently speaking');
                return;
            }
            
            // Handle speech recognition results only when AI is not speaking
            if (window.handleSpeechResult) {
                window.handleSpeechResult(event);
            }
        };
    }

    // Start speech recognition
    startRecognition() {
        if (!this.recognition || this.isActive) return;

        try {
            this.recognition.start();
        } catch (error) {
            console.error('Failed to start speech recognition:', error);
        }
    }

    // Stop speech recognition
    stopRecognition() {
        if (this.recognition && this.isActive) {
            this.autoRestart = false;
            this.recognition.stop();
            this.updateMicrophoneUI(false);
        }
    }

    // Manually restart recognition
    restartRecognition() {
        this.autoRestart = true;
        this.restartAttempts = 0;
        if (this.isActive) {
            this.recognition.stop();
        } else {
            this.startRecognition();
        }
    }

    // Update microphone UI
    updateMicrophoneUI(active) {
        const micBtn = document.getElementById('micBtn');
        if (!micBtn) return;

        if (active) {
            micBtn.classList.add('recording');
            micBtn.innerHTML = '🔴';
            micBtn.title = 'Microphone is ON (Professional Interview Mode)';
        } else {
            micBtn.classList.remove('recording');
            micBtn.innerHTML = '🎤';
            micBtn.title = 'Click to turn microphone ON';
        }
    }

    // Show permission error
    showPermissionError() {
        const errorDiv = document.createElement('div');
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
        `;
        errorDiv.innerHTML = `
            🎙️ Microphone permission required for interview<br>
            <small>Please allow microphone access and refresh the page</small>
        `;
        document.body.appendChild(errorDiv);
    }
}

// Global instances
window.professionalAudio = new ProfessionalInterviewAudio();
window.professionalSpeech = new ProfessionalSpeechRecognition();

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Professional interview audio system loading...');
    
    // Wait for user media to be available
    const checkUserMedia = setInterval(() => {
        if (window.userStream) {
            clearInterval(checkUserMedia);
            
            // Initialize professional audio
            window.professionalAudio.initialize(window.userStream);
            
            // Initialize professional speech recognition
            window.professionalSpeech.initialize();
            
            console.log('✅ Professional interview audio system ready');
        }
    }, 100);
    
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

console.log('📁 Professional interview audio module loaded');