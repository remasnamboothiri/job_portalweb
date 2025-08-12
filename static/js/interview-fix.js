// Quick fix for interview network errors
function fixNetworkError() {
    // Override the processSpeechResult function to handle errors better
    window.processSpeechResult = async function(speechText) {
        try {
            console.log('Processing speech result:', speechText);
            
            // Show sending status
            const statusElement = document.getElementById('responseStatus');
            if (statusElement) {
                statusElement.innerHTML = '📤 Sending your response...';
            }
            
            // Get CSRF token
            function getCSRFToken() {
                const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
                if (csrfInput && csrfInput.value) {
                    return csrfInput.value;
                }
                
                const cookies = document.cookie.split(';');
                for (let cookie of cookies) {
                    const [name, value] = cookie.trim().split('=');
                    if (name === 'csrftoken') {
                        return value;
                    }
                }
                return '';
            }
            
            // Prepare form data
            const formData = new FormData();
            formData.append('text', speechText);
            
            // Send request with better error handling
            const response = await fetch(window.location.href, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                handleAIResponse(data);
            } else {
                console.error('Backend error:', data.error);
                if (statusElement) {
                    statusElement.innerHTML = '❌ Error processing response. Please try again.';
                }
            }
            
        } catch (error) {
            console.error('Error sending response:', error);
            const statusElement = document.getElementById('responseStatus');
            if (statusElement) {
                statusElement.innerHTML = '❌ Connection error. Please check your internet and try again.';
            }
            
            // Reset UI after error
            setTimeout(() => {
                if (statusElement) {
                    statusElement.innerHTML = 'Microphone is ready. You can speak anytime.';
                }
            }, 3000);
        }
    };
}

// Apply fix when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', fixNetworkError);
} else {
    fixNetworkError();
}