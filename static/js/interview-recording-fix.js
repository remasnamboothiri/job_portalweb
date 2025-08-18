// Simple Camera and Recording Fix
let mediaRecorder = null;
let recordedChunks = [];
let isRecording = false;
let isCameraOn = true;
let userStream = null;

    // Recording state management
    class InterviewRecorder {
        constructor() {
            this.mediaRecorder = null;
            this.recordedChunks = [];
            this.isRecording = false;
            this.recordingStartTime = null;
            this.recordingBlob = null;
        }

        async startRecording(stream) {
            try {
                console.log('🎥 Starting interview recording...');
                
                // Create MediaRecorder with the stream
                const options = {
                    mimeType: 'video/webm;codecs=vp9,opus'
                };
                
                // Fallback MIME types if VP9 not supported
                if (!MediaRecorder.isTypeSupported(options.mimeType)) {
                    options.mimeType = 'video/webm;codecs=vp8,opus';
                    if (!MediaRecorder.isTypeSupported(options.mimeType)) {
                        options.mimeType = 'video/webm';
                        if (!MediaRecorder.isTypeSupported(options.mimeType)) {
                            options.mimeType = 'video/mp4';
                        }
                    }
                }

                console.log('🎥 Using MIME type:', options.mimeType);

                this.mediaRecorder = new MediaRecorder(stream, options);
                this.recordedChunks = [];
                
                this.mediaRecorder.ondataavailable = (event) => {
                    if (event.data && event.data.size > 0) {
                        this.recordedChunks.push(event.data);
                        console.log('🎥 Recording chunk added:', event.data.size, 'bytes');
                    }
                };

                this.mediaRecorder.onstop = () => {
                    console.log('🎥 Recording stopped, processing data...');
                    this.processRecording();
                };

                this.mediaRecorder.onerror = (event) => {
                    console.error('🎥 Recording error:', event.error);
                };

                // Start recording
                this.mediaRecorder.start(1000); // Collect data every second
                this.isRecording = true;
                this.recordingStartTime = new Date();
                
                console.log('✅ Recording started successfully');
                this.updateRecordingUI(true);
                
                return true;
            } catch (error) {
                console.error('❌ Failed to start recording:', error);
                return false;
            }
        }

        stopRecording() {
            if (this.mediaRecorder && this.isRecording) {
                console.log('🎥 Stopping recording...');
                this.mediaRecorder.stop();
                this.isRecording = false;
                this.updateRecordingUI(false);
            }
        }

        processRecording() {
            if (this.recordedChunks.length === 0) {
                console.warn('⚠️ No recording data available');
                return;
            }

            console.log('🎥 Processing recording with', this.recordedChunks.length, 'chunks');
            
            // Create blob from recorded chunks
            const mimeType = this.mediaRecorder.mimeType || 'video/webm';
            this.recordingBlob = new Blob(this.recordedChunks, { type: mimeType });
            
            console.log('✅ Recording processed:', {
                size: this.recordingBlob.size,
                type: this.recordingBlob.type,
                duration: this.recordingStartTime ? (new Date() - this.recordingStartTime) / 1000 : 'unknown'
            });

            // Save recording
            this.saveRecording();
        }

        async saveRecording() {
            if (!this.recordingBlob) {
                console.error('❌ No recording blob to save');
                return;
            }

            try {
                console.log('💾 Saving interview recording...');
                
                // Create form data
                const formData = new FormData();
                const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
                const filename = `interview-recording-${timestamp}.webm`;
                
                formData.append('recording', this.recordingBlob, filename);
                formData.append('interview_uuid', this.getInterviewUUID());
                formData.append('duration', this.recordingStartTime ? (new Date() - this.recordingStartTime) / 1000 : 0);

                // Get CSRF token
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                                 document.querySelector('meta[name=csrf-token]')?.getAttribute('content') || '';

                // Send to server
                const response = await fetch('/save-interview-recording/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: formData
                });

                if (response.ok) {
                    const result = await response.json();
                    console.log('✅ Recording saved successfully:', result);
                    this.showRecordingSavedMessage();
                } else {
                    console.error('❌ Failed to save recording:', response.status, response.statusText);
                    this.showRecordingErrorMessage();
                }
            } catch (error) {
                console.error('❌ Error saving recording:', error);
                this.showRecordingErrorMessage();
            }
        }

        getInterviewUUID() {
            // Extract UUID from URL
            const pathParts = window.location.pathname.split('/');
            return pathParts[pathParts.length - 2] || 'unknown';
        }

        updateRecordingUI(recording) {
            const recordingIndicator = document.getElementById('recordingIndicator');
            if (recordingIndicator) {
                if (recording) {
                    recordingIndicator.classList.add('active');
                    recordingIndicator.innerHTML = '<i class="fas fa-circle"></i> Recording';
                } else {
                    recordingIndicator.classList.remove('active');
                    recordingIndicator.innerHTML = '<i class="fas fa-circle"></i> Stopped';
                }
            }
        }

        showRecordingSavedMessage() {
            // Show success message
            const message = document.createElement('div');
            message.className = 'recording-message success';
            message.innerHTML = '✅ Interview recording saved successfully!';
            message.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: #4CAF50;
                color: white;
                padding: 12px 20px;
                border-radius: 8px;
                z-index: 10000;
                font-weight: 500;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            `;
            document.body.appendChild(message);
            
            setTimeout(() => {
                message.remove();
            }, 5000);
        }

        showRecordingErrorMessage() {
            // Show error message
            const message = document.createElement('div');
            message.className = 'recording-message error';
            message.innerHTML = '❌ Failed to save recording. Please try again.';
            message.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: #f44336;
                color: white;
                padding: 12px 20px;
                border-radius: 8px;
                z-index: 10000;
                font-weight: 500;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            `;
            document.body.appendChild(message);
            
            setTimeout(() => {
                message.remove();
            }, 5000);
        }
    }

    // Initialize recorder
    const recorder = new InterviewRecorder();

    // Enhanced camera management
    class CameraManager {
        constructor() {
            this.stream = null;
            this.isCameraOn = true;
            this.videoElement = null;
        }

        async initializeCamera() {
            try {
                console.log('📹 Initializing camera...');
                
                const constraints = {
                    video: {
                        width: { ideal: 1280, max: 1920 },
                        height: { ideal: 720, max: 1080 },
                        frameRate: { ideal: 30, max: 60 }
                    },
                    audio: {
                        echoCancellation: true,
                        noiseSuppression: true,
                        autoGainControl: true,
                        sampleRate: { ideal: 48000 }
                    }
                };

                this.stream = await navigator.mediaDevices.getUserMedia(constraints);
                this.videoElement = document.getElementById('userVideo');
                
                if (this.videoElement) {
                    this.videoElement.srcObject = this.stream;
                    this.videoElement.muted = true; // Prevent echo
                    console.log('✅ Camera initialized successfully');
                    
                    // Start recording automatically when camera is initialized
                    setTimeout(() => {
                        this.startRecording();
                    }, 2000);
                } else {
                    console.error('❌ Video element not found');
                }

                // Store stream globally for other functions
                window.stream = this.stream;
                
                return this.stream;
            } catch (error) {
                console.error('❌ Camera initialization failed:', error);
                this.showCameraError(error);
                throw error;
            }
        }

        toggleCamera() {
            if (!this.stream) {
                console.warn('⚠️ No camera stream available');
                return;
            }

            const videoTracks = this.stream.getVideoTracks();
            if (videoTracks.length === 0) {
                console.warn('⚠️ No video tracks available');
                return;
            }

            this.isCameraOn = !this.isCameraOn;
            
            videoTracks.forEach(track => {
                track.enabled = this.isCameraOn;
            });

            console.log(`📹 Camera ${this.isCameraOn ? 'enabled' : 'disabled'}`);
            this.updateCameraButton();
        }

        updateCameraButton() {
            const cameraBtn = document.getElementById('cameraBtn');
            if (cameraBtn) {
                if (this.isCameraOn) {
                    cameraBtn.innerHTML = '📹';
                    cameraBtn.title = 'Turn off camera';
                    cameraBtn.style.background = '#5f6368';
                } else {
                    cameraBtn.innerHTML = '📹';
                    cameraBtn.title = 'Turn on camera';
                    cameraBtn.style.background = '#ea4335';
                }
            }
        }

        startRecording() {
            if (this.stream && !recorder.isRecording) {
                console.log('🎥 Starting interview recording...');
                recorder.startRecording(this.stream);
            }
        }

        stopRecording() {
            if (recorder.isRecording) {
                console.log('🎥 Stopping interview recording...');
                recorder.stopRecording();
            }
        }

        showCameraError(error) {
            let errorMessage = 'Camera access failed. ';
            
            if (error.name === 'NotAllowedError') {
                errorMessage += 'Please allow camera and microphone access.';
            } else if (error.name === 'NotFoundError') {
                errorMessage += 'No camera or microphone found.';
            } else if (error.name === 'NotReadableError') {
                errorMessage += 'Camera is being used by another application.';
            } else {
                errorMessage += 'Please check your camera settings.';
            }

            // Show error message
            const errorDiv = document.createElement('div');
            errorDiv.className = 'camera-error';
            errorDiv.innerHTML = `❌ ${errorMessage}`;
            errorDiv.style.cssText = `
                position: fixed;
                top: 20px;
                left: 50%;
                transform: translateX(-50%);
                background: #f44336;
                color: white;
                padding: 12px 20px;
                border-radius: 8px;
                z-index: 10000;
                font-weight: 500;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            `;
            document.body.appendChild(errorDiv);
            
            setTimeout(() => {
                errorDiv.remove();
            }, 8000);
        }

        cleanup() {
            if (this.stream) {
                this.stream.getTracks().forEach(track => {
                    track.stop();
                });
                this.stream = null;
            }
        }
    }

    // Initialize camera manager
    const cameraManager = new CameraManager();

    // Override the existing initializeCamera function
    window.initializeCamera = async function() {
        return await cameraManager.initializeCamera();
    };

    // Enhanced button event handlers
    function setupButtonHandlers() {
        // Camera button handler
        const cameraBtn = document.getElementById('cameraBtn');
        if (cameraBtn) {
            cameraBtn.addEventListener('click', () => {
                console.log('📹 Camera button clicked');
                cameraManager.toggleCamera();
            });
        }

        // End button handler - stop recording before ending
        const endBtn = document.getElementById('endBtn');
        if (endBtn) {
            const originalEndHandler = endBtn.onclick;
            endBtn.onclick = function(e) {
                console.log('📞 End button clicked - stopping recording');
                
                // Stop recording first
                cameraManager.stopRecording();
                
                // Wait a moment for recording to process, then end interview
                setTimeout(() => {
                    if (originalEndHandler) {
                        originalEndHandler.call(this, e);
                    } else if (confirm('Are you sure you want to end the interview?')) {
                        if (window.showCompletionModal) {
                            window.showCompletionModal();
                        }
                    }
                }, 1000);
            };
        }

        // Microphone button - ensure it works properly
        const micBtn = document.getElementById('muteBtn');
        if (micBtn) {
            micBtn.addEventListener('click', () => {
                console.log('🎤 Microphone button clicked');
                if (window.toggleMicrophone) {
                    window.toggleMicrophone();
                }
            });
        }
    }

    // Enhanced completion modal to ensure recording is saved
    const originalShowCompletionModal = window.showCompletionModal;
    window.showCompletionModal = function() {
        console.log('🏁 Interview ending - ensuring recording is saved...');
        
        // Stop recording if still active
        if (recorder.isRecording) {
            recorder.stopRecording();
            
            // Wait for recording to be processed and saved
            setTimeout(() => {
                if (originalShowCompletionModal) {
                    originalShowCompletionModal();
                } else {
                    document.getElementById('completionModal')?.classList.add('show');
                }
            }, 2000);
        } else {
            // Recording already stopped, show modal immediately
            if (originalShowCompletionModal) {
                originalShowCompletionModal();
            } else {
                document.getElementById('completionModal')?.classList.add('show');
            }
        }
    };

    // Initialize everything when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        console.log('🚀 Interview recording system initializing...');
        
        // Setup button handlers
        setupButtonHandlers();
        
        // Initialize camera with recording
        setTimeout(async () => {
            try {
                await cameraManager.initializeCamera();
                console.log('✅ Interview recording system ready');
            } catch (error) {
                console.error('❌ Failed to initialize camera:', error);
            }
        }, 1000);
    });

    // Cleanup on page unload
    window.addEventListener('beforeunload', () => {
        console.log('🧹 Cleaning up interview recording system...');
        
        // Stop recording
        if (recorder.isRecording) {
            recorder.stopRecording();
        }
        
        // Cleanup camera
        cameraManager.cleanup();
    });

    // Handle page visibility changes
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            console.log('📱 Page hidden - pausing recording');
            // Could pause recording here if needed
        } else {
            console.log('📱 Page visible - resuming recording');
            // Could resume recording here if needed
        }
    });

    // Expose functions globally for debugging
    window.interviewRecording = {
        recorder: recorder,
        cameraManager: cameraManager,
        startRecording: () => cameraManager.startRecording(),
        stopRecording: () => cameraManager.stopRecording(),
        toggleCamera: () => cameraManager.toggleCamera(),
        getRecordingStatus: () => ({
            isRecording: recorder.isRecording,
            isCameraOn: cameraManager.isCameraOn,
            hasStream: !!cameraManager.stream,
            recordedChunks: recorder.recordedChunks.length
        })
    };

    console.log('✅ Interview recording and camera fix loaded');
    console.log('🔧 Debug functions available at window.interviewRecording');

})();