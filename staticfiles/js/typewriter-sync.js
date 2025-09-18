/**
 * Typewriter Synchronization System - INTERVIEW OPTIMIZED
 * Fast, reliable typewriter without audio sync issues
 */

(function() {
    'use strict';
    
    console.log('⚡ Typewriter Sync System Loading - INTERVIEW OPTIMIZED...');
    
    // Configuration for natural interview flow
    const CONFIG = {
        interviewerSpeed: 40,       // 40ms per character for interviewer questions
        candidateSpeed: 20,         // 20ms per character for candidate responses (faster)
        minDuration: 1000,          // minimum 1 second
        maxDuration: 8000,          // maximum 8 seconds
    };
    
    /**
     * Natural interview typewriter - no complex sync, just smooth typing
     */
    function createInterviewTypewriter(element, text, isInterviewer = false) {
        return new Promise((resolve) => {
            if (!element || !text) {
                console.warn('⚠️ Invalid element or text for typewriter');
                resolve();
                return;
            }
            
            element.textContent = '';
            let index = 0;
            const speed = isInterviewer ? CONFIG.interviewerSpeed : CONFIG.candidateSpeed;
            
            console.log(`⚡ Starting ${isInterviewer ? 'interviewer' : 'candidate'} typewriter: ${text.length} chars at ${speed}ms/char`);
            
            const typeInterval = setInterval(() => {
                if (index < text.length) {
                    element.textContent += text.charAt(index);
                    index++;
                } else {
                    clearInterval(typeInterval);
                    console.log(`✅ ${isInterviewer ? 'Interviewer' : 'Candidate'} typewriter completed`);
                    resolve();
                }
            }, speed);
        });
    }
    
    /**
     * Simple natural typewriter for any text
     */
    function createNaturalTypewriter(element, text, speed = 30) {
        return new Promise((resolve) => {
            if (!element || !text) {
                resolve();
                return;
            }
            
            element.textContent = '';
            let index = 0;
            
            const typeInterval = setInterval(() => {
                if (index < text.length) {
                    element.textContent += text.charAt(index);
                    index++;
                } else {
                    clearInterval(typeInterval);
                    resolve();
                }
            }, speed);
        });
    }
    
    /**
     * Main typewriter function for interview
     */
    function startInterviewTypewriter(element, text, options = {}) {
        if (!element || !text) {
            console.error('⚠️ Invalid parameters for interview typewriter');
            return Promise.resolve();
        }
        
        const isInterviewer = options.isInterviewer || false;
        const speed = options.speed || (isInterviewer ? CONFIG.interviewerSpeed : CONFIG.candidateSpeed);
        
        console.log(`🎯 Starting interview typewriter - ${isInterviewer ? 'Interviewer' : 'Candidate'} mode`);
        
        return createNaturalTypewriter(element, text, speed);
    }
    
    /**
     * Estimate natural speaking duration (for reference only)
     */
    function estimateSpeechDuration(text, wordsPerMinute = 140) {
        if (!text || !text.trim()) {
            return 2.0;
        }
        
        const wordCount = text.split(/\s+/).length;
        const baseDuration = (wordCount / wordsPerMinute) * 60;
        const withPauses = baseDuration * 1.2; // Add 20% for natural pauses
        
        return Math.max(2.0, Math.min(withPauses, 12.0)); // 2-12 seconds range
    }
    
    /**
     * Clear typewriter and reset element
     */
    function clearTypewriter(element) {
        if (element) {
            element.textContent = '';
            element.className = element.className.replace(/typewriter-\w+/g, '').trim();
        }
    }
    
    // Export to global scope
    window.TypewriterSync = {
        start: startInterviewTypewriter,
        createInterview: createInterviewTypewriter,
        createNatural: createNaturalTypewriter,
        clear: clearTypewriter,
        estimateDuration: estimateSpeechDuration,
        config: CONFIG
    };
    
    console.log('✅ Typewriter Sync System Ready - INTERVIEW OPTIMIZED');
    console.log('📋 Available methods:');
    console.log('  - window.TypewriterSync.start(element, text, {isInterviewer: boolean})');
    console.log('  - window.TypewriterSync.createInterview(element, text, isInterviewer)');
    console.log('  - window.TypewriterSync.createNatural(element, text, speed)');
    console.log('  - window.TypewriterSync.clear(element)');
    console.log(`⚡ Interviewer: ${CONFIG.interviewerSpeed}ms/char, Candidate: ${CONFIG.candidateSpeed}ms/char`);
    
})();