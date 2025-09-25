// /**
//  * Typewriter System - WITH AUDIO SUPPORT
//  * Properly handles audio playback and text synchronization
//  */

// (function() {
//     'use strict';
    
//     console.log('📝 Typewriter System Loading - WITH AUDIO SUPPORT...');
    
//     // Configuration
//     const CONFIG = {
//         standardSpeed: 50,          // milliseconds per character for standard typing
//         fastSpeed: 30,              // milliseconds per character for fast typing
//         minDuration: 1000,          // minimum duration in milliseconds
//         maxDuration: 8000,          // maximum duration in milliseconds
//     };
    
//     /**
//      * Text-only typewriter - no audio synchronization
//      */
//     function createTextOnlyTypewriter(element, text, options = {}) {
//         return new Promise((resolve) => {
//             element.textContent = '';
//             let index = 0;
            
//             console.log(`📝 TEXT ONLY: Starting typewriter: ${text.length} chars`);
            
//             const speed = options.fast ? CONFIG.fastSpeed : CONFIG.standardSpeed;
            
//             const typeInterval = setInterval(() => {
//                 if (index < text.length) {
//                     element.textContent += text.charAt(index);
//                     index++;
//                 } else {
//                     clearInterval(typeInterval);
//                     console.log('📝 TEXT ONLY: Typewriter completed');
//                     resolve();
//                 }
//             }, speed);
//         });
//     }
    
//     /**
//      * Smart duration typewriter - adjusts speed based on content length
//      */
//     function createSmartTypewriter(element, text, targetDuration = null, options = {}) {
//         return new Promise((resolve) => {
//             element.textContent = '';
//             let index = 0;
            
//             if (!targetDuration || targetDuration <= 0) {
//                 targetDuration = Math.min(text.length * 60, CONFIG.maxDuration);
//             }
            
//             const charDelay = Math.max(CONFIG.fastSpeed, Math.min(CONFIG.standardSpeed, targetDuration / text.length));
            
//             console.log(`📝 SMART: ${text.length} chars, ${targetDuration}ms duration, ${charDelay}ms per char`);
            
//             const typeInterval = setInterval(() => {
//                 if (index < text.length) {
//                     element.textContent += text.charAt(index);
//                     index++;
//                 } else {
//                     clearInterval(typeInterval);
//                     console.log('📝 SMART: Typewriter completed');
//                     resolve();
//                 }
//             }, charDelay);
//         });
//     }
    
//     /**
//      * Audio-synchronized typewriter
//      */
//     function createAudioSyncTypewriter(element, text, audioElement, audioDuration) {
//         return new Promise((resolve) => {
//             element.textContent = '';
//             let index = 0;
//             let audioPlaying = false;
            
//             const charDelay = Math.max(30, (audioDuration * 1000) / text.length);
            
//             console.log(`🔊 AUDIO SYNC: ${text.length} chars, ${audioDuration}s audio, ${charDelay}ms per char`);
            
//             // Start typewriter when audio plays
//             const startTypewriter = () => {
//                 if (audioPlaying) return;
//                 audioPlaying = true;
                
//                 const typeInterval = setInterval(() => {
//                     if (index < text.length) {
//                         element.textContent += text.charAt(index);
//                         index++;
//                     } else {
//                         clearInterval(typeInterval);
//                         console.log('🔊 AUDIO SYNC: Typewriter completed');
//                         resolve();
//                     }
//                 }, charDelay);
//             };
            
//             // Set up audio event listeners
//             audioElement.addEventListener('play', startTypewriter);
//             audioElement.addEventListener('ended', () => {
//                 if (index < text.length) {
//                     // If audio ends before typewriter, speed up
//                     console.log('🔊 Audio ended, completing typewriter...');
//                     element.textContent = text;
//                     resolve();
//                 }
//             });
            
//             audioElement.addEventListener('error', () => {
//                 console.error('🔊 Audio error, falling back to text-only');
//                 createTextOnlyTypewriter(element, text).then(resolve);
//             });
//         });
//     }
    
//     /**
//      * Main typewriter function - WITH AUDIO SUPPORT
//      */
//     function startTypewriter(element, text, audioElement = null, duration = null, options = {}) {
//         if (!element || !text) {
//             console.error('📝 Invalid element or text');
//             return Promise.resolve();
//         }
        
//         element.textContent = '';
        
//         // If audio is provided and valid, use audio sync
//         if (audioElement && audioElement.src && duration > 0) {
//             console.log('🔊 Starting audio-synchronized typewriter');
//             return createAudioSyncTypewriter(element, text, audioElement, duration);
//         } else {
//             console.log('📝 Starting text-only typewriter (no audio)');
//             return createSmartTypewriter(element, text, duration, options);
//         }
//     }
    
//     /**
//      * Estimate natural reading duration
//      */
//     function estimateReadingDuration(text, wordsPerMinute = 150) {
//         if (!text || !text.trim()) {
//             return 2.0;
//         }
        
//         const wordCount = text.split(/\s+/).length;
//         const baseDuration = (wordCount / wordsPerMinute) * 60;
//         const withPauses = baseDuration * 1.2; // Add 20% for reading pauses
        
//         return Math.max(2.0, Math.min(withPauses, 20.0));
//     }
    
//     // Export to global scope
//     window.TypewriterSync = {
//         start: startTypewriter,
//         createTextOnly: createTextOnlyTypewriter,
//         createSmart: createSmartTypewriter,
//         createAudioSync: createAudioSyncTypewriter,
//         estimateDuration: estimateReadingDuration,
//         config: CONFIG
//     };
    
//     console.log('✅ Typewriter System Loaded - WITH AUDIO SUPPORT');
//     console.log('📋 Available methods:');
//     console.log('  - window.TypewriterSync.start(element, text, audioElement, duration)');
//     console.log('  - window.TypewriterSync.createTextOnly(element, text)');
//     console.log('  - window.TypewriterSync.createSmart(element, text, duration)');
//     console.log('  - window.TypewriterSync.createAudioSync(element, text, audio, duration)');
//     console.log('  - window.TypewriterSync.estimateDuration(text)');
    
// })();



/**
 * FIXED Typewriter System - WITH PROPER AUDIO SUPPORT
 * This version properly handles audio playback and text synchronization
 * Key fixes: Better audio event handling, proper timing, fallback mechanisms
 */

(function() {
    'use strict';
    
    console.log('📝 Fixed Typewriter System Loading - WITH AUDIO SUPPORT...');
    
    // Configuration
    const CONFIG = {
        standardSpeed: 50,          // milliseconds per character for standard typing
        fastSpeed: 30,              // milliseconds per character for fast typing
        minDuration: 1000,          // minimum duration in milliseconds
        maxDuration: 10000,         // maximum duration in milliseconds
        audioSyncBuffer: 0.9        // Use 90% of audio duration for typing
    };
    
    /**
     * Text-only typewriter - no audio synchronization
     */
    function createTextOnlyTypewriter(element, text, options = {}) {
        return new Promise((resolve) => {
            if (!element || !text) {
                console.error('📝 TEXT ONLY: Invalid element or text');
                resolve();
                return;
            }
            
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
            if (!element || !text) {
                console.error('📝 SMART: Invalid element or text');
                resolve();
                return;
            }
            
            element.textContent = '';
            let index = 0;
            
            if (!targetDuration || targetDuration <= 0) {
                targetDuration = Math.min(text.length * 60, CONFIG.maxDuration);
            }
            
            const charDelay = Math.max(CONFIG.fastSpeed, Math.min(CONFIG.standardSpeed, targetDuration / text.length));
            
            console.log(`📝 SMART: ${text.length} chars, ${targetDuration}ms duration, ${charDelay.toFixed(1)}ms per char`);
            
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
     * FIXED: Audio-synchronized typewriter with proper event handling
     */
    function createAudioSyncTypewriter(element, text, audioElement, audioDuration) {
        return new Promise((resolve) => {
            if (!element || !text || !audioElement) {
                console.error('🔊 AUDIO SYNC: Invalid parameters, falling back to text-only');
                createTextOnlyTypewriter(element, text).then(resolve);
                return;
            }
            
            element.textContent = '';
            let index = 0;
            let typeInterval = null;
            let audioStarted = false;
            let typingStarted = false;
            
            // Use 90% of audio duration to finish typing before audio ends
            const syncDuration = Math.max(1, audioDuration * CONFIG.audioSyncBuffer);
            const charDelay = Math.max(20, (syncDuration * 1000) / text.length);
            
            console.log(`🔊 AUDIO SYNC: ${text.length} chars, ${audioDuration}s audio, ${syncDuration}s sync, ${charDelay.toFixed(1)}ms per char`);
            
            // Start typewriter function
            const startTypewriter = () => {
                if (typingStarted) return;
                typingStarted = true;
                
                console.log('🔊 Starting synchronized typewriter');
                
                typeInterval = setInterval(() => {
                    if (index < text.length) {
                        element.textContent += text.charAt(index);
                        index++;
                    } else {
                        clearInterval(typeInterval);
                        typeInterval = null;
                        console.log('🔊 AUDIO SYNC: Typewriter completed');
                        resolve();
                    }
                }, charDelay);
            };
            
            // Cleanup function
            const cleanup = () => {
                if (typeInterval) {
                    clearInterval(typeInterval);
                    typeInterval = null;
                }
                // Remove all event listeners
                audioElement.removeEventListener('play', onAudioPlay);
                audioElement.removeEventListener('ended', onAudioEnded);
                audioElement.removeEventListener('error', onAudioError);
                audioElement.removeEventListener('pause', onAudioPause);
                audioElement.removeEventListener('canplay', onCanPlay);
            };
            
            // Event handlers
            const onAudioPlay = () => {
                console.log('🔊 Audio started playing');
                audioStarted = true;
                startTypewriter();
            };
            
            const onAudioEnded = () => {
                console.log('🔊 Audio ended');
                if (index < text.length) {
                    // If audio ends before typewriter, complete text immediately
                    element.textContent = text;
                    cleanup();
                    resolve();
                } else if (!typingStarted) {
                    // If typing never started, complete it now
                    element.textContent = text;
                    cleanup();
                    resolve();
                }
            };
            
            const onAudioError = (error) => {
                console.error('🔊 Audio error occurred:', error);
                cleanup();
                console.log('🔊 Falling back to text-only due to audio error');
                createTextOnlyTypewriter(element, text).then(resolve);
            };
            
            const onAudioPause = () => {
                console.log('🔊 Audio paused');
                // Don't stop typing when audio pauses
            };
            
            const onCanPlay = () => {
                console.log('🔊 Audio can play');
                // Audio is ready but hasn't started yet
            };
            
            // FIXED: Attach event listeners with proper error handling
            try {
                audioElement.addEventListener('play', onAudioPlay);
                audioElement.addEventListener('ended', onAudioEnded);
                audioElement.addEventListener('error', onAudioError);
                audioElement.addEventListener('pause', onAudioPause);
                audioElement.addEventListener('canplay', onCanPlay);
                
                // Fallback timeout in case audio never starts
                setTimeout(() => {
                    if (!audioStarted && !typingStarted) {
                        console.warn('🔊 Audio timeout - starting typewriter without audio');
                        startTypewriter();
                    }
                }, 3000); // 3 second timeout
                
                // Ultimate fallback - ensure completion
                setTimeout(() => {
                    if (index < text.length) {
                        console.warn('🔊 Ultimate timeout - completing typewriter');
                        element.textContent = text;
                        cleanup();
                        resolve();
                    }
                }, (audioDuration + 5) * 1000); // Audio duration + 5 second buffer
                
            } catch (error) {
                console.error('🔊 Error setting up audio listeners:', error);
                cleanup();
                createTextOnlyTypewriter(element, text).then(resolve);
            }
        });
    }
    
    /**
     * FIXED: Main typewriter function with improved audio support
     */
    function startTypewriter(element, text, audioElement = null, duration = null, options = {}) {
        if (!element || !text) {
            console.error('📝 MAIN: Invalid element or text');
            return Promise.resolve();
        }
        
        // Clear element immediately
        element.textContent = '';
        
        // If audio is provided and valid, use audio sync
        if (audioElement && audioElement.src && duration && duration > 0) {
            console.log('🔊 MAIN: Starting audio-synchronized typewriter');
            console.log(`🔊 Audio details: src=${audioElement.src.substring(0, 50)}..., duration=${duration}s`);
            
            // Check if audio is already loaded
            if (audioElement.readyState >= 3) { // HAVE_FUTURE_DATA or higher
                console.log('🔊 Audio already loaded, can start sync');
            } else {
                console.log('🔊 Audio not loaded yet, waiting...');
            }
            
            return createAudioSyncTypewriter(element, text, audioElement, duration);
        } else {
            console.log('📝 MAIN: Starting text-only typewriter (no valid audio)');
            if (audioElement) {
                console.log(`📝 Audio rejected - src: ${audioElement.src || 'none'}, duration: ${duration || 'none'}`);
            }
            return createSmartTypewriter(element, text, duration ? duration * 1000 : null, options);
        }
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
    
    /**
     * Test audio element validity
     */
    function isAudioValid(audioElement, duration) {
        if (!audioElement) {
            console.log('🔊 No audio element provided');
            return false;
        }
        
        if (!audioElement.src || audioElement.src.trim() === '' || audioElement.src === 'none') {
            console.log('🔊 Invalid audio src:', audioElement.src);
            return false;
        }
        
        if (!duration || duration <= 0 || isNaN(duration)) {
            console.log('🔊 Invalid duration:', duration);
            return false;
        }
        
        console.log('🔊 Audio validation passed');
        return true;
    }
    
    // Export to global scope with enhanced functionality
    window.TypewriterSync = {
        start: startTypewriter,
        createTextOnly: createTextOnlyTypewriter,
        createSmart: createSmartTypewriter,
        createAudioSync: createAudioSyncTypewriter,
        estimateDuration: estimateReadingDuration,
        isAudioValid: isAudioValid,
        config: CONFIG,
        
        // Utility function for debugging
        debug: {
            logAudioState: function(audioElement) {
                if (!audioElement) {
                    console.log('🔊 DEBUG: No audio element');
                    return;
                }
                
                console.log('🔊 DEBUG: Audio State:');
                console.log('  - src:', audioElement.src || 'none');
                console.log('  - readyState:', audioElement.readyState);
                console.log('  - paused:', audioElement.paused);
                console.log('  - ended:', audioElement.ended);
                console.log('  - duration:', audioElement.duration || 'unknown');
                console.log('  - currentTime:', audioElement.currentTime);
                console.log('  - volume:', audioElement.volume);
                console.log('  - error:', audioElement.error);
            }
        }
    };
    
    console.log('✅ Fixed Typewriter System Loaded - WITH AUDIO SUPPORT');
    console.log('📋 Available methods:');
    console.log('  - window.TypewriterSync.start(element, text, audioElement, duration)');
    console.log('  - window.TypewriterSync.createTextOnly(element, text)');
    console.log('  - window.TypewriterSync.createSmart(element, text, duration)');
    console.log('  - window.TypewriterSync.createAudioSync(element, text, audio, duration)');
    console.log('  - window.TypewriterSync.estimateDuration(text)');
    console.log('  - window.TypewriterSync.isAudioValid(audio, duration)');
    console.log('  - window.TypewriterSync.debug.logAudioState(audio)');
    
})();