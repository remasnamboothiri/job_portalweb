/**
 * Interview Microphone Always-On System
 * Ensures microphone stays on throughout the interview
 * Only controls speech recognition, not microphone hardware
 */

(function() {
    'use strict';
    
    console.log('🎤 Interview Microphone Always-On System Loading...');
    
    let microphoneAlwaysOn = true;
    let speechRecognitionEnabled = true;
    let aiCurrentlySpeaking = false;
    
    // Override any existing microphone toggle functions
    function ensureMicrophoneAlwaysOn() {
        // Keep microphone hardware always enabled
        if (window.userStream) {
            const audioTracks = window.userStream.getAudioTracks();
            audioTracks.forEach(track => {
                track.enabled = true; // Always keep microphone on
            });
        }
        
        // Update UI to reflect always-on state
        const micBtn = document.getElementById('muteBtn');
        if (micBtn) {
            if (speechRecognitionEnabled && !aiCurrentlySpeaking) {
                micBtn.classList.add('mic-active');
                micBtn.classList.remove('mic-muted');
                micBtn.innerHTML = '🎤';
                micBtn.title = 'Microphone ON - Speech recognition active';
            } else {
                micBtn.classList.add('mic-active'); // Still show as active
                micBtn.classList.remove('mic-muted');
                micBtn.innerHTML = '🎤';
                micBtn.title = 'Microphone ON - Speech recognition paused';
            }
        }
    }
    
    // Override the toggle microphone function
    function overrideMicrophoneToggle() {
        const micBtn = document.getElementById('muteBtn');
        if (micBtn) {
            // Remove existing event listeners
            const newMicBtn = micBtn.cloneNode(true);
            micBtn.parentNode.replaceChild(newMicBtn, micBtn);
            
            // Add new event listener that only controls speech recognition
            newMicBtn.addEventListener('click', function() {
                speechRecognitionEnabled = !speechRecognitionEnabled;
                
                if (speechRecognitionEnabled) {
                    console.log('🎤 Speech recognition enabled (microphone stays on)');
                    if (!aiCurrentlySpeaking && window.startSpeechRecognition) {
                        window.startSpeechRecognition();
                    }
                } else {
                    console.log('🔇 Speech recognition disabled (microphone stays on)');
                    if (window.stopSpeechRecognition) {
                        window.stopSpeechRecognition();
                    }
                }
                
                ensureMicrophoneAlwaysOn();
            });
        }
    }
    
    // Monitor AI speaking state
    function monitorAISpeaking() {
        // Watch for AI audio elements
        const aiAudioPlayer = document.getElementById('aiAudioPlayer');
        if (aiAudioPlayer) {
            aiAudioPlayer.addEventListener('play', function() {
                aiCurrentlySpeaking = true;
                console.log('🤖 AI started speaking - speech recognition paused (microphone stays on)');
                ensureMicrophoneAlwaysOn();
            });
            
            aiAudioPlayer.addEventListener('ended', function() {
                aiCurrentlySpeaking = false;
                console.log('🎤 AI finished speaking - speech recognition can resume (microphone was always on)');
                setTimeout(() => {
                    ensureMicrophoneAlwaysOn();
                    if (speechRecognitionEnabled && window.startSpeechRecognition) {
                        window.startSpeechRecognition();
                    }
                }, 1000);
            });
            
            aiAudioPlayer.addEventListener('pause', function() {
                aiCurrentlySpeaking = false;
                ensureMicrophoneAlwaysOn();
            });
            
            aiAudioPlayer.addEventListener('error', function() {
                aiCurrentlySpeaking = false;
                ensureMicrophoneAlwaysOn();
            });
        }
    }
    
    // Ensure microphone stays on during camera initialization
    function overrideCameraInitialization() {
        const originalGetUserMedia = navigator.mediaDevices.getUserMedia;
        
        navigator.mediaDevices.getUserMedia = function(constraints) {
            // Ensure audio is always enabled
            if (constraints && constraints.audio) {
                if (typeof constraints.audio === 'object') {
                    constraints.audio.enabled = true;
                } else {
                    constraints.audio = { enabled: true };
                }
            }
            
            return originalGetUserMedia.call(this, constraints).then(stream => {
                // Ensure all audio tracks are enabled
                const audioTracks = stream.getAudioTracks();
                audioTracks.forEach(track => {
                    track.enabled = true;
                });
                
                console.log('🎤 Camera initialized with microphone always ON');
                return stream;
            });
        };
    }
    
    // Initialize the always-on system
    function initializeAlwaysOnSystem() {
        console.log('🎤 Initializing microphone always-on system...');
        
        // Override camera initialization
        overrideCameraInitialization();
        
        // Set up microphone monitoring
        setInterval(ensureMicrophoneAlwaysOn, 2000); // Check every 2 seconds
        
        // Monitor for DOM changes and re-apply overrides
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList') {
                    // Re-apply overrides when DOM changes
                    setTimeout(() => {
                        overrideMicrophoneToggle();
                        monitorAISpeaking();
                        ensureMicrophoneAlwaysOn();
                    }, 100);
                }
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        console.log('✅ Microphone always-on system initialized');
    }
    
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(initializeAlwaysOnSystem, 500);
        });
    } else {
        setTimeout(initializeAlwaysOnSystem, 500);
    }
    
    // Apply overrides immediately if elements exist
    setTimeout(() => {
        overrideMicrophoneToggle();
        monitorAISpeaking();
        ensureMicrophoneAlwaysOn();
    }, 1000);
    
    // Expose functions for debugging
    window.interviewMicrophoneSystem = {
        ensureMicrophoneAlwaysOn,
        getSpeechRecognitionState: () => speechRecognitionEnabled,
        getAISpeakingState: () => aiCurrentlySpeaking,
        getMicrophoneState: () => microphoneAlwaysOn,
        forceEnable: () => {
            speechRecognitionEnabled = true;
            aiCurrentlySpeaking = false;
            ensureMicrophoneAlwaysOn();
        }
    };
    
    console.log('🎤 Interview Microphone Always-On System Loaded');
    console.log('📋 Available debug commands:');
    console.log('  - window.interviewMicrophoneSystem.getSpeechRecognitionState()');
    console.log('  - window.interviewMicrophoneSystem.getAISpeakingState()');
    console.log('  - window.interviewMicrophoneSystem.forceEnable()');
    
})();