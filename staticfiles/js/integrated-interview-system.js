/**
 * INTEGRATED AI INTERVIEW SYSTEM
 * Single unified system handling all audio/video/speech recognition
 * This replaces the inline script in your HTML template
 */

// Global variables - centralized
let recognition = null;
let isListening = false;
let questionCount = 1;
let timeLeft = 15 * 60;
let userStream = null;
let isCameraOn = true;
let audioContext = null;
let microphoneSource = null;
let echoCancellation = null;

// Speech handling
let collectedText = '';
let speechTimeout = null;
let lastSpeechTime = 0;
let isProcessingResponse = false;

// Enhanced audio isolation
let isAISpeaking = false;
let speechRecognitionBlocked = false;

/**
 * STEP 1: Initialize Camera and Audio Together
 */
async function initCamera() {
    try {
        console.log('🎥 Initializing camera and microphone...');
        
        // Single getUserMedia call for both video and audio
        userStream = await navigator.mediaDevices.getUserMedia({ 
            video: true, 
            audio: {
                echoCancellation: true,
                noiseSuppression: true,
                autoGainControl: true,
                sampleRate: 44100
            }
        });
        
        // Set up video display
        const videoElement = document.getElementById('userVideo');
        videoElement.srcObject = userStream;
        
        // Make stream globally available
        window.userStream = userStream;
        
        // Setup enhanced audio isolation
        await setupEnhancedAudioIsolation();
        
        console.log('✅ Camera and microphone initialized successfully');
        return true;
        
    } catch (error) {
        console.error('❌ Camera/microphone initialization failed:', error);
        showInitializationError(error);
        return false;
    }
}

/**
 * STEP 2: Enhanced Audio Isolation Setup
 */
async function setupEnhancedAudioIsolation() {
    try {
        // Create audio context for processing
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        
        // Create microphone source from stream
        microphoneSource = audioContext.createMediaStreamSource(userStream);
        
        // Create gain node for volume control
        const gainNode = audioContext.createGain();
        gainNode.gain.value = 1.0;
        
        // Create compressor for consistent levels
        const compressor = audioContext.createDynamicsCompressor();
        compressor.threshold.value = -24;
        compressor.knee.value = 30;
        compressor.ratio.value = 12;
        compressor.attack.value = 0.003;
        compressor.release.value = 0.25;
        
        // Connect audio processing chain
        microphoneSource.connect(gainNode).connect(compressor);
        
        // Setup AI audio monitoring
        setupAIAudioMonitoring();
        
        console.log('🔊 Enhanced audio isolation configured');
        
    } catch (error) {
        console.error('❌ Audio isolation setup failed:', error);
    }
}

/**
 * STEP 3: AI Audio Monitoring (Prevents Feedback)
 */
function setupAIAudioMonitoring() {
    const aiAudio = document.getElementById('aiAudio');
    if (!aiAudio) return;

    // Set optimal volume to prevent feedback
    aiAudio.volume = 0.6;
    
    // Monitor AI audio events
    aiAudio.addEventListener('play', () => {
        console.log('🔇 AI started speaking - blocking speech recognition');
        isAISpeaking = true;
        speechRecognitionBlocked = true;
        isProcessingResponse = true;
        
        // Stop current speech recognition
        if (recognition && isListening) {
            try {
                recognition.abort();
            } catch (e) {
                console.log('Could not abort recognition:', e);
            }
        }
        
        // Clear any pending speech timeouts
        if (speechTimeout) {
            clearTimeout(speechTimeout);
            speechTimeout = null;
        }
    });

    aiAudio.addEventListener('ended', () => {
        console.log('🎙️ AI finished speaking - enabling speech recognition');
        isAISpeaking = false;
        
        // Wait a moment then re-enable speech recognition
        setTimeout(() => {
            speechRecognitionBlocked = false;
            isProcessingResponse = false;
            
            // Restart speech recognition
            if (isListening) {
                startSpeechRecognition();
            }
        }, 1000);
    });

    aiAudio.addEventListener('pause', () => {
        console.log('🎙️ AI audio paused - enabling speech recognition');
        isAISpeaking = false;
        speechRecognitionBlocked = false;
        isProcessingResponse = false;
        
        if (isListening) {
            setTimeout(() => startSpeechRecognition(), 500);
        }
    });
    
    // Fallback timeout in case audio events don't fire
    aiAudio.addEventListener('play', () => {
        setTimeout(() => {
            if (isAISpeaking) {
                console.log('⏰ Fallback: Unblocking speech recognition');
                isAISpeaking = false;
                speechRecognitionBlocked = false;
                isProcessingResponse = false;
                if (isListening) startSpeechRecognition();
            }
        }, 15000); // 15 second fallback
    });
}

/**
 * STEP 4: Initialize Speech Recognition (Single Instance)
 */
function initSpeech() {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        console.error('❌ Speech recognition not supported');
        showBrowserError();
        return false;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';
    recognition.maxAlternatives = 1;
    
    recognition.onstart = function() {
        if (!speechRecognitionBlocked) {
            console.log('🎙️ Speech recognition started');
            updateMicrophoneUI(true);
        }
    };
    
    recognition.onend = function() {
        console.log('🎙️ Speech recognition ended');
        updateMicrophoneUI(false);
        
        // Auto-restart if should be listening and not blocked
        if (isListening && !speechRecognitionBlocked && !isProcessingResponse) {
            setTimeout(() => {
                if (isListening && !speechRecognitionBlocked && !isProcessingResponse) {
                    startSpeechRecognition();
                }
            }, 100);
        }
    };
    
    recognition.onerror = function(event) {
        console.log('🎙️ Speech recognition error:', event.error);
        
        // Handle different error types
        switch (event.error) {
            case 'no-speech':
                // Normal, just restart
                break;
            case 'audio-capture':
                console.error('❌ No microphone access for speech recognition');
                showMicrophoneAccessError();
                break;
            case 'network':
                // Restart after delay
                setTimeout(() => {
                    if (isListening && !speechRecognitionBlocked) {
                        startSpeechRecognition();
                    }
                }, 1000);
                break;
            case 'not-allowed':
                console.error('❌ Microphone permission denied');
                showPermissionError();
                isListening = false;
                break;
        }
    };
    
    recognition.onresult = function(event) {
        // Block processing if AI is speaking
        if (speechRecognitionBlocked || isAISpeaking || isProcessingResponse) {
            console.log('🔇 Speech blocked - AI speaking or processing');
            return;
        }
        
        handleSpeechResult(event);
    };
    
    // Start automatically
    startMicrophone();
    return true;
}

/**
 * STEP 5: Start Speech Recognition
 */
function startSpeechRecognition() {
    if (!recognition || speechRecognitionBlocked || isAISpeaking || isProcessingResponse) {
        return;
    }
    
    try {
        recognition.start();
    } catch (error) {
        console.log('Speech recognition start failed:', error);
    }
}

/**
 * STEP 6: Handle Speech Results with Auto-Submit
 */
function handleSpeechResult(event) {
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
    
    // Filter out potential AI echo
    const aiPhrases = ['tell me about', 'can you describe', 'what are your', 'how do you', 'thank you for'];
    const textLower = (finalTranscript + interimTranscript).toLowerCase();
    
    if (aiPhrases.some(phrase => textLower.includes(phrase))) {
        console.log('🔇 AI echo detected, ignoring');
        return;
    }
    
    // Collect final text
    if (finalTranscript.trim()) {
        collectedText += finalTranscript;
        lastSpeechTime = Date.now();
        
        // Clear existing timeout
        if (speechTimeout) {
            clearTimeout(speechTimeout);
        }
        
        // Auto-submit after 1 second of silence
        speechTimeout = setTimeout(() => {
            if (collectedText.trim() && !isProcessingResponse && !speechRecognitionBlocked) {
                autoSubmitResponse();
            }
        }, 1000);
    }
    
    // Update UI with live transcription
    const displayText = collectedText + interimTranscript;
    if (displayText.trim()) {
        const conversationArea = document.getElementById('conversationArea');
        if (conversationArea) {
            conversationArea.innerHTML = displayText;
            conversationArea.className = 'conversation-text live-transcription';
        }
        
        // Update audio level indicator
        updateAudioLevelIndicator(interimTranscript ? 70 : 30);
        
        if (interimTranscript.trim()) {
            lastSpeechTime = Date.now();
        }
    }
}

/**
 * STEP 7: Auto-Submit Response
 */
function autoSubmitResponse() {
    if (isProcessingResponse || !collectedText.trim() || speechRecognitionBlocked) {
        return;
    }
    
    console.log('📤 Auto-submitting response:', collectedText);
    isProcessingResponse = true;
    speechRecognitionBlocked = true;
    
    // Stop speech recognition
    if (recognition) {
        try {
            recognition.abort();
        } catch (e) {
            console.log('Could not abort recognition:', e);
        }
    }
    
    // Clear timeout
    if (speechTimeout) {
        clearTimeout(speechTimeout);
        speechTimeout = null;
    }
    
    // Send response
    const responseText = collectedText.trim();
    collectedText = '';
    
    sendResponse(responseText);
}

/**
 * STEP 8: Send Response to Server
 */
async function sendResponse(text) {
    try {
        console.log('📤 Sending response to server:', text);
        
        const response = await fetch(window.location.href, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            },
            body: new URLSearchParams({ text: text })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Show new question
            showCurrentQuestion(data.response, data.audio, data.audio_duration);
            
            // Update counter
            questionCount = data.question_count || questionCount + 1;
            document.getElementById('questionCount').textContent = questionCount + '/8';
            
            // Handle audio response
            if (data.audio && data.audio.trim() !== '' && data.audio !== 'None') {
                // Keep speech blocked until audio ends (handled by audio event listeners)
                console.log('🔊 AI will speak - keeping speech recognition blocked');
            } else {
                // No audio, unblock after short delay
                setTimeout(() => {
                    isProcessingResponse = false;
                    speechRecognitionBlocked = false;
                    console.log('✅ Ready for next response (no audio)');
                }, 1000);
            }
            
            // Check if interview complete
            if (data.is_final || questionCount >= 8) {
                setTimeout(endInterview, 3000);
            }
        }
        
    } catch (error) {
        console.error('❌ Send response error:', error);
        // Reset flags on error
        isProcessingResponse = false;
        speechRecognitionBlocked = false;
    }
}

/**
 * STEP 9: Question Display with Audio Sync
 */
function showCurrentQuestion(question, audioUrl = null, audioDuration = null) {
    const element = document.getElementById('conversationArea');
    element.innerHTML = '';
    element.className = 'conversation-text ai-speaking';
    
    if (audioUrl && audioUrl.trim() !== '' && audioUrl !== 'None') {
        console.log('🔊 Playing AI question with audio');
        
        const audio = document.getElementById('aiAudio');
        audio.src = audioUrl;
        
        audio.oncanplaythrough = () => {
            // Start audio
            audio.play().then(() => {
                // Sync typewriter with audio
                const duration = audioDuration || audio.duration || 5;
                const charDelay = (duration * 1000) / question.length;
                
                let index = 0;
                const typeChar = () => {
                    if (index < question.length) {
                        element.innerHTML += question.charAt(index);
                        index++;
                        setTimeout(typeChar, charDelay);
                    }
                };
                typeChar();
                
            }).catch(error => {
                console.error('Audio play failed:', error);
                naturalTypewriter(element, question);
            });
        };
        
        audio.onerror = () => {
            console.error('Audio loading failed');
            naturalTypewriter(element, question);
        };
        
        audio.load();
        
    } else {
        // No audio, use natural typing
        naturalTypewriter(element, question);
        
        // Unblock after typing completes
        setTimeout(() => {
            if (!audioUrl || audioUrl.trim() === '' || audioUrl === 'None') {
                isProcessingResponse = false;
                speechRecognitionBlocked = false;
            }
        }, question.length * 50 + 1000);
    }
}

/**
 * Natural typewriter effect
 */
function naturalTypewriter(element, text) {
    let index = 0;
    const typeChar = () => {
        if (index < text.length) {
            element.innerHTML += text.charAt(index);
            index++;
            setTimeout(typeChar, 50);
        }
    };
    typeChar();
}

/**
 * UI Update Functions
 */
function updateMicrophoneUI(active) {
    const micBtn = document.getElementById('micBtn');
    if (!micBtn) return;
    
    if (active && isListening) {
        micBtn.classList.add('recording');
        micBtn.innerHTML = '🔴 ON';
        micBtn.title = 'Microphone is ON - Recording';
    } else {
        micBtn.classList.remove('recording');
        micBtn.innerHTML = '🎤 ON';
        micBtn.title = 'Microphone is ON - Ready';
    }
}

function updateAudioLevelIndicator(level = 0) {
    const indicator = document.getElementById('audioLevelIndicator');
    if (!indicator) return;
    
    const bars = indicator.querySelectorAll('.audio-level-bar');
    const activeCount = Math.floor((level / 100) * bars.length);
    
    bars.forEach((bar, index) => {
        if (index < activeCount) {
            bar.classList.add('active');
        } else {
            bar.classList.remove('active');
        }
    });
}

/**
 * Control Functions
 */
function startMicrophone() {
    if (!isListening) {
        isListening = true;
        collectedText = '';
        if (!speechRecognitionBlocked && !isProcessingResponse) {
            startSpeechRecognition();
        }
        console.log('🎙️ Microphone activated for professional interview');
    }
}

function toggleMic() {
    if (isListening) {
        if (confirm('Turn off microphone? Not recommended during interview.')) {
            isListening = false;
            speechRecognitionBlocked = true;
            isProcessingResponse = true;
            
            if (recognition) {
                recognition.abort();
            }
            
            if (speechTimeout) {
                clearTimeout(speechTimeout);
                speechTimeout = null;
            }
            
            if (collectedText.trim()) {
                sendResponse(collectedText.trim());
                collectedText = '';
            }
            
            updateMicrophoneUI(false);
            showWarningMessage('Microphone OFF. Click to reactivate.');
        }
    } else {
        // Reactivate microphone
        isListening = true;
        speechRecognitionBlocked = false;
        isProcessingResponse = false;
        collectedText = '';
        startSpeechRecognition();
        hideWarningMessage();
        updateMicrophoneUI(true);
    }
}

function toggleCamera() {
    if (!userStream) return;
    
    const videoTracks = userStream.getVideoTracks();
    isCameraOn = !isCameraOn;
    
    videoTracks.forEach(track => {
        track.enabled = isCameraOn;
    });
    
    const btn = document.getElementById('cameraBtn');
    if (isCameraOn) {
        btn.innerHTML = '📹 ON';
        btn.classList.remove('camera-off');
    } else {
        btn.innerHTML = '📹 OFF';
        btn.classList.add('camera-off');
    }
}

/**
 * Timer and Interview Control
 */
function updateTimer() {
    const minutes = Math.floor(timeLeft / 60);
    const seconds = timeLeft % 60;
    document.getElementById('timer').textContent = 
        minutes + ':' + seconds.toString().padStart(2, '0');
    
    if (timeLeft <= 0) {
        endInterview();
        return;
    }
    timeLeft--;
}

function endInterview() {
    console.log('🏁 Ending interview...');
    
    // Stop everything
    isListening = false;
    speechRecognitionBlocked = true;
    isProcessingResponse = true;
    
    if (recognition) {
        recognition.abort();
    }
    
    if (userStream) {
        userStream.getTracks().forEach(track => track.stop());
    }
    
    if (audioContext && audioContext.state !== 'closed') {
        audioContext.close();
    }
    
    alert('Interview completed! Redirecting to dashboard...');
    window.location.href = '/jobseeker/dashboard/';
}

/**
 * Error Handling Functions
 */
function showInitializationError(error) {
    const errorDiv = document.createElement('div');
    errorDiv.style.cssText = `
        position: fixed; top: 20px; left: 50%; transform: translateX(-50%);
        background: #f44336; color: white; padding: 15px 25px;
        border-radius: 8px; z-index: 10000; font-weight: bold; text-align: center;
    `;
    errorDiv.innerHTML = `🎥 Camera/Microphone Error<br><small>${error.message}</small>`;
    document.body.appendChild(errorDiv);
}

function showBrowserError() {
    const errorDiv = document.createElement('div');
    errorDiv.style.cssText = `
        position: fixed; top: 20px; left: 50%; transform: translateX(-50%);
        background: #ff9800; color: white; padding: 15px 25px;
        border-radius: 8px; z-index: 10000; font-weight: bold; text-align: center;
    `;
    errorDiv.innerHTML = `🌐 Browser Not Supported<br><small>Please use Chrome or Edge</small>`;
    document.body.appendChild(errorDiv);
}

function showMicrophoneAccessError() {
    const errorDiv = document.createElement('div');
    errorDiv.style.cssText = `
        position: fixed; top: 20px; left: 50%; transform: translateX(-50%);
        background: #f44336; color: white; padding: 15px 25px;
        border-radius: 8px; z-index: 10000; font-weight: bold; text-align: center;
    `;
    errorDiv.innerHTML = `🎙️ Microphone Access Required<br><small>Please allow microphone access</small>`;
    document.body.appendChild(errorDiv);
}

function showPermissionError() {
    const errorDiv = document.createElement('div');
    errorDiv.style.cssText = `
        position: fixed; top: 20px; left: 50%; transform: translateX(-50%);
        background: #f44336; color: white; padding: 15px 25px;
        border-radius: 8px; z-index: 10000; font-weight: bold; text-align: center;
    `;
    errorDiv.innerHTML = `🚫 Permission Denied<br><small>Microphone access is required for interviews</small>`;
    document.body.appendChild(errorDiv);
}

function showWarningMessage(message) {
    const warningDiv = document.createElement('div');
    warningDiv.id = 'micWarning';
    warningDiv.className = 'mic-warning';
    warningDiv.innerHTML = `🚨 ${message}`;
    document.body.appendChild(warningDiv);
}

function hideWarningMessage() {
    const warning = document.getElementById('micWarning');
    if (warning) {
        warning.remove();
    }
}

function showProfessionalNotice() {
    const notice = document.createElement('div');
    notice.className = 'professional-notice';
    notice.innerHTML = '🎤 Professional Interview Mode: Microphone is ALWAYS ON';
    document.body.appendChild(notice);
    
    setTimeout(() => {
        notice.style.animation = 'slideUp 0.5s ease-out forwards';
        setTimeout(() => notice.remove(), 500);
    }, 5000);
}

/**
 * MAIN INITIALIZATION
 */
document.addEventListener('DOMContentLoaded', async function() {
    console.log('🚀 Starting integrated interview system...');
    
    // Step 1: Initialize camera and microphone
    const mediaInitialized = await initCamera();
    if (!mediaInitialized) {
        console.error('❌ Media initialization failed');
        return;
    }
    
    // Step 2: Initialize speech recognition
    const speechInitialized = initSpeech();
    if (!speechInitialized) {
        console.error('❌ Speech recognition initialization failed');
    }
    
    // Step 3: Start timer
    setInterval(updateTimer, 1000);
    
    // Step 4: Show professional notice
    showProfessionalNotice();
    
    // Step 5: Handle initial question
    const initialQuestion = document.querySelector('script').textContent.match(/initialQuestion = '([^']*)'/);
    const initialAudio = document.querySelector('script').textContent.match(/initialAudio = '([^']*)'/);
    const initialDuration = document.querySelector('script').textContent.match(/initialDuration = ([^;]*)/);
    
    if (initialQuestion && initialQuestion[1]) {
        // Set initial state
        isProcessingResponse = true;
        speechRecognitionBlocked = true;
        
        setTimeout(() => {
            showCurrentQuestion(
                initialQuestion[1] || "Hello! Welcome to your AI interview. Can you tell me about yourself?",
                initialAudio ? initialAudio[1] : null,
                initialDuration ? parseFloat(initialDuration[1]) : null
            );
        }, 1000);
    }
    
    console.log('✅ Integrated interview system ready');
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (userStream) {
        userStream.getTracks().forEach(track => track.stop());
    }
    if (audioContext && audioContext.state !== 'closed') {
        audioContext.close();
    }
});

// Export functions for external use
window.toggleMic = toggleMic;
window.toggleCamera = toggleCamera;
window.endInterview = endInterview;
window.handleSpeechResult = handleSpeechResult;