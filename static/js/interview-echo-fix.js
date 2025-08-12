// Comprehensive Interview Echo Fix and Partial Question Display
(function() {
    'use strict';

    // Echo Prevention Manager
    class EchoPreventionManager {
        constructor() {
            this.isAISpeaking = false;
            this.echoDelay = 1000; // 1 second delay after AI stops speaking
            this.originalVolume = 1.0;
        }

        // Prevent echo during AI speech
        preventEchoDuringAISpeech() {
            this.isAISpeaking = true;
            
            // Stop speech recognition immediately
            if (window.continuousRecognition) {
                try {
                    window.continuousRecognition.stop();
                    console.log('🔇 Speech recognition stopped to prevent echo');
                } catch (e) {
                    console.warn('Could not stop speech recognition:', e);
                }
            }

            // Mute microphone input if available
            if (window.stream) {
                const audioTracks = window.stream.getAudioTracks();
                audioTracks.forEach(track => {
                    track.enabled = false;
                });
                console.log('🔇 Microphone muted during AI speech');
            }
        }

        // Resume after AI speech with delay
        resumeAfterAISpeech() {
            setTimeout(() => {
                this.isAISpeaking = false;
                
                // Unmute microphone
                if (window.stream) {
                    const audioTracks = window.stream.getAudioTracks();
                    audioTracks.forEach(track => {
                        track.enabled = true;
                    });
                    console.log('🎤 Microphone unmuted after AI speech');
                }

                // Restart speech recognition with additional delay
                setTimeout(() => {
                    if (window.isMicOn && window.startContinuousListening) {
                        window.startContinuousListening();
                        console.log('🎤 Speech recognition restarted');
                    }
                }, 500);
                
            }, this.echoDelay);
        }
    }

    // Initialize echo prevention
    const echoManager = new EchoPreventionManager();

    // Enhanced getUserMedia with AEC
    async function getEnhancedMediaStream() {
        const constraints = {
            video: {
                width: { ideal: 1280 },
                height: { ideal: 720 }
            },
            audio: {
                // Primary AEC settings
                echoCancellation: true,
                noiseSuppression: true,
                autoGainControl: true,
                
                // Advanced settings
                sampleRate: { ideal: 48000 },
                channelCount: { ideal: 1 },
                
                // Browser-specific AEC settings
                googEchoCancellation: true,
                googAutoGainControl: true,
                googNoiseSuppression: true,
                googHighpassFilter: true,
                googTypingNoiseDetection: true,
                mozEchoCancellation: true,
                mozAutoGainControl: true,
                mozNoiseSuppression: true
            }
        };

        try {
            const stream = await navigator.mediaDevices.getUserMedia(constraints);
            
            // Verify AEC settings
            const audioTrack = stream.getAudioTracks()[0];
            if (audioTrack) {
                const settings = audioTrack.getSettings();
                console.log('🔊 Enhanced AEC Settings:', {
                    echoCancellation: settings.echoCancellation,
                    noiseSuppression: settings.noiseSuppression,
                    autoGainControl: settings.autoGainControl
                });
            }
            
            return stream;
        } catch (error) {
            console.error('Enhanced media stream failed, falling back to basic:', error);
            // Fallback to basic constraints
            return await navigator.mediaDevices.getUserMedia({
                video: true,
                audio: { echoCancellation: true }
            });
        }
    }

    // Override initializeCamera with enhanced AEC
    const originalInitializeCamera = window.initializeCamera;
    window.initializeCamera = async function() {
        try {
            console.log('🔊 Initializing camera with enhanced AEC...');
            
            window.stream = await getEnhancedMediaStream();
            const userVideo = document.getElementById('userVideo');
            if (userVideo) {
                userVideo.srcObject = window.stream;
            }
            
            console.log('✅ Camera initialized with enhanced echo cancellation');
        } catch (error) {
            console.error('❌ Enhanced camera initialization failed:', error);
            if (originalInitializeCamera) {
                return await originalInitializeCamera();
            }
            throw error;
        }
    };

    // Override playAIAudio with echo prevention
    const originalPlayAIAudio = window.playAIAudio;
    window.playAIAudio = function(audioUrl) {
        console.log('🔊 Playing AI audio with echo prevention');
        
        // Prevent echo immediately
        echoManager.preventEchoDuringAISpeech();
        
        if (!audioUrl || audioUrl === 'None' || audioUrl === null) {
            console.log('❌ No valid audio URL provided');
            echoManager.resumeAfterAISpeech();
            return;
        }

        const audioPlayer = document.getElementById('aiAudioPlayer');
        if (!audioPlayer) {
            console.error('❌ Audio player not found');
            echoManager.resumeAfterAISpeech();
            return;
        }

        // Show AI speaking indicator
        const aiSpeakingIndicator = document.getElementById('aiSpeakingIndicator');
        if (aiSpeakingIndicator) {
            aiSpeakingIndicator.style.display = 'block';
        }

        audioPlayer.src = audioUrl;
        
        audioPlayer.onended = () => {
            console.log('🔊 AI audio finished');
            if (aiSpeakingIndicator) {
                aiSpeakingIndicator.style.display = 'none';
            }
            echoManager.resumeAfterAISpeech();
            
            // Show voice response panel
            setTimeout(() => {
                const voicePanel = document.getElementById('voiceResponsePanel');
                const responseStatus = document.getElementById('responseStatus');
                
                if (voicePanel) voicePanel.style.display = 'block';
                if (responseStatus) responseStatus.innerHTML = 'Microphone is ready. You can speak now.';
            }, 1000);
        };

        audioPlayer.onerror = (error) => {
            console.error('❌ Audio playback error:', error);
            if (aiSpeakingIndicator) {
                aiSpeakingIndicator.style.display = 'none';
            }
            echoManager.resumeAfterAISpeech();
        };

        audioPlayer.play().catch(error => {
            console.error('❌ Audio play failed:', error);
            echoManager.resumeAfterAISpeech();
        });
    };

    // Partial Question Display
    function createPartialQuestionDisplay(fullText, maxLength = 50) {
        if (fullText.length <= maxLength) {
            return fullText;
        }

        const truncated = fullText.substring(0, maxLength).trim();
        const questionId = 'question_' + Date.now();
        
        return `
            <span id="${questionId}_preview">${truncated}...</span>
            <span id="${questionId}_full" style="display: none;">${fullText}</span>
            <button onclick="showFullQuestion('${questionId}')" 
                    style="background: #1a73e8; color: white; border: none; padding: 2px 6px; 
                           border-radius: 3px; font-size: 11px; margin-left: 5px; cursor: pointer;">
                Show Full
            </button>
        `;
    }

    // Global function to show full question
    window.showFullQuestion = function(questionId) {
        const preview = document.getElementById(questionId + '_preview');
        const full = document.getElementById(questionId + '_full');
        const button = event.target;
        
        if (preview && full) {
            preview.style.display = 'none';
            full.style.display = 'inline';
            button.style.display = 'none';
        }
    };

    // Override handleAIResponse with partial display
    const originalHandleAIResponse = window.handleAIResponse;
    window.handleAIResponse = function(data) {
        // Hide voice response panel
        const voicePanel = document.getElementById('voiceResponsePanel');
        if (voicePanel) {
            voicePanel.style.display = 'none';
        }
        
        // Update question counter
        window.currentQuestionCount = data.question_count || window.currentQuestionCount + 1;
        const questionCounter = document.getElementById('questionCounter');
        if (questionCounter) {
            questionCounter.textContent = `${window.currentQuestionCount}/8`;
        }
        
        // Update progress bar
        const progress = (window.currentQuestionCount / 8) * 100;
        const progressBar = document.getElementById('progressBar');
        if (progressBar) {
            progressBar.style.width = `${progress}%`;
        }
        
        // Show AI response with partial display
        const subtitleText = document.getElementById('subtitleText');
        if (subtitleText && data.response) {
            const partialDisplay = createPartialQuestionDisplay(data.response);
            subtitleText.innerHTML = `AI: "${partialDisplay}"`;
        }
        
        const subtitleOverlay = document.getElementById('subtitleOverlay');
        if (subtitleOverlay) {
            subtitleOverlay.classList.add('show');
        }
        
        // Play AI audio with echo prevention
        if (data.audio) {
            window.playAIAudio(data.audio);
        } else {
            // No audio case - still prevent echo
            echoManager.resumeAfterAISpeech();
            setTimeout(() => {
                if (!data.is_final) {
                    if (voicePanel) voicePanel.style.display = 'block';
                    const responseStatus = document.getElementById('responseStatus');
                    if (responseStatus) {
                        responseStatus.innerHTML = 'Microphone is ready. You can speak now.';
                    }
                } else if (window.showCompletionModal) {
                    window.showCompletionModal();
                }
            }, 1500);
        }
        
        // Hide subtitles after delay
        setTimeout(() => {
            if (subtitleOverlay) {
                subtitleOverlay.classList.remove('show');
            }
        }, 8000);
        
        // Check if interview complete
        if (data.is_final || window.currentQuestionCount >= 8) {
            setTimeout(() => {
                if (window.showCompletionModal) {
                    window.showCompletionModal();
                }
            }, 2000);
        }
    };

    // Initialize on DOM ready
    document.addEventListener('DOMContentLoaded', function() {
        console.log('✅ Interview echo fix and partial question display loaded');
        
        // Handle initial question display
        const subtitleText = document.getElementById('subtitleText');
        if (subtitleText && subtitleText.textContent) {
            const match = subtitleText.textContent.match(/AI: "(.+)"/);
            if (match && match[1]) {
                const partialDisplay = createPartialQuestionDisplay(match[1]);
                subtitleText.innerHTML = `AI: "${partialDisplay}"`;
            }
        }
    });

    // Cleanup on page unload
    window.addEventListener('beforeunload', () => {
        if (window.stream) {
            window.stream.getTracks().forEach(track => track.stop());
        }
    });

})();