// Minimal fix to prevent AI speech from being recognized as candidate input
(function() {
    let aiSpeechActive = false;
    let speechTimeout = null;

    // Override playAIAudio to block speech recognition during AI speech
    const originalPlayAIAudio = window.playAIAudio;
    window.playAIAudio = function(audioUrl) {
        aiSpeechActive = true;
        
        // Immediately stop speech recognition
        if (window.continuousRecognition) {
            window.continuousRecognition.stop();
            window.continuousRecognition = null;
        }
        
        // Clear any pending speech timeouts
        if (speechTimeout) {
            clearTimeout(speechTimeout);
            speechTimeout = null;
        }

        if (audioUrl) {
            const audioPlayer = document.getElementById('aiAudioPlayer');
            const aiSpeakingIndicator = document.getElementById('aiSpeakingIndicator');
            
            if (aiSpeakingIndicator) aiSpeakingIndicator.style.display = 'block';
            
            audioPlayer.src = audioUrl;
            audioPlayer.onended = () => {
                if (aiSpeakingIndicator) aiSpeakingIndicator.style.display = 'none';
                
                // Wait 3 seconds after AI finishes before allowing speech recognition
                setTimeout(() => {
                    aiSpeechActive = false;
                    document.getElementById('voiceResponsePanel').style.display = 'block';
                    document.getElementById('responseStatus').innerHTML = 'You can speak now.';
                    
                    if (window.isMicOn) {
                        window.startContinuousListening();
                    }
                }, 3000);
            };
            
            audioPlayer.play().catch(() => {
                aiSpeechActive = false;
            });
        } else {
            setTimeout(() => {
                aiSpeechActive = false;
                document.getElementById('voiceResponsePanel').style.display = 'block';
                if (window.isMicOn) {
                    window.startContinuousListening();
                }
            }, 2000);
        }
    };

    // Override startContinuousListening to prevent activation during AI speech
    const originalStartListening = window.startContinuousListening;
    window.startContinuousListening = function() {
        if (aiSpeechActive) {
            console.log('Blocked: AI is speaking');
            return;
        }
        
        if (originalStartListening) {
            originalStartListening();
        }
    };

    // Enhanced audio constraints
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
            
            document.getElementById('userVideo').srcObject = window.stream;
            console.log('Camera initialized with AEC');
        } catch (error) {
            if (originalInitCamera) {
                return originalInitCamera();
            }
        }
    };

})();