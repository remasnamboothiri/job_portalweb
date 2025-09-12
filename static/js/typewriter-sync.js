/**
 * Typewriter Synchronization System
 * Synchronizes text typing with audio playback for natural interview experience
 */

(function() {
    'use strict';
    
    console.log('🔤 Typewriter Sync System Loading...');
    
    // Configuration
    const CONFIG = {
        naturalTypingSpeed: 80,     // milliseconds per character for natural feel
        minDuration: 2000,          // minimum duration in milliseconds
        maxDuration: 30000,         // maximum duration in milliseconds
        syncTolerance: 2,           // characters tolerance for sync adjustment
        speedUpDelay: 30,           // fast typing delay when behind
        slowDownDelay: 120,         // slow typing delay when ahead
        normalDelay: 80             // normal typing delay
    };
    
    /**
     * Enhanced typewriter effect with audio synchronization - FIXED VERSION
     */
    function createSynchronizedTypewriter(element, text, audioElement, options = {}) {
        const config = { ...CONFIG, ...options };
        
        return new Promise((resolve) => {
            // CRITICAL FIX: Ensure text is cleared and stays empty until audio starts
            element.textContent = '';
            let index = 0;
            let startTime = Date.now();
            let audioStarted = false;
            let isComplete = false;
            let hasStartedTyping = false;
            
            const totalChars = text.length;
            
            console.log(`🔤 FIXED: Starting synchronized typewriter: ${totalChars} chars`);
            console.log(`🔊 FIXED: Audio element:`, audioElement ? 'Available' : 'Not available');
            
            function typeNextCharacter() {
                if (isComplete || index >= totalChars) {
                    if (!isComplete) {
                        isComplete = true;
                        console.log('🔤 FIXED: Typewriter completed');
                        resolve();
                    }
                    return;
                }
                
                // CRITICAL FIX: Only start typing if audio is playing or no audio
                if (audioElement && audioElement.paused && !hasStartedTyping) {
                    // Audio not playing yet, wait
                    setTimeout(typeNextCharacter, 50);
                    return;
                }
                
                // Mark that we've started typing
                if (!hasStartedTyping) {
                    hasStartedTyping = true;
                    console.log('🔤 FIXED: Starting to type - audio is ready');
                }
                
                // Add next character
                element.textContent += text.charAt(index);
                index++;
                
                // Calculate next delay based on audio sync
                let nextDelay = config.normalDelay;
                
                if (audioElement && !audioElement.paused && audioElement.duration > 0) {
                    if (!audioStarted) {
                        audioStarted = true;
                        startTime = Date.now();
                        console.log('🔊 FIXED: Audio playback detected, syncing typewriter');
                    }
                    
                    // Calculate expected position based on audio progress
                    const audioProgress = audioElement.currentTime / audioElement.duration;
                    const expectedIndex = Math.floor(audioProgress * totalChars);
                    const indexDifference = index - expectedIndex;
                    
                    // Adjust typing speed based on sync
                    if (indexDifference < -config.syncTolerance) {
                        // Behind audio, speed up
                        nextDelay = config.speedUpDelay;
                    } else if (indexDifference > config.syncTolerance) {
                        // Ahead of audio, slow down
                        nextDelay = config.slowDownDelay;
                    } else {
                        // In sync, normal speed
                        nextDelay = config.normalDelay;
                    }
                    
                    // Debug sync info every 10 characters
                    if (index % 10 === 0) {
                        console.log(`🔄 FIXED: Sync: audio ${(audioProgress * 100).toFixed(1)}%, text ${((index / totalChars) * 100).toFixed(1)}%, delay ${nextDelay}ms`);
                    }
                }
                
                // Schedule next character
                setTimeout(typeNextCharacter, nextDelay);
            }
            
            // CRITICAL FIX: Wait a moment before starting to ensure audio is ready
            setTimeout(() => {
                typeNextCharacter();
            }, 100);
            
            // Fallback completion timer
            const estimatedDuration = Math.max(config.minDuration, Math.min(totalChars * config.naturalTypingSpeed, config.maxDuration));
            setTimeout(() => {
                if (!isComplete) {
                    console.log('🔤 FIXED: Typewriter fallback completion triggered');
                    isComplete = true;
                    element.textContent = text; // Ensure full text is shown
                    resolve();
                }
            }, estimatedDuration + 3000); // Add 3 second buffer
        });
    }
    
    /**
     * Natural typewriter effect without audio sync
     */
    function createNaturalTypewriter(element, text, duration = null, options = {}) {
        const config = { ...CONFIG, ...options };
        
        return new Promise((resolve) => {
            element.textContent = '';
            let index = 0;
            const totalChars = text.length;
            
            // Calculate effective duration
            const effectiveDuration = duration ? 
                (duration * 1000) : 
                Math.max(config.minDuration, Math.min(totalChars * config.naturalTypingSpeed, config.maxDuration));
            
            const charDelay = effectiveDuration / totalChars;
            
            console.log(`🔤 Natural typewriter: ${totalChars} chars, ${effectiveDuration}ms total, ${charDelay.toFixed(1)}ms per char`);
            
            function typeNextCharacter() {
                if (index < totalChars) {
                    element.textContent += text.charAt(index);
                    index++;
                    setTimeout(typeNextCharacter, charDelay);
                } else {
                    console.log('🔤 Natural typewriter completed');
                    resolve();
                }
            }
            
            typeNextCharacter();
        });
    }
    
    /**
     * Main typewriter function with automatic sync detection - FIXED VERSION
     */
    function startTypewriter(element, text, audioElement = null, duration = null, options = {}) {
        if (!element || !text) {
            console.error('🔤 FIXED: Typewriter: Invalid element or text');
            return Promise.resolve();
        }
        
        // CRITICAL FIX: Clear element and ensure it stays empty
        element.textContent = '';
        
        // Choose typewriter method - FIXED logic
        if (audioElement && audioElement.src && audioElement.src.trim() !== '') {
            console.log('🔤 FIXED: Using synchronized typewriter with audio');
            return createSynchronizedTypewriter(element, text, audioElement, options);
        } else {
            console.log('🔤 FIXED: Using natural typewriter (no audio sync)');
            return createNaturalTypewriter(element, text, duration, options);
        }
    }
    
    /**
     * Estimate natural speaking duration
     */
    function estimateSpeechDuration(text, wordsPerMinute = 140) {
        if (!text || !text.trim()) {
            return 2.0;
        }
        
        const wordCount = text.split(/\s+/).length;
        const baseDuration = (wordCount / wordsPerMinute) * 60;
        const withPauses = baseDuration * 1.15; // Add 15% for natural pauses
        
        return Math.max(2.0, Math.min(withPauses, 30.0));
    }
    
    // Export to global scope
    window.TypewriterSync = {
        start: startTypewriter,
        createSynchronized: createSynchronizedTypewriter,
        createNatural: createNaturalTypewriter,
        estimateDuration: estimateSpeechDuration,
        config: CONFIG
    };
    
    console.log('✅ Typewriter Sync System Loaded');
    console.log('📋 Available methods:');
    console.log('  - window.TypewriterSync.start(element, text, audioElement, duration)');
    console.log('  - window.TypewriterSync.createSynchronized(element, text, audioElement)');
    console.log('  - window.TypewriterSync.createNatural(element, text, duration)');
    console.log('  - window.TypewriterSync.estimateDuration(text)');
    
})();