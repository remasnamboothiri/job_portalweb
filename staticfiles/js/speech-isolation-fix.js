// Speech isolation fix: Keep microphone ON, prevent AI speech recognition
(function() {
    let aiSpeechActive = false;
    let speechTimeout = null;

    // Override playAIAudio to block speech recognition but keep microphone on
    const originalPlayAIAudio = window.playAIAudio;
    window.playAIAudio = function(audioUrl) {
        aiSpeechActive = true;
        
        // Stop speech recognition but keep microphone hardware active
        if (window.continuousRecognition) {
            window.continuousRecognition.stop();
            // Don't set to null - we'll restart it
        }
        
        // Clear any pending speech timeouts
        if (speechTimeout) {
            clearTimeout(speechTimeout);
            speechTimeout = null;
        }
        
        console.log('🤖 AI speaking - speech recognition isolated (microphone stays on)');

        if (audioUrl) {
            const audioPlayer = document.getElementById('aiAudioPlayer');
            const aiSpeakingIndicator = document.getElementById('aiSpeakingIndicator');
            
            if (aiSpeakingIndicator) aiSpeakingIndicator.style.display = 'block';
            
            audioPlayer.src = audioUrl;
            audioPlayer.onended = () => {
                if (aiSpeakingIndicator) aiSpeakingIndicator.style.display = 'none';
                
                // Wait 1 second after AI finishes before re-enabling speech recognition
                setTimeout(() => {
                    aiSpeechActive = false;
                    
                    const responsePanel = document.getElementById('voiceResponsePanel');
                    const responseStatus = document.getElementById('responseStatus');
                    if (responsePanel) responsePanel.style.display = 'block';
                    if (responseStatus) responseStatus.innerHTML = 'You can speak now (microphone is always on).';
                    
                    if (window.isMicOn && window.startContinuousListening) {
                        window.startContinuousListening();
                    }
                    
                    console.log('🎤 AI finished - speech recognition restored');
                }, 1000);
            };
            
            audioPlayer.onerror = () => {
                aiSpeechActive = false;
                console.log('🎤 AI audio error - speech recognition restored');
            };
            
            audioPlayer.play().catch(() => {
                aiSpeechActive = false;
                console.log('🎤 AI audio play failed - speech recognition restored');
            });
        } else {
            setTimeout(() => {
                aiSpeechActive = false;
                const responsePanel = document.getElementById('voiceResponsePanel');
                if (responsePanel) responsePanel.style.display = 'block';
                if (window.isMicOn && window.startContinuousListening) {
                    window.startContinuousListening();
                }
            }, 2000);
        }
    };

    // Override startContinuousListening to prevent activation during AI speech
    const originalStartListening = window.startContinuousListening;
    window.startContinuousListening = function() {
        if (aiSpeechActive) {
            console.log('🚫 Speech recognition blocked: AI is speaking (microphone hardware stays on)');
            return;
        }
        
        console.log('🎤 Starting speech recognition (microphone always active)');
        if (originalStartListening) {
            originalStartListening();
        }
    };

    // Enhanced audio constraints - microphone always on
    const originalInitCamera = window.initializeCamera;
    window.initializeCamera = async function() {
        try {
            window.stream = await navigator.mediaDevices.getUserMedia({
                video: true,
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                }
            });
            
            const userVideo = document.getElementById('userVideo');
            if (userVideo) {
                userVideo.srcObject = window.stream;
            }
            
            // Ensure audio tracks stay enabled (microphone always on)
            const audioTracks = window.stream.getAudioTracks();
            audioTracks.forEach(track => {
                track.enabled = true; // Keep microphone always on
            });
            
            console.log('🎤 Camera and microphone initialized - microphone will remain ON throughout interview');
        } catch (error) {
            console.error('Camera initialization failed:', error);
            if (originalInitCamera) {
                return originalInitCamera();
            }
        }
    };

    // Ensure microphone button shows always-on state
    setTimeout(() => {
        const micBtn = document.getElementById('muteBtn');
        if (micBtn) {
            micBtn.classList.add('mic-active');
            micBtn.classList.remove('mic-muted');
            micBtn.innerHTML = '🎤';
            micBtn.title = 'Microphone is always ON during interview - Controls speech recognition only';
            
            console.log('🎤 Microphone button configured for always-on interview mode');
        }
    }, 1000);

})();