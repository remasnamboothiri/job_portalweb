/**
 * Typewriter Synchronization System
 * Synchronizes text typing with audio playback for natural interview experience
 */

(function() {
    'use strict';
    
    console.log('🔤 Typewriter Sync System Loading - COMPLETELY FIXED VERSION...');
    
    // Configuration - OPTIMIZED FOR BETTER SYNC
    const CONFIG = {
        naturalTypingSpeed: 60,     // milliseconds per character for natural feel (faster)
        minDuration: 2000,          // minimum duration in milliseconds
        maxDuration: 30000,         // maximum duration in milliseconds
        syncTolerance: 3,           // characters tolerance for sync adjustment (more forgiving)
        speedUpDelay: 20,           // fast typing delay when behind (much faster)
        slowDownDelay: 150,         // slow typing delay when ahead (slower)
        normalDelay: 60,            // normal typing delay (faster)
        audioCheckInterval: 50,     // how often to check audio status (ms)
        maxWaitForAudio: 5000       // maximum time to wait for audio to start (ms)
    };
    
    /**
     * Enhanced typewriter effect with audio synchronization - COMPLETELY FIXED VERSION
     */
    function createSynchronizedTypewriter(element, text, audioElement, options = {}) {
        const config = { ...CONFIG, ...options };
        
        return new Promise((resolve) => {
            // CRITICAL FIX: Ensure text is cleared and stays empty until audio ACTUALLY starts
            element.textContent = '';
            let index = 0;
            let startTime = Date.now();
            let audioStarted = false;
            let isComplete = false;
            let hasStartedTyping = false;
            let audioPlaybackConfirmed = false;
            
            const totalChars = text.length;
            
            console.log(`🔤 COMPLETELY FIXED: Starting synchronized typewriter: ${totalChars} chars`);
            console.log(`🔊 COMPLETELY FIXED: Audio element:`, audioElement ? 'Available' : 'Not available');
            
            function typeNextCharacter() {
                if (isComplete || index >= totalChars) {
                    if (!isComplete) {
                        isComplete = true;
                        console.log('🔤 COMPLETELY FIXED: Typewriter completed');
                        resolve();
                    }
                    return;
                }
                
                // CRITICAL FIX: Only start typing if audio is ACTUALLY playing (not just loaded)
                if (audioElement && !audioPlaybackConfirmed && !hasStartedTyping) {
                    // Check if audio is actually playing
                    if (audioElement.currentTime > 0 && !audioElement.paused) {
                        audioPlaybackConfirmed = true;
                        console.log('🔤 COMPLETELY FIXED: Audio playback confirmed via currentTime');
                    } else {
                        // Audio not playing yet, wait
                        setTimeout(typeNextCharacter, 50);
                        return;
                    }
                }
                
                // Mark that we've started typing
                if (!hasStartedTyping) {
                    hasStartedTyping = true;
                    console.log('🔤 COMPLETELY FIXED: Starting to type - audio is confirmed playing');
                }
                
                // Add next character
                element.textContent += text.charAt(index);
                index++;
                
                // Calculate next delay based on audio sync
                let nextDelay = config.normalDelay;
                
                if (audioElement && !audioElement.paused && audioElement.duration > 0 && audioElement.currentTime > 0) {
                    if (!audioStarted) {
                        audioStarted = true;
                        startTime = Date.now();
                        console.log('🔊 COMPLETELY FIXED: Audio playback detected, syncing typewriter');
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
                        console.log(`🔄 COMPLETELY FIXED: Sync: audio ${(audioProgress * 100).toFixed(1)}%, text ${((index / totalChars) * 100).toFixed(1)}%, delay ${nextDelay}ms`);
                    }
                }
                
                // Schedule next character
                setTimeout(typeNextCharacter, nextDelay);
            }
            
            // CRITICAL FIX: Wait for audio to actually start playing before beginning typewriter
            const waitForAudioStart = () => {
                if (audioElement && audioElement.currentTime > 0 && !audioElement.paused) {
                    console.log('🔤 COMPLETELY FIXED: Audio confirmed playing, starting typewriter');
                    typeNextCharacter();
                } else if (!audioElement) {
                    console.log('🔤 COMPLETELY FIXED: No audio element, starting typewriter immediately');
                    typeNextCharacter();
                } else {
                    // Keep waiting for audio to start
                    setTimeout(waitForAudioStart, 100);
                }
            };
            
            // Start waiting for audio
            setTimeout(waitForAudioStart, 200); // Small initial delay
            
            // Fallback completion timer (longer to account for audio loading)
            const estimatedDuration = Math.max(config.minDuration, Math.min(totalChars * config.naturalTypingSpeed, config.maxDuration));
            setTimeout(() => {
                if (!isComplete) {
                    console.log('🔤 COMPLETELY FIXED: Typewriter fallback completion triggered');
                    isComplete = true;
                    element.textContent = text; // Ensure full text is shown
                    resolve();
                }
            }, estimatedDuration + 5000); // Add 5 second buffer for audio loading
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
    
    console.log('✅ Typewriter Sync System Loaded - COMPLETELY FIXED VERSION');
    console.log('📋 Available methods:');
    console.log('  - window.TypewriterSync.start(element, text, audioElement, duration)');
    console.log('  - window.TypewriterSync.createSynchronized(element, text, audioElement)');
    console.log('  - window.TypewriterSync.createNatural(element, text, duration)');
    console.log('  - window.TypewriterSync.estimateDuration(text)');
    console.log('🔧 Optimized for better audio-text synchronization');
    
})();