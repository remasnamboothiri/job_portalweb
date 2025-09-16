class WebRTCAudioManager {
    constructor() {
        this.audioContext = null;
        this.mediaStream = null;
        this.mediaRecorder = null;
        this.isRecording = false;
        this.audioChunks = [];
        this.echoCancellation = true;
        this.noiseSuppression = true;
        this.autoGainControl = true;
    }

    async initialize() {
        try {
            // Get user media with echo cancellation enabled
            this.mediaStream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: this.echoCancellation,
                    noiseSuppression: this.noiseSuppression,
                    autoGainControl: this.autoGainControl,
                    sampleRate: 44100,
                    channelCount: 1
                }
            });

            // Create audio context for processing
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            
            // Setup media recorder
            this.mediaRecorder = new MediaRecorder(this.mediaStream, {
                mimeType: 'audio/webm;codecs=opus'
            });

            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };

            console.log('WebRTC Audio Manager initialized with AEC');
            return true;
        } catch (error) {
            console.error('Failed to initialize WebRTC Audio:', error);
            return false;
        }
    }

    startRecording() {
        if (!this.mediaRecorder || this.isRecording) return false;
        
        this.audioChunks = [];
        this.mediaRecorder.start(100); // Collect data every 100ms
        this.isRecording = true;
        console.log('Recording started with echo cancellation');
        return true;
    }

    stopRecording() {
        return new Promise((resolve) => {
            if (!this.mediaRecorder || !this.isRecording) {
                resolve(null);
                return;
            }

            this.mediaRecorder.onstop = () => {
                const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
                this.isRecording = false;
                console.log('Recording stopped');
                resolve(audioBlob);
            };

            this.mediaRecorder.stop();
        });
    }

    async playAudio(audioUrl) {
        try {
            const audio = new Audio(audioUrl);
            audio.volume = 0.8; // Reduce volume to minimize feedback
            
            // Use Web Audio API for better control
            if (this.audioContext) {
                const source = this.audioContext.createMediaElementSource(audio);
                const gainNode = this.audioContext.createGain();
                
                gainNode.gain.value = 0.8;
                source.connect(gainNode);
                gainNode.connect(this.audioContext.destination);
            }
            
            await audio.play();
            return true;
        } catch (error) {
            console.error('Audio playback failed:', error);
            return false;
        }
    }

    cleanup() {
        if (this.mediaStream) {
            this.mediaStream.getTracks().forEach(track => track.stop());
        }
        if (this.audioContext) {
            this.audioContext.close();
        }
        this.isRecording = false;
    }

    // Get audio constraints info
    getAudioConstraints() {
        return {
            echoCancellation: this.echoCancellation,
            noiseSuppression: this.noiseSuppression,
            autoGainControl: this.autoGainControl
        };
    }
}

// Global instance
window.webrtcAudio = new WebRTCAudioManager();