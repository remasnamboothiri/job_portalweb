// WebRTC AEC (Acoustic Echo Cancellation) Fix for Interview
class WebRTCAECManager {
    constructor() {
        this.audioContext = null;
        this.mediaStream = null;
        this.echoCanceller = null;
    }

    // Initialize WebRTC with AEC
    async initializeAEC() {
        try {
            // Enhanced audio constraints with AEC
            const constraints = {
                video: {
                    width: { ideal: 1280 },
                    height: { ideal: 720 },
                    frameRate: { ideal: 30 }
                },
                audio: {
                    // Core AEC settings
                    echoCancellation: true,
                    echoCancellationType: 'system', // Use system-level AEC if available
                    noiseSuppression: true,
                    autoGainControl: true,
                    
                    // Advanced settings
                    sampleRate: { ideal: 48000 },
                    channelCount: { ideal: 1 },
                    latency: { ideal: 0.01 }, // Low latency for real-time
                    
                    // Additional echo cancellation settings
                    googEchoCancellation: true,
                    googAutoGainControl: true,
                    googNoiseSuppression: true,
                    googHighpassFilter: true,
                    googTypingNoiseDetection: true,
                    googAudioMirroring: false
                }
            };

            this.mediaStream = await navigator.mediaDevices.getUserMedia(constraints);
            
            // Verify AEC is enabled
            const audioTrack = this.mediaStream.getAudioTracks()[0];
            if (audioTrack) {
                const settings = audioTrack.getSettings();
                console.log('🔊 AEC Settings Applied:', {
                    echoCancellation: settings.echoCancellation,
                    noiseSuppression: settings.noiseSuppression,
                    autoGainControl: settings.autoGainControl,
                    sampleRate: settings.sampleRate,
                    channelCount: settings.channelCount
                });

                // Apply additional constraints if needed
                await this.applyAdvancedAECConstraints(audioTrack);
            }

            return this.mediaStream;
        } catch (error) {
            console.error('❌ AEC initialization failed:', error);
            throw error;
        }
    }

    // Apply advanced AEC constraints
    async applyAdvancedAECConstraints(audioTrack) {
        try {
            const advancedConstraints = {
                echoCancellation: { exact: true },
                noiseSuppression: { exact: true },
                autoGainControl: { exact: true }
            };

            await audioTrack.applyConstraints({ audio: advancedConstraints });
            console.log('✅ Advanced AEC constraints applied');
        } catch (error) {
            console.warn('⚠️ Could not apply advanced AEC constraints:', error);
        }
    }

    // Create audio context with AEC processing
    async createAudioContext() {
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)({
                sampleRate: 48000,
                latencyHint: 'interactive'
            });

            if (this.audioContext.state === 'suspended') {
                await this.audioContext.resume();
            }

            console.log('✅ Audio context created with AEC support');
            return this.audioContext;
        } catch (error) {
            console.error('❌ Audio context creation failed:', error);
            throw error;
        }
    }

    // Stop echo during AI speech
    muteInputDuringAIResponse() {
        if (this.mediaStream) {
            const audioTracks = this.mediaStream.getAudioTracks();
            audioTracks.forEach(track => {
                track.enabled = false;
            });
            console.log('🔇 Input muted during AI response');
        }
    }

    // Resume input after AI speech
    unmuteInputAfterAIResponse() {
        if (this.mediaStream) {
            const audioTracks = this.mediaStream.getAudioTracks();
            audioTracks.forEach(track => {
                track.enabled = true;
            });
            console.log('🎤 Input unmuted after AI response');
        }
    }

    // Cleanup
    cleanup() {
        if (this.mediaStream) {
            this.mediaStream.getTracks().forEach(track => track.stop());
        }
        if (this.audioContext) {
            this.audioContext.close();
        }
    }
}

// Global AEC manager instance
window.aecManager = new WebRTCAECManager();

// Override the original initializeCamera function
window.originalInitializeCamera = window.initializeCamera;
window.initializeCamera = async function() {
    try {
        console.log('🔊 Initializing camera with WebRTC AEC...');
        
        // Use AEC manager instead of basic getUserMedia
        const stream = await window.aecManager.initializeAEC();
        await window.aecManager.createAudioContext();
        
        const userVideo = document.getElementById('userVideo');
        if (userVideo) {
            userVideo.srcObject = stream;
        }
        
        // Store stream globally
        window.stream = stream;
        
        console.log('✅ Camera and microphone initialized with AEC');
        return stream;
    } catch (error) {
        console.error('❌ AEC camera initialization failed:', error);
        // Fallback to original method
        if (window.originalInitializeCamera) {
            return await window.originalInitializeCamera();
        }
        throw error;
    }
};

// Override playAIAudio to prevent echo
window.originalPlayAIAudio = window.playAIAudio;
window.playAIAudio = function(audioUrl) {
    // Mute input during AI speech to prevent echo
    window.aecManager.muteInputDuringAIResponse();
    
    // Stop any ongoing speech recognition
    if (window.continuousRecognition) {
        window.continuousRecognition.stop();
    }
    
    if (audioUrl) {
        const audioPlayer = document.getElementById('aiAudioPlayer');
        audioPlayer.src = audioUrl;
        
        const aiSpeakingIndicator = document.getElementById('aiSpeakingIndicator');
        if (aiSpeakingIndicator) {
            aiSpeakingIndicator.style.display = 'block';
        }
        
        audioPlayer.play().catch(error => {
            console.error('Error playing AI audio:', error);
        });
        
        audioPlayer.onended = () => {
            if (aiSpeakingIndicator) {
                aiSpeakingIndicator.style.display = 'none';
            }
            
            // Wait for echo to settle, then unmute input
            setTimeout(() => {
                window.aecManager.unmuteInputAfterAIResponse();
                
                // Restart speech recognition after delay
                setTimeout(() => {
                    const voicePanel = document.getElementById('voiceResponsePanel');
                    const responseStatus = document.getElementById('responseStatus');
                    
                    if (voicePanel) voicePanel.style.display = 'block';
                    if (responseStatus) responseStatus.innerHTML = 'Microphone is ready. You can speak now.';
                    
                    if (window.isMicOn && window.startContinuousListening) {
                        window.startContinuousListening();
                    }
                }, 1000);
            }, 500);
        };
    } else {
        // No audio case
        setTimeout(() => {
            window.aecManager.unmuteInputAfterAIResponse();
            
            const voicePanel = document.getElementById('voiceResponsePanel');
            const responseStatus = document.getElementById('responseStatus');
            
            if (voicePanel) voicePanel.style.display = 'block';
            if (responseStatus) responseStatus.innerHTML = 'Microphone is ready. You can speak now.';
            
            if (window.isMicOn && window.startContinuousListening) {
                window.startContinuousListening();
            }
        }, 2000);
    }
};

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.aecManager) {
        window.aecManager.cleanup();
    }
});

console.log('✅ WebRTC AEC fix loaded');