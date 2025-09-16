// Simple Interview Camera and Recording Fix
let mediaRecorder = null;
let recordedChunks = [];
let isRecording = false;
let isCameraOn = true;
let userStream = null;

// Initialize camera and setup recording
async function initializeCameraAndRecording() {
    try {
        console.log('🎥 Starting camera and recording setup...');
        
        // Get user media
        userStream = await navigator.mediaDevices.getUserMedia({
            video: true,
            audio: true
        });
        
        // Set video element
        const userVideo = document.getElementById('userVideo');
        if (userVideo) {
            userVideo.srcObject = userStream;
            userVideo.muted = true;
        }
        
        // Setup recording
        setupRecording();
        
        // Setup camera button
        setupCameraButton();
        
        console.log('✅ Camera and recording ready');
        
    } catch (error) {
        console.error('❌ Camera setup failed:', error);
    }
}

// Setup recording functionality
function setupRecording() {
    if (!userStream) return;
    
    try {
        mediaRecorder = new MediaRecorder(userStream, {
            mimeType: 'video/webm'
        });
        
        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                recordedChunks.push(event.data);
            }
        };
        
        mediaRecorder.onstop = () => {
            saveRecording();
        };
        
        // Start recording automatically
        startRecording();
        
    } catch (error) {
        console.error('❌ Recording setup failed:', error);
    }
}

// Start recording
function startRecording() {
    if (mediaRecorder && !isRecording) {
        recordedChunks = [];
        mediaRecorder.start(1000);
        isRecording = true;
        
        // Show recording indicator
        const indicator = document.getElementById('recordingIndicator');
        if (indicator) {
            indicator.style.display = 'flex';
        }
        
        console.log('🎥 Recording started');
    }
}

// Stop recording
function stopRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        isRecording = false;
        
        // Hide recording indicator
        const indicator = document.getElementById('recordingIndicator');
        if (indicator) {
            indicator.style.display = 'none';
        }
        
        console.log('🎥 Recording stopped');
    }
}

// Save recording to server
async function saveRecording() {
    if (recordedChunks.length === 0) return;
    
    try {
        const blob = new Blob(recordedChunks, { type: 'video/webm' });
        const formData = new FormData();
        
        // Get interview UUID from URL
        const pathParts = window.location.pathname.split('/');
        const uuid = pathParts[pathParts.length - 2];
        
        formData.append('recording', blob, `interview-${uuid}.webm`);
        formData.append('interview_uuid', uuid);
        formData.append('duration', '300'); // 5 minutes default
        
        // Get CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        const response = await fetch('/save-interview-recording/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            },
            body: formData
        });
        
        if (response.ok) {
            console.log('✅ Recording saved successfully');
            showMessage('Recording saved successfully!', 'success');
        } else {
            console.error('❌ Failed to save recording');
            showMessage('Failed to save recording', 'error');
        }
        
    } catch (error) {
        console.error('❌ Error saving recording:', error);
        showMessage('Error saving recording', 'error');
    }
}

// Setup camera button functionality
function setupCameraButton() {
    const cameraBtn = document.getElementById('cameraBtn');
    if (!cameraBtn) return;
    
    cameraBtn.addEventListener('click', toggleCamera);
    updateCameraButton();
}

// Toggle camera on/off
function toggleCamera() {
    if (!userStream) return;
    
    const videoTracks = userStream.getVideoTracks();
    if (videoTracks.length === 0) return;
    
    isCameraOn = !isCameraOn;
    
    videoTracks.forEach(track => {
        track.enabled = isCameraOn;
    });
    
    updateCameraButton();
    console.log(`📹 Camera ${isCameraOn ? 'ON' : 'OFF'}`);
}

// Update camera button appearance
function updateCameraButton() {
    const cameraBtn = document.getElementById('cameraBtn');
    if (!cameraBtn) return;
    
    if (isCameraOn) {
        cameraBtn.style.background = '#5f6368';
        cameraBtn.title = 'Turn off camera';
    } else {
        cameraBtn.style.background = '#ea4335';
        cameraBtn.title = 'Turn on camera';
    }
}

// Show message to user
function showMessage(text, type) {
    const message = document.createElement('div');
    message.textContent = text;
    message.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 20px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 10000;
        background: ${type === 'success' ? '#4CAF50' : '#f44336'};
    `;
    
    document.body.appendChild(message);
    
    setTimeout(() => {
        message.remove();
    }, 3000);
}

// Override existing initializeCamera function
window.initializeCamera = initializeCameraAndRecording;

// Setup when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Interview fix loading...');
    
    // Initialize after a short delay
    setTimeout(initializeCameraAndRecording, 1000);
    
    // Stop recording when interview ends
    const endBtn = document.getElementById('endBtn');
    if (endBtn) {
        const originalClick = endBtn.onclick;
        endBtn.onclick = function(e) {
            stopRecording();
            setTimeout(() => {
                if (originalClick) originalClick.call(this, e);
            }, 1000);
        };
    }
});

// Stop recording on page unload
window.addEventListener('beforeunload', () => {
    stopRecording();
});

console.log('✅ Interview simple fix loaded');