/**
 * Typewriter Synchronization System - INSTANT START VERSION
 * Starts typing immediately while audio loads for natural interview experience
 */

(function() {
    'use strict';
    
    console.log('⚡ Typewriter Sync System Loading - ULTRA FAST VERSION...');
    
    // Configuration - ULTRA FAST
    const CONFIG = {
        ultraFastSpeed: 25,         // milliseconds per character - ultra fast
        minDuration: 500,           // minimum duration in milliseconds
        maxDuration: 5000,          // maximum duration in milliseconds
    };
    
    /**
     * ULTRA FAST TYPEWRITER - No sync, just speed
     */
    function createSynchronizedTypewriter(element, text, audioElement, options = {}) {
        return new Promise((resolve) => {
            element.textContent = '';
            let index = 0;
            
            console.log(`⚡ ULTRA FAST: Starting typewriter: ${text.length} chars`);
            
            const typeInterval = setInterval(() => {
                if (index < text.length) {
                    element.textContent += text.charAt(index);
                    index++;
                } else {
                    clearInterval(typeInterval);
                    console.log('⚡ ULTRA FAST: Typewriter completed');
                    resolve();
                }
            }, 25); // 25ms per character = ultra fast
        });
    }
    
    /**
     * Ultra fast natural typewriter
     */
    function createNaturalTypewriter(element, text, duration = null, options = {}) {
        return new Promise((resolve) => {
            element.textContent = '';
            let index = 0;
            
            console.log(`⚡ ULTRA FAST Natural: ${text.length} chars`);
            
            const typeInterval = setInterval(() => {
                if (index < text.length) {
                    element.textContent += text.charAt(index);
                    index++;
                } else {
                    clearInterval(typeInterval);
                    console.log('⚡ ULTRA FAST Natural completed');
                    resolve();
                }
            }, 25); // 25ms per character = ultra fast
        });
    }
    
    /**
     * Ultra fast typewriter - always 25ms per character
     */
    function startTypewriter(element, text, audioElement = null, duration = null, options = {}) {
        if (!element || !text) {
            console.error('⚡ ULTRA FAST: Invalid element or text');
            return Promise.resolve();
        }
        
        element.textContent = '';
        console.log('⚡ ULTRA FAST: Starting ultra fast typewriter');
        return createNaturalTypewriter(element, text, null, options);
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
    
    console.log('✅ Typewriter Sync System Loaded - ULTRA FAST VERSION');
    console.log('📋 Available methods:');
    console.log('  - window.TypewriterSync.start(element, text, audioElement, duration)');
    console.log('  - window.TypewriterSync.createSynchronized(element, text, audioElement)');
    console.log('  - window.TypewriterSync.createNatural(element, text, duration)');
    console.log('  - window.TypewriterSync.estimateDuration(text)');
    console.log('⚡ Ultra fast 25ms per character - no delays, no waiting');
    
})();
// Force Git update