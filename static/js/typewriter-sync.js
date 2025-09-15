/**
 * Typewriter Synchronization System - INSTANT START VERSION
 * Starts typing immediately while audio loads for natural interview experience
 */

(function() {
    'use strict';
    
    console.log('🔤 Typewriter Sync System Loading - INSTANT START VERSION...');
    
    // Configuration - OPTIMIZED FOR INSTANT START
    const CONFIG = {
        instantTypingSpeed: 35,     // milliseconds per character for instant start
        naturalTypingSpeed: 50,     // milliseconds per character for natural feel
        minDuration: 1500,          // minimum duration in milliseconds
        maxDuration: 25000,         // maximum duration in milliseconds
        syncAdjustmentInterval: 200, // how often to adjust sync (ms)
        maxWaitForAudio: 1000       // maximum time to wait for audio metadata (ms)
    };
    
    /**
     * INSTANT START SYNC - Start typing immediately, adjust speed when audio loads
     */
    function createSynchronizedTypewriter(element, text, audioElement, options = {}) {
        const config = { ...CONFIG, ...options };
        
        return new Promise((resolve) => {
            element.textContent = '';
            let index = 0;
            let isComplete = false;
            let currentInterval = null;
            let currentSpeed = config.instantTypingSpeed;
            
            const totalChars = text.length;
            
            console.log(`🔤 INSTANT START: Starting typewriter immediately: ${totalChars} chars`);
            
            function typeNextCharacter() {
                if (isComplete || index >= totalChars) {
                    if (!isComplete) {
                        isComplete = true;
                        if (currentInterval) clearInterval(currentInterval);
                        console.log('🔤 INSTANT START: Typewriter completed');
                        resolve();
                    }
                    return;
                }
                
                element.textContent += text.charAt(index);
                index++;
            }
            
            function startTypingWithSpeed(speed) {
                if (currentInterval) clearInterval(currentInterval);
                currentSpeed = speed;
                
                currentInterval = setInterval(() => {
                    typeNextCharacter();
                }, speed);
                
                console.log(`🔤 INSTANT START: Typing at ${speed}ms per character`);
            }
            
            function adjustSpeedForAudio() {
                if (!audioElement || !audioElement.duration || audioElement.duration <= 0) {
                    return; // Keep current speed
                }
                
                const remainingChars = totalChars - index;
                if (remainingChars <= 0) return;
                
                const audioDurationMs = audioElement.duration * 1000;
                const elapsedTime = index * currentSpeed;
                const remainingTime = Math.max(audioDurationMs - elapsedTime, remainingChars * 20); // minimum 20ms per char
                const newSpeed = remainingTime / remainingChars;
                
                if (Math.abs(newSpeed - currentSpeed) > 10) { // Only adjust if significant difference
                    console.log(`🔤 INSTANT START: Adjusting speed from ${currentSpeed}ms to ${newSpeed.toFixed(1)}ms per char`);
                    startTypingWithSpeed(Math.max(20, Math.min(newSpeed, 200))); // Clamp between 20-200ms
                }
            }
            
            // START TYPING IMMEDIATELY
            startTypingWithSpeed(config.instantTypingSpeed);
            
            // Monitor audio loading and adjust speed
            if (audioElement) {
                const checkAudioAndAdjust = () => {
                    if (audioElement.duration > 0 && !isComplete) {
                        adjustSpeedForAudio();
                    }
                };
                
                // Check for audio metadata
                audioElement.addEventListener('loadedmetadata', checkAudioAndAdjust);
                audioElement.addEventListener('canplay', checkAudioAndAdjust);
                audioElement.addEventListener('play', checkAudioAndAdjust);
                
                // Periodic adjustment while typing
                const adjustmentInterval = setInterval(() => {
                    if (isComplete) {
                        clearInterval(adjustmentInterval);
                        return;
                    }
                    checkAudioAndAdjust();
                }, config.syncAdjustmentInterval);
                
                // Initial check after short delay
                setTimeout(checkAudioAndAdjust, 100);
            }
            
            // Fallback completion
            setTimeout(() => {
                if (!isComplete) {
                    console.log('🔤 INSTANT START: Fallback completion');
                    isComplete = true;
                    if (currentInterval) clearInterval(currentInterval);
                    element.textContent = text;
                    resolve();
                }
            }, config.maxDuration);
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
            
            const typeInterval = setInterval(() => {
                if (index < totalChars) {
                    element.textContent += text.charAt(index);
                    index++;
                } else {
                    clearInterval(typeInterval);
                    console.log('🔤 Natural typewriter completed');
                    resolve();
                }
            }, charDelay);
        });
    }
    
    /**
     * Main typewriter function with instant start - OPTIMIZED VERSION
     */
    function startTypewriter(element, text, audioElement = null, duration = null, options = {}) {
        if (!element || !text) {
            console.error('🔤 INSTANT START: Typewriter: Invalid element or text');
            return Promise.resolve();
        }
        
        // Clear element immediately
        element.textContent = '';
        
        // Always start typing immediately - adjust for audio if available
        if (audioElement && audioElement.src && audioElement.src.trim() !== '') {
            console.log('🔤 INSTANT START: Using synchronized typewriter with instant start');
            return createSynchronizedTypewriter(element, text, audioElement, options);
        } else {
            console.log('🔤 INSTANT START: Using fast natural typewriter');
            // Use faster natural typing when no audio
            const fastDuration = duration ? Math.min(duration, 3) : Math.min(text.length * 0.03, 3);
            return createNaturalTypewriter(element, text, fastDuration, options);
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
    
    console.log('✅ Typewriter Sync System Loaded - INSTANT START VERSION');
    console.log('📋 Available methods:');
    console.log('  - window.TypewriterSync.start(element, text, audioElement, duration)');
    console.log('  - window.TypewriterSync.createSynchronized(element, text, audioElement)');
    console.log('  - window.TypewriterSync.createNatural(element, text, duration)');
    console.log('  - window.TypewriterSync.estimateDuration(text)');
    console.log('🚀 Instant start with dynamic speed adjustment for perfect sync');
    
})();