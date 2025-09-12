/**
 * Typewriter Synchronization System
 * Synchronizes text typing with audio playback for natural interview experience
 */

(function() {
    'use strict';
    
    console.log('🔤 Typewriter Sync System Loading - SIMPLE DIRECT SYNC...');
    
    // Configuration - SIMPLE AND DIRECT SYNC
    const CONFIG = {
        naturalTypingSpeed: 50,     // milliseconds per character for natural feel
        minDuration: 2000,          // minimum duration in milliseconds
        maxDuration: 30000,         // maximum duration in milliseconds
        syncCheckInterval: 100,     // how often to check sync (ms)
        maxWaitForAudio: 3000       // maximum time to wait for audio to start (ms)
    };
    
    /**
     * SIMPLE DIRECT SYNC - Calculate exact timing from audio duration
     */
    function createSynchronizedTypewriter(element, text, audioElement, options = {}) {
        const config = { ...CONFIG, ...options };
        
        return new Promise((resolve) => {
            element.textContent = '';
            let index = 0;
            let isComplete = false;
            let syncInterval = null;
            
            const totalChars = text.length;
            
            console.log(`🔤 SIMPLE SYNC: Starting typewriter: ${totalChars} chars`);
            
            function typeNextCharacter() {
                if (isComplete || index >= totalChars) {
                    if (!isComplete) {
                        isComplete = true;
                        if (syncInterval) clearInterval(syncInterval);
                        console.log('🔤 SIMPLE SYNC: Typewriter completed');
                        resolve();
                    }
                    return;
                }
                
                element.textContent += text.charAt(index);
                index++;
            }
            
            // Wait for audio to start, then calculate exact timing
            const startSyncedTyping = () => {
                if (!audioElement || audioElement.paused || audioElement.duration <= 0) {
                    // No audio or not ready, use natural timing
                    const charDelay = config.naturalTypingSpeed;
                    const typeChar = () => {
                        typeNextCharacter();
                        if (index < totalChars) {
                            setTimeout(typeChar, charDelay);
                        }
                    };
                    typeChar();
                    return;
                }
                
                // DIRECT CALCULATION: Divide audio duration by character count
                const audioDurationMs = audioElement.duration * 1000;
                const charDelay = audioDurationMs / totalChars;
                
                console.log(`🔤 SIMPLE SYNC: Audio duration: ${audioDurationMs}ms, chars: ${totalChars}, delay per char: ${charDelay.toFixed(1)}ms`);
                
                // Start typing at calculated intervals
                syncInterval = setInterval(() => {
                    typeNextCharacter();
                }, charDelay);
            };
            
            // Wait for audio to be ready and playing
            const waitForAudio = () => {
                if (audioElement && audioElement.currentTime > 0 && !audioElement.paused && audioElement.duration > 0) {
                    console.log('🔤 SIMPLE SYNC: Audio ready, starting synchronized typing');
                    startSyncedTyping();
                } else if (!audioElement) {
                    console.log('🔤 SIMPLE SYNC: No audio, using natural timing');
                    startSyncedTyping();
                } else {
                    setTimeout(waitForAudio, 100);
                }
            };
            
            // Start waiting
            setTimeout(waitForAudio, 200);
            
            // Fallback timer
            setTimeout(() => {
                if (!isComplete) {
                    console.log('🔤 SIMPLE SYNC: Fallback completion');
                    isComplete = true;
                    if (syncInterval) clearInterval(syncInterval);
                    element.textContent = text;
                    resolve();
                }
            }, config.maxWaitForAudio + (audioElement?.duration * 1000 || 5000));
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
     * Main typewriter function with automatic sync detection - COMPLETELY FIXED VERSION
     */
    function startTypewriter(element, text, audioElement = null, duration = null, options = {}) {
        if (!element || !text) {
            console.error('🔤 COMPLETELY FIXED: Typewriter: Invalid element or text');
            return Promise.resolve();
        }
        
        // CRITICAL FIX: Clear element and ensure it stays empty
        element.textContent = '';
        
        // Choose typewriter method - COMPLETELY FIXED logic
        if (audioElement && audioElement.src && audioElement.src.trim() !== '') {
            console.log('🔤 COMPLETELY FIXED: Using synchronized typewriter with audio');
            return createSynchronizedTypewriter(element, text, audioElement, options);
        } else {
            console.log('🔤 COMPLETELY FIXED: Using natural typewriter (no audio sync)');
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
    
    console.log('✅ Typewriter Sync System Loaded - SIMPLE DIRECT SYNC');
    console.log('📋 Available methods:');
    console.log('  - window.TypewriterSync.start(element, text, audioElement, duration)');
    console.log('  - window.TypewriterSync.createSynchronized(element, text, audioElement)');
    console.log('  - window.TypewriterSync.createNatural(element, text, duration)');
    console.log('  - window.TypewriterSync.estimateDuration(text)');
    console.log('🔧 Simple direct calculation for perfect sync');
    
})();