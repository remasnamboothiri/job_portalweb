// Minimal Interview Camera and Recording Fix
console.log('🔧 Loading minimal interview fix...');

// Global variables
window.mediaRecorder = null;
window.recordedChunks = [];
window.isRecording = false;
window.isCameraOn = true;
window.userStream = null;

// Override initializeCamera function
window.initializeCamera = async function() {
    try {
        console.log('📹 Initializing camera with recording...');
        
        const constraints = {
            video: { width: { ideal: 1280 }, height: { ideal: 720 } },
            audio: true
        };
        
        window.userStream = await navigator.mediaDevices.getUserMedia(constraints);
        
        const userVideo = document.getElementById('userVideo');
        if (userVideo) {
            userVideo.srcObject = window.userStream;
            console.log('✅ Camera initialized');
        }
        
        // Setup recording
        setupRecording();
        
        // Setup camera button
        setupCameraButton();
        
    } catch (error) {
        console.error('❌ Camera initialization failed:', error);
    }
};

// Setup recording
function setupRecording() {
    if (!window.userStream) return;
    
    try {
        window.mediaRecorder = new MediaRecorder(window.userStream, {
            mimeType: 'video/webm'
        });
        
        window.mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                window.recordedChunks.push(event.data);
            }
        };
        
        window.mediaRecorder.onstop = () => {
            saveRecording();
        };
        
        // Auto-start recording
        setTimeout(() => {
            startRecording();
        }, 2000);
        
        console.log('✅ Recording setup complete');
        
    } catch (error) {
        console.error('❌ Recording setup failed:', error);
    }
}

// Start recording
function startRecording() {
    if (window.mediaRecorder && !window.isRecording) {
        window.recordedChunks = [];
        window.mediaRecorder.start(1000);
        window.isRecording = true;
        
        const indicator = document.getElementById('recordingIndicator');
        if (indicator) {
            indicator.style.display = 'flex';
        }
        
        console.log('🎥 Recording started');
    }
}

// Stop recording
function stopRecording() {
    if (window.mediaRecorder && window.isRecording) {
        window.mediaRecorder.stop();
        window.isRecording = false;
        
        const indicator = document.getElementById('recordingIndicator');
        if (indicator) {
            indicator.style.display = 'none';
        }
        
        console.log('🎥 Recording stopped');
    }
}

// Save recording
async function saveRecording() {
    if (window.recordedChunks.length === 0) return;
    
    try {
        const blob = new Blob(window.recordedChunks, { type: 'video/webm' });
        const formData = new FormData();
        
        const pathParts = window.location.pathname.split('/');
        const uuid = pathParts[pathParts.length - 2];
        
        formData.append('recording', blob, `interview-${uuid}.webm`);
        formData.append('interview_uuid', uuid);
        formData.append('duration', '300');
        
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        const response = await fetch('/save-interview-recording/', {
            method: 'POST',
            headers: { 'X-CSRFToken': csrfToken },
            body: formData
        });
        
        if (response.ok) {
            console.log('✅ Recording saved');
        } else {
            console.error('❌ Failed to save recording');
        }
        
    } catch (error) {
        console.error('❌ Error saving recording:', error);
    }
}

// Setup camera button
function setupCameraButton() {
    const cameraBtn = document.getElementById('cameraBtn');
    if (!cameraBtn) return;
    
    cameraBtn.onclick = function() {
        toggleCamera();
    };
    
    updateCameraButton();
}

// Toggle camera
function toggleCamera() {
    if (!window.userStream) return;
    
    const videoTracks = window.userStream.getVideoTracks();
    window.isCameraOn = !window.isCameraOn;
    
    videoTracks.forEach(track => {
        track.enabled = window.isCameraOn;
    });
    
    updateCameraButton();
    console.log(`📹 Camera ${window.isCameraOn ? 'ON' : 'OFF'}`);
}

// Update camera button
function updateCameraButton() {
    const cameraBtn = document.getElementById('cameraBtn');
    if (!cameraBtn) return;
    
    if (window.isCameraOn) {
        cameraBtn.style.background = '#5f6368';
        cameraBtn.title = 'Turn off camera';
    } else {
        cameraBtn.style.background = '#ea4335';
        cameraBtn.title = 'Turn on camera';
    }
}

// Override end interview to stop recording
const originalShowCompletionModal = window.showCompletionModal;
window.showCompletionModal = function() {
    console.log('🏁 Interview ending - stopping recording...');
    stopRecording();
    
    setTimeout(() => {
        if (originalShowCompletionModal) {
            originalShowCompletionModal();
        } else {
            document.getElementById('completionModal')?.classList.add('show');
        }
    }, 1000);
};

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(window.initializeCamera, 500);
    });
} else {
    setTimeout(window.initializeCamera, 500);
}

console.log('✅ Minimal interview fix loaded');