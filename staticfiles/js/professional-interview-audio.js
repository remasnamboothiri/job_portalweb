


/**
 * Professional AI Interview Audio Management - FIXED VERSION
 * Properly requests microphone access and ensures recording works
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
        this.userStream = null; // Add this property
    }

    // NEW: Request microphone access first
    async requestMicrophoneAccess() {
        try {
            console.log('🎙️ Requesting microphone access...');
            
            const constraints = {
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true,
                    sampleRate: 44100
                }
            };
            
            this.userStream = await navigator.mediaDevices.getUserMedia(constraints);
            window.userStream = this.userStream; // Set global reference
            
            console.log('✅ Microphone access granted');
            return true;
            
        } catch (error) {
            console.error('❌ Microphone access denied:', error);
            this.showMicrophoneError(error);
            return false;
        }
    }

    // Show microphone error
    showMicrophoneError(error) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'mic-error-notification';
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
            max-width: 90%;
        `;
        
        let message = '🎙️ Microphone access required for interview<br>';
        
        switch (error.name) {
            case 'NotAllowedError':
                message += '<small>Please allow microphone access and refresh the page</small>';
                break;
            case 'NotFoundError':
                message += '<small>No microphone found. Please connect a microphone</small>';
                break;
            case 'NotReadableError':
                message += '<small>Microphone is being used by another application</small>';
                break;
            default:
                message += '<small>Please check your microphone settings and refresh</small>';
        }
        
        errorDiv.innerHTML = message;
        document.body.appendChild(errorDiv);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.parentNode.removeChild(errorDiv);
            }
        }, 5000);
    }

    // Initialize professional audio setup
    async initialize(userStream = null) {
        try {
            console.log('🎙️ Initializing professional interview audio...');
            
            // Use provided stream or request new one
            const stream = userStream || this.userStream;
            if (!stream) {
                console.log('No audio stream available, requesting access...');
                const accessGranted = await this.requestMicrophoneAccess();
                if (!accessGranted) return false;
            }
            
            // Create audio context
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            
            // Setup audio processing chain
            await this.setupAudioProcessing(this.userStream);
            
            // Setup AI audio isolation
            this.setupAIAudioIsolation();
            
            this.isAudioIsolationActive = true;
            console.log('✅ Professional audio setup complete');
            
            return true;
            
        } catch (error) {
            console.error('❌ Professional audio setup failed:', error);
            return false;
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
        if (!aiAudio) {
            console.warn('⚠️ AI audio element not found');
            return;
        }

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

    // Handle AI audio start - block speech recognition but keep mic on
    handleAIAudioStart() {
        // Block speech recognition temporarily
        if (window.recognition && window.recognition.abort) {
            try {
                window.recognition.abort();
                this.speechRecognitionActive = true;
            } catch (e) {
                console.log('Could not pause speech recognition:', e);
            }
        }
        
        // Set global flags to block speech recognition
        window.speechRecognitionBlocked = true;
        window.isAISpeaking = true;
        
        console.log('🔇 AI audio started - speech recognition blocked (microphone stays on)');
    }

    // Handle AI audio end - restore speech recognition
    handleAIAudioEnd() {
        // Clear global blocking flags
        window.isAISpeaking = false;
        
        // Resume speech recognition after delay
        setTimeout(() => {
            window.speechRecognitionBlocked = false;
            
            if (this.speechRecognitionActive && window.professionalSpeech) {
                try {
                    window.professionalSpeech.restartRecognition();
                    this.speechRecognitionActive = false;
                } catch (e) {
                    console.log('Could not resume speech recognition:', e);
                }
            }
        }, 1000);
        
        console.log('🎙️ AI audio ended - speech recognition restored');
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

    // NEW: Test microphone function
    testMicrophone() {
        if (!this.userStream) {
            console.error('No microphone stream available');
            return false;
        }
        
        const tracks = this.userStream.getAudioTracks();
        if (tracks.length === 0) {
            console.error('No audio tracks in stream');
            return false;
        }
        
        console.log('🎙️ Microphone test:', tracks[0].label, 'enabled:', tracks[0].enabled);
        return tracks[0].enabled;
    }

    // Cleanup audio resources
    cleanup() {
        try {
            if (this.userStream) {
                this.userStream.getTracks().forEach(track => track.stop());
            }
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
        this.finalTranscript = '';
        this.interimTranscript = '';
    }

    // Initialize speech recognition with professional settings
    initialize() {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            console.error('❌ Speech recognition not supported in this browser');
            this.showBrowserError();
            return false;
        }

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();
        
        this.recognition.continuous = true;
        this.recognition.interimResults = true;
        this.recognition.lang = 'en-US';
        this.recognition.maxAlternatives = 1;

        this.setupEventHandlers();
        this.startRecognition();
        
        return true;
    }

    // Show browser compatibility error
    showBrowserError() {
        const errorDiv = document.createElement('div');
        errorDiv.style.cssText = `
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: #ff9800;
            color: white;
            padding: 15px 25px;
            border-radius: 8px;
            z-index: 10000;
            font-weight: bold;
            text-align: center;
        `;
        errorDiv.innerHTML = `
            🎙️ Speech recognition not supported<br>
            <small>Please use Chrome or Edge browser for voice interviews</small>
        `;
        document.body.appendChild(errorDiv);
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
            this.updateMicrophoneUI(false);
            
            // Auto-restart if enabled and not manually stopped
            if (this.autoRestart && this.restartAttempts < this.maxRestartAttempts && !window.speechRecognitionBlocked) {
                setTimeout(() => {
                    if (this.autoRestart && !window.speechRecognitionBlocked) {
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
                    // Just restart, this is normal
                    break;
                case 'audio-capture':
                    console.error('❌ No microphone access for speech recognition');
                    this.showMicrophoneError();
                    break;
                case 'network':
                    // Restart on network errors
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
            this.handleSpeechResult(event);
        };
    }

    // NEW: Handle speech recognition results
    handleSpeechResult(event) {
        let interimTranscript = '';
        let finalTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalTranscript += transcript;
            } else {
                interimTranscript += transcript;
            }
        }

        this.finalTranscript += finalTranscript;
        this.interimTranscript = interimTranscript;

        // Update UI with transcription
        this.updateTranscriptionUI(this.finalTranscript, this.interimTranscript);

        // Call external handler if it exists
        if (window.handleSpeechResult && typeof window.handleSpeechResult === 'function') {
            window.handleSpeechResult(event);
        }

        // If we have final results, send to server
        if (finalTranscript.trim()) {
            this.sendTranscriptionToServer(finalTranscript);
        }
    }

    // NEW: Update transcription UI
    updateTranscriptionUI(finalText, interimText) {
        const transcriptionDiv = document.getElementById('live-transcription') || this.createTranscriptionDiv();
        
        if (transcriptionDiv) {
            transcriptionDiv.innerHTML = `
                <div class="final-transcript">${finalText}</div>
                <div class="interim-transcript">${interimText}</div>
            `;
        }
    }

    // NEW: Create transcription display div
    createTranscriptionDiv() {
        const div = document.createElement('div');
        div.id = 'live-transcription';
        div.style.cssText = `
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 10px 20px;
            border-radius: 20px;
            max-width: 80%;
            font-size: 14px;
            z-index: 1000;
        `;
        document.body.appendChild(div);
        return div;
    }

    // NEW: Send transcription to server
    sendTranscriptionToServer(text) {
        // This should integrate with your Django backend
        // You'll need to implement the server endpoint
        console.log('📤 Sending transcription to server:', text);
        
        // Example implementation - adjust URL and payload as needed
        fetch('/interview/speech/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            },
            body: JSON.stringify({
                interview_id: this.getInterviewId(),
                transcript: text
            })
        }).catch(error => {
            console.error('Failed to send transcription:', error);
        });
    }

    // Helper to get CSRF token
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }

    // Helper to get interview ID from URL
    getInterviewId() {
        const matches = window.location.pathname.match(/interview\/start\/([^\/]+)/);
        return matches ? matches[1] : null;
    }

    // Start speech recognition
    startRecognition() {
        if (!this.recognition || this.isActive || window.speechRecognitionBlocked) return;

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
        const micBtn = document.getElementById('micBtn') || document.getElementById('muteBtn');
        if (!micBtn) return;

        if (active) {
            micBtn.classList.add('recording', 'mic-active');
            micBtn.classList.remove('mic-muted');
            micBtn.innerHTML = '🎤';
            micBtn.title = 'Microphone is ON - Speech recognition active';
        } else {
            micBtn.classList.remove('recording');
            micBtn.classList.add('mic-active');
            micBtn.classList.remove('mic-muted');
            micBtn.innerHTML = '🎤';
            micBtn.title = 'Microphone is ON - Speech recognition paused';
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
            🎙️ Speech recognition permission required<br>
            <small>Please allow microphone access and refresh the page</small>
        `;
        document.body.appendChild(errorDiv);
    }

    showMicrophoneError() {
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
            🎙️ Microphone access required for speech recognition<br>
            <small>Please check microphone permissions</small>
        `;
        document.body.appendChild(errorDiv);
    }
}

// Global instances
window.professionalAudio = new ProfessionalInterviewAudio();
window.professionalSpeech = new ProfessionalSpeechRecognition();

// NEW: Initialize immediately on load
async function initializeProfessionalInterview() {
    console.log('🚀 Professional interview audio system initializing...');
    
    // Request microphone access first
    const audioInitialized = await window.professionalAudio.initialize();
    
    if (audioInitialized) {
        // Initialize speech recognition
        const speechInitialized = window.professionalSpeech.initialize();
        
        if (speechInitialized) {
            console.log('✅ Professional interview system fully initialized');
            
            // Test microphone
            const micTest = window.professionalAudio.testMicrophone();
            console.log('🎙️ Microphone test result:', micTest);
            
        } else {
            console.warn('⚠️ Speech recognition initialization failed');
        }
    } else {
        console.error('❌ Audio system initialization failed');
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initializeProfessionalInterview();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.professionalAudio) {
        window.professionalAudio.cleanup();
    }
    if (window.professionalSpeech) {
        window.professionalSpeech.stopRecognition();
    }
});

// Export global functions for external use
window.startSpeechRecognition = () => {
    if (window.professionalSpeech) {
        window.professionalSpeech.startRecognition();
    }
};

window.stopSpeechRecognition = () => {
    if (window.professionalSpeech) {
        window.professionalSpeech.stopRecognition();
    }
};

window.handleSpeechResult = (event) => {
    // This function is called by the speech recognition system
    // You can override this in your main interview script
    if (window.professionalSpeech) {
        window.professionalSpeech.handleSpeechResult(event);
    }
};

console.log('📁 Professional interview audio module loaded - FIXED VERSION');
console.log('🎙️ Microphone access will be requested automatically');
console.log('🔇 Speech recognition will be blocked when AI is speaking');
console.log('📤 Transcriptions will be sent to server automatically');

/**
 * Professional AI Interview Audio Management
 * Ensures microphone is always on with proper audio isolation
 */

// class ProfessionalInterviewAudio {
//     constructor() {
//         this.audioContext = null;
//         this.microphoneSource = null;
//         this.gainNode = null;
//         this.compressor = null;
//         this.noiseGate = null;
//         this.isAudioIsolationActive = false;
//         this.speechRecognitionActive = false;
//         this.aiAudioPlaying = false;
//         this.userStream = null; // Add this property
//     }

    

    // Initialize professional audio setup
    // async initialize(userStream) {
    //     try {
    //         console.log('🎙️ Initializing professional interview audio...');
            
    //         // Create audio context
    //         this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            
    //         // Setup audio processing chain
    //         await this.setupAudioProcessing(userStream);
            
    //         // Setup AI audio isolation
    //         this.setupAIAudioIsolation();
            
    //         this.isAudioIsolationActive = true;
    //         console.log('✅ Professional audio setup complete');
            
    //     } catch (error) {
    //         console.error('❌ Professional audio setup failed:', error);
    //     }
    // }

    // // Setup audio processing chain for better quality
    // async setupAudioProcessing(userStream) {
    //     try {
    //         // Create microphone source
    //         this.microphoneSource = this.audioContext.createMediaStreamSource(userStream);
            
    //         // Create gain node for volume control
    //         this.gainNode = this.audioContext.createGain();
    //         this.gainNode.gain.value = 1.0;
            
    //         // Create compressor for consistent audio levels
    //         this.compressor = this.audioContext.createDynamicsCompressor();
    //         this.compressor.threshold.value = -24;
    //         this.compressor.knee.value = 30;
    //         this.compressor.ratio.value = 12;
    //         this.compressor.attack.value = 0.003;
    //         this.compressor.release.value = 0.25;
            
    //         // Create noise gate (simple implementation)
    //         this.noiseGate = this.audioContext.createGain();
    //         this.noiseGate.gain.value = 1.0;
            
    //         // Connect audio processing chain
    //         this.microphoneSource
    //             .connect(this.gainNode)
    //             .connect(this.compressor)
    //             .connect(this.noiseGate);
            
    //         console.log('🔊 Audio processing chain established');
            
    //     } catch (error) {
    //         console.error('❌ Audio processing setup failed:', error);
    //     }
    // }

    // Setup AI audio isolation to prevent feedback
//     setupAIAudioIsolation() {
//         const aiAudio = document.getElementById('aiAudio');
//         if (!aiAudio) return;

//         // Monitor AI audio playback
//         aiAudio.addEventListener('play', () => {
//             this.aiAudioPlaying = true;
//             this.handleAIAudioStart();
//         });

//         aiAudio.addEventListener('ended', () => {
//             this.aiAudioPlaying = false;
//             this.handleAIAudioEnd();
//         });

//         aiAudio.addEventListener('pause', () => {
//             this.aiAudioPlaying = false;
//             this.handleAIAudioEnd();
//         });

//         // Set optimal volume to prevent feedback
//         aiAudio.volume = 0.6;
        
//         console.log('🔇 AI audio isolation configured');
//     }

//     // Handle AI audio start - block speech recognition but keep mic on
//     handleAIAudioStart() {
//         // Keep microphone at full sensitivity - don't reduce gain
//         // The microphone should always be on during interview
        
//         // Block speech recognition temporarily
//         if (window.recognition && window.isListening) {
//             try {
//                 window.recognition.stop();
//                 this.speechRecognitionActive = true;
//             } catch (e) {
//                 console.log('Could not pause speech recognition:', e);
//             }
//         }
        
//         // Set global flags to block speech recognition
//         if (typeof window.speechRecognitionBlocked !== 'undefined') {
//             window.speechRecognitionBlocked = true;
//         }
//         if (typeof window.isAISpeaking !== 'undefined') {
//             window.isAISpeaking = true;
//         }
        
//         console.log('🔇 AI audio started - speech recognition blocked (microphone stays on)');
//     }

//     // Handle AI audio end - restore speech recognition
//     handleAIAudioEnd() {
//         // Microphone gain stays at full level - no need to restore
        
//         // Clear global blocking flags
//         if (typeof window.isAISpeaking !== 'undefined') {
//             window.isAISpeaking = false;
//         }
        
//         // Resume speech recognition after delay
//         setTimeout(() => {
//             if (typeof window.speechRecognitionBlocked !== 'undefined') {
//                 window.speechRecognitionBlocked = false;
//             }
            
//             if (this.speechRecognitionActive && window.recognition) {
//                 try {
//                     // Use the global start function if available
//                     if (typeof window.startSpeechRecognition === 'function') {
//                         window.startSpeechRecognition();
//                     } else {
//                         window.recognition.start();
//                     }
//                     this.speechRecognitionActive = false;
//                 } catch (e) {
//                     console.log('Could not resume speech recognition:', e);
//                 }
//             }
//         }, 1000); // Increased delay to ensure AI audio has fully stopped
        
//         console.log('🎙️ AI audio ended - speech recognition restored (microphone was always on)');
//     }

//     // Apply noise suppression
//     applyNoiseSuppression(level = 0.5) {
//         if (this.noiseGate) {
//             this.noiseGate.gain.value = Math.max(0.1, 1.0 - level);
//         }
//     }

//     // Adjust microphone sensitivity
//     adjustMicrophoneSensitivity(level = 1.0) {
//         if (this.gainNode) {
//             this.gainNode.gain.setValueAtTime(level, this.audioContext.currentTime);
//         }
//     }

//     // Get audio levels for monitoring
//     getAudioLevel() {
//         // This would require an analyser node for real-time monitoring
//         // Implementation depends on specific requirements
//         return 0;
//     }

//     // Cleanup audio resources
//     cleanup() {
//         try {
//             if (this.microphoneSource) {
//                 this.microphoneSource.disconnect();
//             }
//             if (this.audioContext && this.audioContext.state !== 'closed') {
//                 this.audioContext.close();
//             }
//             console.log('🧹 Audio resources cleaned up');
//         } catch (error) {
//             console.error('❌ Audio cleanup failed:', error);
//         }
//     }
// }

// // Enhanced Speech Recognition Manager
// class ProfessionalSpeechRecognition {
//     constructor() {
//         this.recognition = null;
//         this.isActive = false;
//         this.autoRestart = true;
//         this.restartAttempts = 0;
//         this.maxRestartAttempts = 5;
//     }

//     // Initialize speech recognition with professional settings
//     initialize() {
//         if (!('webkitSpeechRecognition' in window)) {
//             console.error('Speech recognition not supported');
//             return false;
//         }

//         this.recognition = new webkitSpeechRecognition();
//         this.recognition.continuous = true;
//         this.recognition.interimResults = true;
//         this.recognition.lang = 'en-US';
//         this.recognition.maxAlternatives = 1;

//         this.setupEventHandlers();
//         this.startRecognition();
        
//         return true;
//     }

//     // Setup event handlers for robust operation
//     setupEventHandlers() {
//         this.recognition.onstart = () => {
//             this.isActive = true;
//             this.restartAttempts = 0;
//             console.log('🎙️ Speech recognition started');
//             this.updateMicrophoneUI(true);
//         };

//         this.recognition.onend = () => {
//             this.isActive = false;
//             console.log('🎙️ Speech recognition ended');
            
//             // Auto-restart if enabled and not manually stopped
//             if (this.autoRestart && this.restartAttempts < this.maxRestartAttempts) {
//                 setTimeout(() => {
//                     if (this.autoRestart) {
//                         this.startRecognition();
//                     }
//                 }, 100);
//             }
//         };

//         this.recognition.onerror = (event) => {
//             console.log('🎙️ Speech recognition error:', event.error);
            
//             // Handle specific errors
//             switch (event.error) {
//                 case 'no-speech':
//                 case 'audio-capture':
//                 case 'network':
//                     // Restart on recoverable errors
//                     this.restartAttempts++;
//                     if (this.restartAttempts < this.maxRestartAttempts) {
//                         setTimeout(() => {
//                             if (this.autoRestart) {
//                                 this.startRecognition();
//                             }
//                         }, 1000);
//                     }
//                     break;
//                 case 'not-allowed':
//                 case 'service-not-allowed':
//                     // Don't restart on permission errors
//                     this.autoRestart = false;
//                     this.showPermissionError();
//                     break;
//             }
//         };

//         this.recognition.onresult = (event) => {
//             // Handle speech recognition results
//             if (window.handleSpeechResult) {
//                 window.handleSpeechResult(event);
//             }
//         };
//     }

//     // Start speech recognition
//     startRecognition() {
//         if (!this.recognition || this.isActive) return;

//         try {
//             this.recognition.start();
//         } catch (error) {
//             console.error('Failed to start speech recognition:', error);
//         }
//     }

//     // Stop speech recognition
//     stopRecognition() {
//         if (this.recognition && this.isActive) {
//             this.autoRestart = false;
//             this.recognition.stop();
//             this.updateMicrophoneUI(false);
//         }
//     }

//     // Manually restart recognition
//     restartRecognition() {
//         this.autoRestart = true;
//         this.restartAttempts = 0;
//         if (this.isActive) {
//             this.recognition.stop();
//         } else {
//             this.startRecognition();
//         }
//     }

//     // Update microphone UI (always show as active in interview mode)
//     updateMicrophoneUI(active) {
//         const micBtn = document.getElementById('micBtn') || document.getElementById('muteBtn');
//         if (!micBtn) return;

//         // In interview mode, microphone should always appear active
//         // Only speech recognition state changes
//         if (active) {
//             micBtn.classList.add('recording', 'mic-active');
//             micBtn.classList.remove('mic-muted');
//             micBtn.innerHTML = '🎤';
//             micBtn.title = 'Microphone is ON - Speech recognition active';
//         } else {
//             micBtn.classList.remove('recording');
//             micBtn.classList.add('mic-active'); // Keep mic visually active
//             micBtn.classList.remove('mic-muted');
//             micBtn.innerHTML = '🎤';
//             micBtn.title = 'Microphone is ON - Speech recognition paused';
//         }
//     }

//     // Show permission error
//     showPermissionError() {
//         const errorDiv = document.createElement('div');
//         errorDiv.style.cssText = `
//             position: fixed;
//             top: 20px;
//             left: 50%;
//             transform: translateX(-50%);
//             background: #f44336;
//             color: white;
//             padding: 15px 25px;
//             border-radius: 8px;
//             z-index: 10000;
//             font-weight: bold;
//             text-align: center;
//         `;
//         errorDiv.innerHTML = `
//             🎙️ Microphone permission required for interview<br>
//             <small>Please allow microphone access and refresh the page</small>
//         `;
//         document.body.appendChild(errorDiv);
//     }
// }

// // Global instances
// window.professionalAudio = new ProfessionalInterviewAudio();
// window.professionalSpeech = new ProfessionalSpeechRecognition();

// // Initialize when DOM is ready
// document.addEventListener('DOMContentLoaded', function() {
//     console.log('🚀 Professional interview audio system loading...');
    
//     // Wait for user media to be available
//     const checkUserMedia = setInterval(() => {
//         if (window.userStream) {
//             clearInterval(checkUserMedia);
            
//             // Initialize professional audio
//             window.professionalAudio.initialize(window.userStream);
            
//             // Initialize professional speech recognition
//             window.professionalSpeech.initialize();
            
//             console.log('✅ Professional interview audio system ready');
//         }
//     }, 100);
    
//     // Cleanup on page unload
//     window.addEventListener('beforeunload', () => {
//         if (window.professionalAudio) {
//             window.professionalAudio.cleanup();
//         }
//         if (window.professionalSpeech) {
//             window.professionalSpeech.stopRecognition();
//         }
//     });
// });

// console.log('📁 Professional interview audio module loaded');
// console.log('🎙️ Interview mode: Microphone will stay ON throughout the interview');
// console.log('🔇 Speech recognition will be temporarily blocked when AI is speaking');