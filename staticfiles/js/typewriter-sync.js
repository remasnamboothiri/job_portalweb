/**
 * Typewriter System - TEXT ONLY VERSION (No Audio)
 * Prevents feedback loop by removing audio entirely during typing
 */

(function() {
    'use strict';
    
    console.log('📝 Typewriter System Loading - TEXT ONLY VERSION...');
    
    // Configuration
    const CONFIG = {
        standardSpeed: 50,          // milliseconds per character for standard typing
        fastSpeed: 30,              // milliseconds per character for fast typing
        minDuration: 1000,          // minimum duration in milliseconds
        maxDuration: 8000,          // maximum duration in milliseconds
    };
    
    /**
     * Text-only typewriter - no audio synchronization
     */
    function createTextOnlyTypewriter(element, text, options = {}) {
        return new Promise((resolve) => {
            element.textContent = '';
            let index = 0;
            
            console.log(`📝 TEXT ONLY: Starting typewriter: ${text.length} chars`);
            
            const speed = options.fast ? CONFIG.fastSpeed : CONFIG.standardSpeed;
            
            const typeInterval = setInterval(() => {
                if (index < text.length) {
                    element.textContent += text.charAt(index);
                    index++;
                } else {
                    clearInterval(typeInterval);
                    console.log('📝 TEXT ONLY: Typewriter completed');
                    resolve();
                }
            }, speed);
        });
    }
    
    /**
     * Smart duration typewriter - adjusts speed based on content length
     */
    function createSmartTypewriter(element, text, targetDuration = null, options = {}) {
        return new Promise((resolve) => {
            element.textContent = '';
            let index = 0;
            
            if (!targetDuration || targetDuration <= 0) {
                targetDuration = Math.min(text.length * 60, CONFIG.maxDuration);
            }
            
            const charDelay = Math.max(CONFIG.fastSpeed, Math.min(CONFIG.standardSpeed, targetDuration / text.length));
            
            console.log(`📝 SMART: ${text.length} chars, ${targetDuration}ms duration, ${charDelay}ms per char`);
            
            const typeInterval = setInterval(() => {
                if (index < text.length) {
                    element.textContent += text.charAt(index);
                    index++;
                } else {
                    clearInterval(typeInterval);
                    console.log('📝 SMART: Typewriter completed');
                    resolve();
                }
            }, charDelay);
        });
    }
    
    /**
     * Main typewriter function - always text-only now
     */
    function startTypewriter(element, text, audioElement = null, duration = null, options = {}) {
        if (!element || !text) {
            console.error('📝 TEXT ONLY: Invalid element or text');
            return Promise.resolve();
        }
        
        element.textContent = '';
        console.log('📝 TEXT ONLY: Starting text-only typewriter (no audio)');
        
        // Ignore audio parameters completely
        return createSmartTypewriter(element, text, duration, options);
    }
    
    /**
     * Estimate natural reading duration
     */
    function estimateReadingDuration(text, wordsPerMinute = 150) {
        if (!text || !text.trim()) {
            return 2.0;
        }
        
        const wordCount = text.split(/\s+/).length;
        const baseDuration = (wordCount / wordsPerMinute) * 60;
        const withPauses = baseDuration * 1.2; // Add 20% for reading pauses
        
        return Math.max(2.0, Math.min(withPauses, 20.0));
    }
    
    // Export to global scope
    window.TypewriterSync = {
        start: startTypewriter,
        createTextOnly: createTextOnlyTypewriter,
        createSmart: createSmartTypewriter,
        estimateDuration: estimateReadingDuration,
        config: CONFIG
    };
    
    console.log('✅ Typewriter System Loaded - TEXT ONLY VERSION');
    console.log('📋 Available methods:');
    console.log('  - window.TypewriterSync.start(element, text) - NO AUDIO');
    console.log('  - window.TypewriterSync.createTextOnly(element, text)');
    console.log('  - window.TypewriterSync.createSmart(element, text, duration)');
    console.log('  - window.TypewriterSync.estimateDuration(text)');
    console.log('📝 Text-only mode - prevents audio feedback loop');
    
})();