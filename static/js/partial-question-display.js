// Partial Question Display Manager
class PartialQuestionManager {
    constructor() {
        this.maxPreviewLength = 50;
        this.currentFullQuestion = '';
    }

    // Create partial question display HTML
    createPartialDisplay(fullQuestion, speaker = 'AI') {
        this.currentFullQuestion = fullQuestion;
        
        if (fullQuestion.length <= this.maxPreviewLength) {
            return `${speaker}: "${fullQuestion}"`;
        }

        const preview = fullQuestion.substring(0, this.maxPreviewLength).trim();
        
        return `
            <div class="question-container">
                <span class="question-preview" id="questionPreview">
                    ${speaker}: "${preview}..."
                </span>
                <span class="question-full" id="questionFull" style="display: none;">
                    ${speaker}: "${fullQuestion}"
                </span>
                <button class="show-full-btn" id="showFullBtn" onclick="window.questionManager.showFullQuestion()">
                    Show Full Question
                </button>
            </div>
        `;
    }

    // Show full question
    showFullQuestion() {
        const preview = document.getElementById('questionPreview');
        const full = document.getElementById('questionFull');
        const btn = document.getElementById('showFullBtn');
        
        if (preview && full && btn) {
            preview.style.display = 'none';
            full.style.display = 'inline';
            btn.style.display = 'none';
        }
    }

    // Update subtitle with partial display
    updateSubtitleWithPartial(response, speaker = 'AI') {
        const subtitleText = document.getElementById('subtitleText');
        if (subtitleText) {
            subtitleText.innerHTML = this.createPartialDisplay(response, speaker);
        }
    }

    // Reset to preview mode for new questions
    resetToPreview() {
        const preview = document.getElementById('questionPreview');
        const full = document.getElementById('questionFull');
        const btn = document.getElementById('showFullBtn');
        
        if (preview && full && btn) {
            preview.style.display = 'inline';
            full.style.display = 'none';
            if (this.currentFullQuestion.length > this.maxPreviewLength) {
                btn.style.display = 'inline-block';
            }
        }
    }
}

// Global question manager instance
window.questionManager = new PartialQuestionManager();

// Override handleAIResponse to use partial display
window.originalHandleAIResponse = window.handleAIResponse;
window.handleAIResponse = function(data) {
    // Hide voice response panel
    const voicePanel = document.getElementById('voiceResponsePanel');
    if (voicePanel) {
        voicePanel.style.display = 'none';
    }
    
    // Update question counter
    window.currentQuestionCount = data.question_count || window.currentQuestionCount + 1;
    const questionCounter = document.getElementById('questionCounter');
    if (questionCounter) {
        questionCounter.textContent = `${window.currentQuestionCount}/8`;
    }
    
    // Update progress bar
    const progress = (window.currentQuestionCount / 8) * 100;
    const progressBar = document.getElementById('progressBar');
    if (progressBar) {
        progressBar.style.width = `${progress}%`;
    }
    
    // Show AI response with partial display
    const response = data.response;
    window.questionManager.updateSubtitleWithPartial(response, 'AI');
    
    const subtitleOverlay = document.getElementById('subtitleOverlay');
    if (subtitleOverlay) {
        subtitleOverlay.classList.add('show');
    }
    
    // Play AI audio if available
    if (data.audio) {
        if (window.playAIAudio) {
            window.playAIAudio(data.audio);
        }
    } else {
        // Show next response panel with reduced delay
        setTimeout(() => {
            if (!data.is_final) {
                if (voicePanel) {
                    voicePanel.style.display = 'block';
                }
                const responseStatus = document.getElementById('responseStatus');
                if (responseStatus) {
                    responseStatus.innerHTML = 'Microphone is ready. You can speak now.';
                }
            } else {
                if (window.showCompletionModal) {
                    window.showCompletionModal();
                }
            }
        }, 1500);
    }
    
    // Hide subtitles after some time
    setTimeout(() => {
        if (subtitleOverlay) {
            subtitleOverlay.classList.remove('show');
        }
    }, 8000);
    
    // Check if interview is complete
    if (data.is_final || window.currentQuestionCount >= 8) {
        setTimeout(() => {
            if (window.showCompletionModal) {
                window.showCompletionModal();
            }
        }, 2000);
    }
};

// Add CSS for partial question display
const partialQuestionCSS = `
<style>
.question-container {
    display: inline-block;
    width: 100%;
}

.show-full-btn {
    background: rgba(26, 115, 232, 0.8);
    color: white;
    border: none;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
    cursor: pointer;
    margin-left: 8px;
    transition: all 0.3s ease;
}

.show-full-btn:hover {
    background: rgba(26, 115, 232, 1);
    transform: scale(1.05);
}

.question-preview, .question-full {
    display: inline;
    line-height: 1.4;
}

.subtitle-text {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-wrap: wrap;
    gap: 8px;
}

@media (max-width: 768px) {
    .show-full-btn {
        display: block;
        margin: 8px auto 0;
        width: fit-content;
    }
    
    .subtitle-text {
        flex-direction: column;
        text-align: center;
    }
}
</style>
`;

// Inject CSS
document.head.insertAdjacentHTML('beforeend', partialQuestionCSS);

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    // Handle initial question display
    const subtitleText = document.getElementById('subtitleText');
    if (subtitleText && subtitleText.textContent) {
        const currentText = subtitleText.textContent;
        const match = currentText.match(/AI: "(.+)"/);
        if (match && match[1]) {
            const question = match[1];
            window.questionManager.updateSubtitleWithPartial(question, 'AI');
        }
    }
});

console.log('✅ Partial question display manager loaded');