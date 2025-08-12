// Minimal fix for echo and speech recognition issues
(function() {
    let isAISpeaking = false;
    let speechRecognitionBlocked = false;

    // Override playAIAudio to completely stop speech recognition
    const originalPlayAIAudio = window.playAIAudio;
    window.playAIAudio = function(audioUrl) {
        isAISpeaking = true;
        speechRecognitionBlocked = true;
        
        // Immediately stop and disable speech recognition
        if (window.continuousRecognition) {
            window.continuousRecognition.stop();
            window.continuousRecognition = null;
        }
        
        // Show AI speaking indicator
        const aiSpeakingIndicator = document.getElementById('aiSpeakingIndicator');
        if (aiSpeakingIndicator) {
            aiSpeakingIndicator.style.display = 'block';
        }

        if (audioUrl) {
            const audioPlayer = document.getElementById('aiAudioPlayer');
            audioPlayer.src = audioUrl;
            
            audioPlayer.onended = () => {
                isAISpeaking = false;
                if (aiSpeakingIndicator) {
                    aiSpeakingIndicator.style.display = 'none';
                }
                
                // Wait 2 seconds after AI stops, then allow speech recognition
                setTimeout(() => {
                    speechRecognitionBlocked = false;
                    document.getElementById('voiceResponsePanel').style.display = 'block';
                    document.getElementById('responseStatus').innerHTML = 'You can speak now.';
                    
                    if (window.isMicOn) {
                        window.startContinuousListening();
                    }
                }, 2000);
            };
            
            audioPlayer.play().catch(error => {
                console.error('Audio play failed:', error);
                isAISpeaking = false;
                speechRecognitionBlocked = false;
            });
        } else {
            // No audio case
            setTimeout(() => {
                isAISpeaking = false;
                speechRecognitionBlocked = false;
                document.getElementById('voiceResponsePanel').style.display = 'block';
                document.getElementById('responseStatus').innerHTML = 'You can speak now.';
                if (window.isMicOn) {
                    window.startContinuousListening();
                }
            }, 2000);
        }
    };

    // Override startContinuousListening to prevent activation during AI speech
    const originalStartContinuousListening = window.startContinuousListening;
    window.startContinuousListening = function() {
        if (speechRecognitionBlocked || isAISpeaking) {
            console.log('Speech recognition blocked - AI is speaking');
            return;
        }
        
        if (originalStartContinuousListening) {
            originalStartContinuousListening();
        }
    };

    // Enhanced getUserMedia with better AEC
    const originalInitializeCamera = window.initializeCamera;
    window.initializeCamera = async function() {
        try {
            const constraints = {
                video: true,
                audio: {
                    echoCancellation: { exact: true },
                    noiseSuppression: { exact: true },
                    autoGainControl: { exact: true },
                    sampleRate: 48000
                }
            };
            
            window.stream = await navigator.mediaDevices.getUserMedia(constraints);
            const userVideo = document.getElementById('userVideo');
            if (userVideo) {
                userVideo.srcObject = window.stream;
            }
            console.log('Camera initialized with enhanced AEC');
        } catch (error) {
            console.error('Enhanced camera failed, using fallback:', error);
            if (originalInitializeCamera) {
                return await originalInitializeCamera();
            }
        }
    };

})();