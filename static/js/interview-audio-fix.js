// Interview audio fix: Keep microphone always ON, only control speech recognition
(function() {
    let isAISpeaking = false;
    let speechRecognitionBlocked = false;

    // Override playAIAudio to block speech recognition but keep mic on
    const originalPlayAIAudio = window.playAIAudio;
    window.playAIAudio = function(audioUrl) {
        isAISpeaking = true;
        speechRecognitionBlocked = true;
        
        // Stop speech recognition but keep microphone hardware on
        if (window.continuousRecognition) {
            window.continuousRecognition.stop();
            // Don't set to null - we want to restart it later
        }
        
        // Show AI speaking indicator
        const aiSpeakingIndicator = document.getElementById('aiSpeakingIndicator');
        if (aiSpeakingIndicator) {
            aiSpeakingIndicator.style.display = 'block';
        }
        
        console.log('🤖 AI speaking - speech recognition blocked (microphone stays on)');

        if (audioUrl) {
            const audioPlayer = document.getElementById('aiAudioPlayer');
            audioPlayer.src = audioUrl;
            
            audioPlayer.onended = () => {
                isAISpeaking = false;
                if (aiSpeakingIndicator) {
                    aiSpeakingIndicator.style.display = 'none';
                }
                
                // Wait 1 second after AI stops, then re-enable speech recognition
                setTimeout(() => {
                    speechRecognitionBlocked = false;
                    
                    // Always show that user can speak (mic is always on)
                    const responsePanel = document.getElementById('voiceResponsePanel');
                    const responseStatus = document.getElementById('responseStatus');
                    if (responsePanel) responsePanel.style.display = 'block';
                    if (responseStatus) responseStatus.innerHTML = 'You can speak now (microphone is always on).';
                    
                    // Restart speech recognition if mic is conceptually "on"
                    if (window.isMicOn && window.startContinuousListening) {
                        window.startContinuousListening();
                    }
                    
                    console.log('🎤 AI finished - speech recognition re-enabled');
                }, 1000);
            };
            
            audioPlayer.onerror = (error) => {
                console.error('Audio play failed:', error);
                isAISpeaking = false;
                speechRecognitionBlocked = false;
            };
            
            audioPlayer.play().catch(error => {
                console.error('Audio play failed:', error);
                isAISpeaking = false;
                speechRecognitionBlocked = false;
            });
        } else {
            // No audio case - simulate AI speaking time
            setTimeout(() => {
                isAISpeaking = false;
                speechRecognitionBlocked = false;
                
                const responsePanel = document.getElementById('voiceResponsePanel');
                const responseStatus = document.getElementById('responseStatus');
                if (responsePanel) responsePanel.style.display = 'block';
                if (responseStatus) responseStatus.innerHTML = 'You can speak now (microphone is always on).';
                
                if (window.isMicOn && window.startContinuousListening) {
                    window.startContinuousListening();
                }
            }, 2000);
        }
    };

    // Override startContinuousListening to prevent activation during AI speech
    const originalStartContinuousListening = window.startContinuousListening;
    window.startContinuousListening = function() {
        if (speechRecognitionBlocked || isAISpeaking) {
            console.log('🚫 Speech recognition blocked - AI is speaking (microphone hardware stays on)');
            return;
        }
        
        console.log('🎤 Starting speech recognition (microphone always on)');
        if (originalStartContinuousListening) {
            originalStartContinuousListening();
        }
    };

    // Enhanced getUserMedia with better AEC - microphone always on
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
            
            // Ensure audio tracks are always enabled (microphone always on)
            const audioTracks = window.stream.getAudioTracks();
            audioTracks.forEach(track => {
                track.enabled = true; // Always keep microphone on
            });
            
            console.log('🎤 Camera and microphone initialized - microphone will stay ON during interview');
            console.log('🔇 Speech recognition will be controlled separately from microphone hardware');
        } catch (error) {
            console.error('Enhanced camera failed, using fallback:', error);
            if (originalInitializeCamera) {
                return await originalInitializeCamera();
            }
        }
    };

    // Ensure microphone button reflects always-on state
    const micBtn = document.getElementById('muteBtn');
    if (micBtn) {
        // Override the toggle function to only control speech recognition
        const originalToggle = micBtn.onclick;
        micBtn.onclick = function() {
            // Don't actually mute the microphone hardware
            // Only toggle speech recognition state
            window.isMicOn = !window.isMicOn;
            
            if (window.isMicOn) {
                micBtn.classList.add('mic-active');
                micBtn.classList.remove('mic-muted');
                micBtn.innerHTML = '🎤';
                micBtn.title = 'Speech recognition ON (microphone always on)';
                
                if (!speechRecognitionBlocked && !isAISpeaking && window.startContinuousListening) {
                    window.startContinuousListening();
                }
            } else {
                micBtn.classList.remove('mic-active');
                micBtn.classList.add('mic-muted');
                micBtn.innerHTML = '🔇';
                micBtn.title = 'Speech recognition OFF (microphone hardware stays on)';
                
                if (window.continuousRecognition) {
                    window.continuousRecognition.stop();
                }
            }
            
            console.log(`Speech recognition ${window.isMicOn ? 'enabled' : 'disabled'} (microphone hardware always on)`);
        };
        
        // Set initial state
        micBtn.classList.add('mic-active');
        micBtn.innerHTML = '🎤';
        micBtn.title = 'Speech recognition ON (microphone always on)';
    }

})();