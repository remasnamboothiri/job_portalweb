// Google Meet-style Interview Interface
class InterviewMeet {
  constructor() {
    this.currentQuestion = 1;
    this.totalQuestions = 8;
    this.timeRemaining = 15 * 60; // 15 minutes
    this.isRecording = false;
    this.isMuted = false;
    this.isCameraOff = false;
    this.mediaRecorder = null;
    this.userStream = null;
    this.recordedChunks = [];
    this.subtitleQueue = [];
    this.isShowingSubtitle = false;
    
    // this.questions = [
    //   "Hello! Welcome to your interview. Can you hear me clearly? Please introduce yourself and tell me what excites you most about this role.",
    //   "Tell me about a challenging project you've worked on recently and how you overcame the obstacles.",
    //   "How do you stay updated with the latest technologies in your field?",
    //   "Describe your experience with the main technologies required for this position.",
    //   "How do you approach debugging complex issues in your code?",
    //   "Tell me about a time when you had to work with a difficult team member. How did you handle it?",
    //   "What's your experience with responsive design and mobile-first development?",
    //   "Where do you see yourself in your career in the next 5 years?"
    // ];
    
    this.init();
  }

  async init() {
    this.setupEventListeners();
    this.startTimer();
    this.updateProgress();
    await this.initializeCamera();
    this.startInterview();
  }

  setupEventListeners() {
    // Control buttons
    document.getElementById('muteBtn')?.addEventListener('click', () => this.toggleMute());
    document.getElementById('cameraBtn')?.addEventListener('click', () => this.toggleCamera());
    document.getElementById('endBtn')?.addEventListener('click', () => this.endInterview());
    document.getElementById('settingsBtn')?.addEventListener('click', () => this.toggleSettings());
    
    // Response handling
    document.getElementById('submitResponse')?.addEventListener('click', () => this.submitResponse());
    document.getElementById('skipQuestion')?.addEventListener('click', () => this.skipQuestion());
    
    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
      if (e.ctrlKey || e.metaKey) {
        switch(e.key) {
          case 'm':
            e.preventDefault();
            this.toggleMute();
            break;
          case 'e':
            e.preventDefault();
            this.toggleCamera();
            break;
        }
      }
      
      if (e.key === 'Escape') {
        this.toggleSettings(false);
      }
    });
  }

  async initializeCamera() {
    try {
      this.userStream = await navigator.mediaDevices.getUserMedia({ 
        video: true, 
        audio: true 
      });
      
      const userVideo = document.getElementById('userVideo');
      if (userVideo) {
        userVideo.srcObject = this.userStream;
      }
      
      this.updateRecordingIndicator(true);
    } catch (error) {
      console.error('Error accessing camera/microphone:', error);
      this.showAlert('Unable to access camera or microphone. Please check your permissions.', 'error');
    }
  }

  startTimer() {
    this.timerInterval = setInterval(() => {
      this.timeRemaining--;
      this.updateTimerDisplay();
      
      if (this.timeRemaining <= 0) {
        this.endInterview();
      }
    }, 1000);
  }

  updateTimerDisplay() {
    const minutes = Math.floor(this.timeRemaining / 60);
    const seconds = this.timeRemaining % 60;
    const timerElement = document.getElementById('timer');
    
    if (timerElement) {
      timerElement.textContent = 
        `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
      
      // Warning when time is running low
      if (this.timeRemaining <= 300) { // 5 minutes
        timerElement.style.color = 'var(--google-red)';
      }
    }
  }

  updateProgress() {
    const progress = (this.currentQuestion / this.totalQuestions) * 100;
    const progressBar = document.getElementById('progressBar');
    const questionCounter = document.getElementById('questionCounter');
    
    if (progressBar) {
      progressBar.style.width = `${progress}%`;
    }
    
    if (questionCounter) {
      questionCounter.textContent = `${this.currentQuestion}/${this.totalQuestions}`;
    }
  }

  startInterview() {
    this.showSubtitle("AI: " + this.questions[0], 'ai');
    this.animateAISpeaking();
  }

  showSubtitle(text, speaker = 'ai', duration = 5000) {
    const subtitleOverlay = document.getElementById('subtitleOverlay');
    const subtitleText = document.getElementById('subtitleText');
    
    if (!subtitleOverlay || !subtitleText) return;
    
    // Clear any existing subtitle
    this.hideSubtitle();
    
    // Set the text and show
    subtitleText.textContent = text;
    subtitleOverlay.classList.add('show');
    
    // Add typing effect for AI responses
    if (speaker === 'ai') {
      subtitleText.classList.add('subtitle-typing');
    }
    
    // Auto-hide after duration
    this.subtitleTimeout = setTimeout(() => {
      this.hideSubtitle();
    }, duration);
  }

  hideSubtitle() {
    const subtitleOverlay = document.getElementById('subtitleOverlay');
    const subtitleText = document.getElementById('subtitleText');
    
    if (subtitleOverlay) {
      subtitleOverlay.classList.remove('show');
    }
    
    if (subtitleText) {
      subtitleText.classList.remove('subtitle-typing');
    }
    
    if (this.subtitleTimeout) {
      clearTimeout(this.subtitleTimeout);
    }
  }

  animateAISpeaking() {
    const aiAvatar = document.getElementById('aiAvatar');
    const speakingIndicator = document.getElementById('speakingIndicator');
    
    if (aiAvatar) {
      aiAvatar.classList.add('speaking');
      setTimeout(() => {
        aiAvatar.classList.remove('speaking');
      }, 3000);
    }
    
    if (speakingIndicator) {
      speakingIndicator.style.display = 'block';
      setTimeout(() => {
        speakingIndicator.style.display = 'none';
      }, 3000);
    }
  }

  toggleMute() {
    this.isMuted = !this.isMuted;
    const muteBtn = document.getElementById('muteBtn');
    
    if (this.userStream) {
      const audioTracks = this.userStream.getAudioTracks();
      audioTracks.forEach(track => {
        track.enabled = !this.isMuted;
      });
    }
    
    if (muteBtn) {
      muteBtn.innerHTML = this.isMuted ? '🔇' : '🎤';
      muteBtn.classList.toggle('muted', this.isMuted);
    }
    
    this.showSubtitle(this.isMuted ? 'Microphone muted' : 'Microphone unmuted', 'system', 2000);
  }

  toggleCamera() {
    this.isCameraOff = !this.isCameraOff;
    const cameraBtn = document.getElementById('cameraBtn');
    const userVideo = document.getElementById('userVideo');
    
    if (this.userStream) {
      const videoTracks = this.userStream.getVideoTracks();
      videoTracks.forEach(track => {
        track.enabled = !this.isCameraOff;
      });
    }
    
    if (cameraBtn) {
      cameraBtn.innerHTML = this.isCameraOff ? '📹❌' : '📹';
      cameraBtn.classList.toggle('camera-off', this.isCameraOff);
    }
    
    if (userVideo) {
      userVideo.style.display = this.isCameraOff ? 'none' : 'block';
    }
    
    this.showSubtitle(this.isCameraOff ? 'Camera turned off' : 'Camera turned on', 'system', 2000);
  }

  async submitResponse() {
    const responseText = document.getElementById('responseText')?.value.trim();
    
    if (!responseText) {
      this.showAlert('Please provide a response before submitting.', 'warning');
      return;
    }
    
    // Show user's response as subtitle
    this.showSubtitle(`You: ${responseText}`, 'user', 3000);
    
    // Show loading state
    this.showProcessingState();
    
    // Simulate AI processing
    setTimeout(() => {
      this.nextQuestion();
    }, 2000);
  }

  showProcessingState() {
    const submitBtn = document.getElementById('submitResponse');
    if (submitBtn) {
      const originalText = submitBtn.innerHTML;
      submitBtn.innerHTML = '<div class="spinner-google"></div> Processing...';
      submitBtn.disabled = true;
      
      setTimeout(() => {
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
      }, 2000);
    }
  }

  nextQuestion() {
    if (this.currentQuestion >= this.totalQuestions) {
      this.completeInterview();
      return;
    }
    
    this.currentQuestion++;
    this.updateProgress();
    
    // Clear previous response
    const responseText = document.getElementById('responseText');
    if (responseText) {
      responseText.value = '';
    }
    
    // Show next AI question
    const nextQuestion = this.questions[this.currentQuestion - 1];
    setTimeout(() => {
      this.showSubtitle(`AI: ${nextQuestion}`, 'ai');
      this.animateAISpeaking();
    }, 1000);
  }

  skipQuestion() {
    if (confirm('Are you sure you want to skip this question?')) {
      this.showSubtitle('Question skipped', 'system', 2000);
      setTimeout(() => {
        this.nextQuestion();
      }, 1000);
    }
  }

  toggleSettings(show = null) {
    const settingsPanel = document.getElementById('settingsPanel');
    if (!settingsPanel) return;
    
    if (show === null) {
      settingsPanel.classList.toggle('show');
    } else {
      settingsPanel.classList.toggle('show', show);
    }
  }

  updateRecordingIndicator(isRecording) {
    const recordingIndicator = document.getElementById('recordingIndicator');
    if (recordingIndicator) {
      recordingIndicator.style.display = isRecording ? 'flex' : 'none';
    }
  }

  showAlert(message, type = 'info') {
    // Create alert element
    const alert = document.createElement('div');
    alert.className = `alert-google alert-google-${type}`;
    alert.textContent = message;
    alert.style.cssText = `
      position: fixed;
      top: 80px;
      left: 50%;
      transform: translateX(-50%);
      z-index: 1000;
      min-width: 300px;
      text-align: center;
    `;
    
    document.body.appendChild(alert);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
      alert.remove();
    }, 3000);
  }

  completeInterview() {
    clearInterval(this.timerInterval);
    
    // Stop all media streams
    if (this.userStream) {
      this.userStream.getTracks().forEach(track => track.stop());
    }
    
    // Show completion message
    this.showSubtitle('Interview completed! Thank you for your time.', 'ai', 5000);
    
    // Redirect to completion page after delay
    setTimeout(() => {
      this.showCompletionModal();
    }, 3000);
  }

  showCompletionModal() {
    const modal = document.getElementById('completionModal');
    if (modal) {
      modal.style.display = 'block';
    } else {
      // Create completion modal if it doesn't exist
      const modalHTML = `
        <div id="completionModal" class="modal-google" style="display: block;">
          <div class="modal-google-content">
            <div class="modal-google-header">
              <h3>Interview Complete!</h3>
            </div>
            <div class="modal-google-body">
              <p>Thank you for taking the time to interview with us. We'll review your responses and get back to you within 2-3 business days.</p>
            </div>
            <div class="modal-google-footer">
              <button class="btn-google" onclick="window.location.href='jobseeker-dashboard.html'">
                Back to Dashboard
              </button>
            </div>
          </div>
        </div>
      `;
      document.body.insertAdjacentHTML('beforeend', modalHTML);
    }
  }

  endInterview() {
    if (confirm('Are you sure you want to end the interview? Your progress will be saved.')) {
      this.completeInterview();
    }
  }

  // Voice recognition for subtitles (if supported)
  startVoiceRecognition() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      this.recognition = new SpeechRecognition();
      
      this.recognition.continuous = true;
      this.recognition.interimResults = true;
      
      this.recognition.onresult = (event) => {
        let finalTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript;
          }
        }
        
        if (finalTranscript) {
          this.showSubtitle(`You: ${finalTranscript}`, 'user', 3000);
        }
      };
      
      this.recognition.start();
    }
  }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  // Only initialize if we're on the interview page
  if (document.getElementById('interviewContainer')) {
    new InterviewMeet();
  }
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = InterviewMeet;
}