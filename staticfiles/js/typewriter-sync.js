/**
 * IMPROVED Typewriter System - WITH ENHANCED AUDIO SUPPORT
 * This version provides better audio synchronization and fallback handling
 * Key improvements: More reliable audio event handling, better error recovery
 */

(function() {
    'use strict';
    
    console.log('📝 Improved Typewriter System Loading - WITH ENHANCED AUDIO SUPPORT...');
    
    // Configuration
    const CONFIG = {
        standardSpeed: 45,          // milliseconds per character for standard typing
        fastSpeed: 25,              // milliseconds per character for fast typing
        minDuration: 1000,          // minimum duration in milliseconds
        maxDuration: 12000,         // maximum duration in milliseconds
        audioSyncBuffer: 0.95       // Use 95% of audio duration for typing
    };
    
    /**
     * Enhanced text-only typewriter
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
                targetDuration = Math.min(text.length * 50, CONFIG.maxDuration);
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
     * IMPROVED: Audio-synchronized typewriter with enhanced reliability
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
            let isCompleted = false;
            
            // Enhanced sync duration calculation
            const syncDuration = Math.max(1, audioDuration * CONFIG.audioSyncBuffer);
            const charDelay = Math.max(20, (syncDuration * 1000) / text.length);
            
            console.log(`🔊 ENHANCED AUDIO SYNC: ${text.length} chars, ${audioDuration}s audio, ${syncDuration}s sync, ${charDelay.toFixed(1)}ms per char`);
            
            // Completion function
            const completeTypewriter = (reason = 'completed') => {
                if (isCompleted) return;
                isCompleted = true;
                
                console.log(`🔊 Completing typewriter: ${reason}`);
                
                if (typeInterval) {
                    clearInterval(typeInterval);
                    typeInterval = null;
                }
                
                // Ensure full text is shown
                if (element.textContent !== text) {
                    element.textContent = text;
                }
                
                cleanup();
                resolve();
            };
            
            // Start typewriter function
            const startTypewriter = () => {
                if (typingStarted || isCompleted) return;
                typingStarted = true;
                
                console.log('🔊 Starting enhanced synchronized typewriter');
                
                typeInterval = setInterval(() => {
                    if (isCompleted) return;
                    
                    if (index < text.length) {
                        element.textContent += text.charAt(index);
                        index++;
                    } else {
                        completeTypewriter('typing finished');
                    }
                }, charDelay);
            };
            
            // Cleanup function
            const cleanup = () => {
                try {
                    audioElement.removeEventListener('play', onAudioPlay);
                    audioElement.removeEventListener('ended', onAudioEnded);
                    audioElement.removeEventListener('error', onAudioError);
                    audioElement.removeEventListener('pause', onAudioPause);
                    audioElement.removeEventListener('canplay', onCanPlay);
                    audioElement.removeEventListener('loadeddata', onLoadedData);
                } catch (e) {
                    console.warn('🔊 Cleanup warning:', e.message);
                }
            };
            
            // Enhanced event handlers
            const onAudioPlay = () => {
                console.log('🔊 Audio play event detected');
                audioStarted = true;
                startTypewriter();
            };
            
            const onAudioEnded = () => {
                console.log('🔊 Audio ended event detected');
                if (!isCompleted) {
                    completeTypewriter('audio ended');
                }
            };
            
            const onAudioError = (error) => {
                console.error('🔊 Audio error event:', error);
                if (!isCompleted) {
                    console.log('🔊 Falling back to text-only due to audio error');
                    cleanup();
                    createTextOnlyTypewriter(element, text).then(resolve);
                }
            };
            
            const onAudioPause = () => {
                console.log('🔊 Audio paused - continuing typewriter');
                // Continue typing even if audio pauses
            };
            
            const onCanPlay = () => {
                console.log('🔊 Audio can play event');
            };
            
            const onLoadedData = () => {
                console.log('🔊 Audio data loaded event');
            };
            
            // Enhanced audio state detection
            const checkAudioState = () => {
                if (isCompleted) return;
                
                try {
                    console.log(`🔊 Audio state check: readyState=${audioElement.readyState}, paused=${audioElement.paused}, ended=${audioElement.ended}, currentTime=${audioElement.currentTime}`);
                    
                    // If audio is already playing, start immediately
                    if (!audioElement.paused && audioElement.currentTime > 0 && !audioElement.ended) {
                        console.log('🔊 Audio already playing, starting typewriter');
                        audioStarted = true;
                        startTypewriter();
                        return true;
                    }
                } catch (e) {
                    console.warn('🔊 Audio state check error:', e.message);
                }
                return false;
            };
            
            try {
                // Attach all event listeners
                audioElement.addEventListener('play', onAudioPlay);
                audioElement.addEventListener('ended', onAudioEnded);
                audioElement.addEventListener('error', onAudioError);
                audioElement.addEventListener('pause', onAudioPause);
                audioElement.addEventListener('canplay', onCanPlay);
                audioElement.addEventListener('loadeddata', onLoadedData);
                
                // Check if audio is already in a ready/playing state
                if (checkAudioState()) {
                    // Audio already detected as playing
                } else {
                    // Set up fallback timers
                    
                    // Primary fallback - start typing if audio doesn't start soon
                    setTimeout(() => {
                        if (!audioStarted && !typingStarted && !isCompleted) {
                            console.warn('🔊 Primary timeout - starting typewriter without audio sync');
                            startTypewriter();
                        }
                    }, 2000); // 2 second timeout
                    
                    // Secondary fallback - ensure completion
                    setTimeout(() => {
                        if (!isCompleted) {
                            console.warn('🔊 Secondary timeout - force completing typewriter');
                            completeTypewriter('timeout fallback');
                        }
                    }, (audioDuration + 3) * 1000); // Audio duration + 3 second buffer
                    
                    // Ultimate safety net
                    setTimeout(() => {
                        if (!isCompleted) {
                            console.warn('🔊 Ultimate safety net - force completion');
                            completeTypewriter('safety net');
                        }
                    }, Math.max(10000, (audioDuration + 5) * 1000)); // At least 10s or audio + 5s
                }
                
            } catch (error) {
                console.error('🔊 Error setting up enhanced audio sync:', error);
                cleanup();
                createTextOnlyTypewriter(element, text).then(resolve);
            }
        });
    }
    
    /**
     * IMPROVED: Main typewriter function with enhanced audio support
     */
    function startTypewriter(element, text, audioElement = null, duration = null, options = {}) {
        if (!element || !text) {
            console.error('📝 MAIN: Invalid element or text');
            return Promise.resolve();
        }
        
        // Clear element immediately
        element.textContent = '';
        
        // Enhanced audio validation
        if (audioElement && isAudioValid(audioElement, duration)) {
            console.log('🔊 MAIN: Starting enhanced audio-synchronized typewriter');
            console.log(`🔊 Audio details: src=${audioElement.src ? audioElement.src.substring(0, 50) + '...' : 'none'}, duration=${duration}s`);
            
            // Additional debugging
            if (window.TypewriterSync && window.TypewriterSync.debug) {
                window.TypewriterSync.debug.logAudioState(audioElement);
            }
            
            return createAudioSyncTypewriter(element, text, audioElement, duration);
        } else {
            console.log('📝 MAIN: Starting smart text-only typewriter (no valid audio)');
            if (audioElement) {
                console.log(`📝 Audio validation failed - src: ${audioElement.src || 'none'}, duration: ${duration || 'none'}`);
            }
            return createSmartTypewriter(element, text, duration ? duration * 1000 : null, options);
        }
    }
    
    /**
     * Enhanced audio validation
     */
    function isAudioValid(audioElement, duration) {
        if (!audioElement) {
            console.log('🔊 VALIDATION: No audio element provided');
            return false;
        }
        
        if (!audioElement.src || audioElement.src.trim() === '' || audioElement.src.toLowerCase().includes('none')) {
            console.log('🔊 VALIDATION: Invalid audio src:', audioElement.src);
            return false;
        }
        
        if (!duration || duration <= 0 || isNaN(duration)) {
            console.log('🔊 VALIDATION: Invalid duration:', duration);
            return false;
        }
        
        // Additional checks
        try {
            // Check if element is properly attached to DOM
            if (!audioElement.parentNode && !document.contains(audioElement)) {
                console.log('🔊 VALIDATION: Audio element not in DOM');
                return false;
            }
        } catch (e) {
            console.warn('🔊 VALIDATION: DOM check failed:', e.message);
        }
        
        console.log('🔊 VALIDATION: Audio validation passed');
        return true;
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
        const withPauses = baseDuration * 1.3; // Add 30% for natural pauses
        
        return Math.max(2.0, Math.min(withPauses, 25.0));
    }
    
    // Export enhanced functionality to global scope
    window.TypewriterSync = {
        start: startTypewriter,
        createTextOnly: createTextOnlyTypewriter,
        createSmart: createSmartTypewriter,
        createAudioSync: createAudioSyncTypewriter,
        estimateDuration: estimateReadingDuration,
        isAudioValid: isAudioValid,
        config: CONFIG,
        
        // Enhanced debugging utilities
        debug: {
            logAudioState: function(audioElement) {
                if (!audioElement) {
                    console.log('🔊 DEBUG: No audio element');
                    return;
                }
                
                console.log('🔊 DEBUG: Enhanced Audio State Analysis:');
                console.log('  - src:', audioElement.src || 'none');
                console.log('  - readyState:', audioElement.readyState, '(0=HAVE_NOTHING, 1=HAVE_METADATA, 2=HAVE_CURRENT_DATA, 3=HAVE_FUTURE_DATA, 4=HAVE_ENOUGH_DATA)');
                console.log('  - networkState:', audioElement.networkState, '(0=EMPTY, 1=IDLE, 2=LOADING, 3=NO_SOURCE)');
                console.log('  - paused:', audioElement.paused);
                console.log('  - ended:', audioElement.ended);
                console.log('  - duration:', audioElement.duration || 'unknown');
                console.log('  - currentTime:', audioElement.currentTime);
                console.log('  - volume:', audioElement.volume);
                console.log('  - muted:', audioElement.muted);
                console.log('  - error:', audioElement.error);
                console.log('  - seeking:', audioElement.seeking);
                console.log('  - played ranges:', audioElement.played.length);
                console.log('  - buffered ranges:', audioElement.buffered.length);
                
                // Check if element is in DOM
                try {
                    console.log('  - inDOM:', document.contains(audioElement));
                    console.log('  - parentNode:', !!audioElement.parentNode);
                } catch (e) {
                    console.log('  - DOM check failed:', e.message);
                }
            },
            
            testAudioPlayback: function(audioElement) {
                if (!audioElement) {
                    console.log('🔊 TEST: No audio element provided');
                    return;
                }
                
                console.log('🔊 TEST: Starting audio playback test...');
                this.logAudioState(audioElement);
                
                audioElement.play().then(() => {
                    console.log('🔊 TEST: Audio playback started successfully');
                }).catch(error => {
                    console.error('🔊 TEST: Audio playback failed:', error);
                });
            }
        }
    };
    
    console.log('✅ Enhanced Typewriter System Loaded - WITH IMPROVED AUDIO SUPPORT');
    console.log('📋 Available methods:');
    console.log('  - window.TypewriterSync.start(element, text, audioElement, duration)');
    console.log('  - window.TypewriterSync.createTextOnly(element, text, options)');
    console.log('  - window.TypewriterSync.createSmart(element, text, duration, options)');
    console.log('  - window.TypewriterSync.createAudioSync(element, text, audio, duration)');
    console.log('  - window.TypewriterSync.estimateDuration(text, wpm)');
    console.log('  - window.TypewriterSync.isAudioValid(audio, duration)');
    console.log('  - window.TypewriterSync.debug.logAudioState(audio)');
    console.log('  - window.TypewriterSync.debug.testAudioPlayback(audio)');
    
})();



// /**
//  * FIXED Typewriter System - WITH PROPER AUDIO SUPPORT
//  * This version properly handles audio playback and text synchronization
//  * Key fixes: Better audio event handling, proper timing, fallback mechanisms
//  */

// (function() {
//     'use strict';
    
//     console.log('📝 Fixed Typewriter System Loading - WITH AUDIO SUPPORT...');
    
//     // Configuration
//     const CONFIG = {
//         standardSpeed: 50,          // milliseconds per character for standard typing
//         fastSpeed: 30,              // milliseconds per character for fast typing
//         minDuration: 1000,          // minimum duration in milliseconds
//         maxDuration: 10000,         // maximum duration in milliseconds
//         audioSyncBuffer: 0.9        // Use 90% of audio duration for typing
//     };
    
//     /**
//      * Text-only typewriter - no audio synchronization
//      */
//     function createTextOnlyTypewriter(element, text, options = {}) {
//         return new Promise((resolve) => {
//             if (!element || !text) {
//                 console.error('📝 TEXT ONLY: Invalid element or text');
//                 resolve();
//                 return;
//             }
            
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
//             if (!element || !text) {
//                 console.error('📝 SMART: Invalid element or text');
//                 resolve();
//                 return;
//             }
            
//             element.textContent = '';
//             let index = 0;
            
//             if (!targetDuration || targetDuration <= 0) {
//                 targetDuration = Math.min(text.length * 60, CONFIG.maxDuration);
//             }
            
//             const charDelay = Math.max(CONFIG.fastSpeed, Math.min(CONFIG.standardSpeed, targetDuration / text.length));
            
//             console.log(`📝 SMART: ${text.length} chars, ${targetDuration}ms duration, ${charDelay.toFixed(1)}ms per char`);
            
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
//      * FIXED: Audio-synchronized typewriter with proper event handling
//      */
//     function createAudioSyncTypewriter(element, text, audioElement, audioDuration) {
//         return new Promise((resolve) => {
//             if (!element || !text || !audioElement) {
//                 console.error('🔊 AUDIO SYNC: Invalid parameters, falling back to text-only');
//                 createTextOnlyTypewriter(element, text).then(resolve);
//                 return;
//             }
            
//             element.textContent = '';
//             let index = 0;
//             let typeInterval = null;
//             let audioStarted = false;
//             let typingStarted = false;
            
//             // Use 90% of audio duration to finish typing before audio ends
//             const syncDuration = Math.max(1, audioDuration * CONFIG.audioSyncBuffer);
//             const charDelay = Math.max(20, (syncDuration * 1000) / text.length);
            
//             console.log(`🔊 AUDIO SYNC: ${text.length} chars, ${audioDuration}s audio, ${syncDuration}s sync, ${charDelay.toFixed(1)}ms per char`);
            
//             // Start typewriter function
//             const startTypewriter = () => {
//                 if (typingStarted) return;
//                 typingStarted = true;
                
//                 console.log('🔊 Starting synchronized typewriter');
                
//                 typeInterval = setInterval(() => {
//                     if (index < text.length) {
//                         element.textContent += text.charAt(index);
//                         index++;
//                     } else {
//                         clearInterval(typeInterval);
//                         typeInterval = null;
//                         console.log('🔊 AUDIO SYNC: Typewriter completed');
//                         resolve();
//                     }
//                 }, charDelay);
//             };
            
//             // Cleanup function
//             const cleanup = () => {
//                 if (typeInterval) {
//                     clearInterval(typeInterval);
//                     typeInterval = null;
//                 }
//                 // Remove all event listeners
//                 audioElement.removeEventListener('play', onAudioPlay);
//                 audioElement.removeEventListener('ended', onAudioEnded);
//                 audioElement.removeEventListener('error', onAudioError);
//                 audioElement.removeEventListener('pause', onAudioPause);
//                 audioElement.removeEventListener('canplay', onCanPlay);
//             };
            
//             // Event handlers
//             const onAudioPlay = () => {
//                 console.log('🔊 Audio started playing');
//                 audioStarted = true;
//                 startTypewriter();
//             };
            
//             const onAudioEnded = () => {
//                 console.log('🔊 Audio ended');
//                 if (index < text.length) {
//                     // If audio ends before typewriter, complete text immediately
//                     element.textContent = text;
//                     cleanup();
//                     resolve();
//                 } else if (!typingStarted) {
//                     // If typing never started, complete it now
//                     element.textContent = text;
//                     cleanup();
//                     resolve();
//                 }
//             };
            
//             const onAudioError = (error) => {
//                 console.error('🔊 Audio error occurred:', error);
//                 cleanup();
//                 console.log('🔊 Falling back to text-only due to audio error');
//                 createTextOnlyTypewriter(element, text).then(resolve);
//             };
            
//             const onAudioPause = () => {
//                 console.log('🔊 Audio paused');
//                 // Don't stop typing when audio pauses
//             };
            
//             const onCanPlay = () => {
//                 console.log('🔊 Audio can play');
//                 // Audio is ready but hasn't started yet
//             };
            
//             // FIXED: Attach event listeners with proper error handling
//             try {
//                 audioElement.addEventListener('play', onAudioPlay);
//                 audioElement.addEventListener('ended', onAudioEnded);
//                 audioElement.addEventListener('error', onAudioError);
//                 audioElement.addEventListener('pause', onAudioPause);
//                 audioElement.addEventListener('canplay', onCanPlay);
                
//                 // Fallback timeout in case audio never starts
//                 setTimeout(() => {
//                     if (!audioStarted && !typingStarted) {
//                         console.warn('🔊 Audio timeout - starting typewriter without audio');
//                         startTypewriter();
//                     }
//                 }, 3000); // 3 second timeout
                
//                 // Ultimate fallback - ensure completion
//                 setTimeout(() => {
//                     if (index < text.length) {
//                         console.warn('🔊 Ultimate timeout - completing typewriter');
//                         element.textContent = text;
//                         cleanup();
//                         resolve();
//                     }
//                 }, (audioDuration + 5) * 1000); // Audio duration + 5 second buffer
                
//             } catch (error) {
//                 console.error('🔊 Error setting up audio listeners:', error);
//                 cleanup();
//                 createTextOnlyTypewriter(element, text).then(resolve);
//             }
//         });
//     }
    
//     /**
//      * FIXED: Main typewriter function with improved audio support
//      */
//     function startTypewriter(element, text, audioElement = null, duration = null, options = {}) {
//         if (!element || !text) {
//             console.error('📝 MAIN: Invalid element or text');
//             return Promise.resolve();
//         }
        
//         // Clear element immediately
//         element.textContent = '';
        
//         // If audio is provided and valid, use audio sync
//         if (audioElement && audioElement.src && duration && duration > 0) {
//             console.log('🔊 MAIN: Starting audio-synchronized typewriter');
//             console.log(`🔊 Audio details: src=${audioElement.src.substring(0, 50)}..., duration=${duration}s`);
            
//             // Check if audio is already loaded
//             if (audioElement.readyState >= 3) { // HAVE_FUTURE_DATA or higher
//                 console.log('🔊 Audio already loaded, can start sync');
//             } else {
//                 console.log('🔊 Audio not loaded yet, waiting...');
//             }
            
//             return createAudioSyncTypewriter(element, text, audioElement, duration);
//         } else {
//             console.log('📝 MAIN: Starting text-only typewriter (no valid audio)');
//             if (audioElement) {
//                 console.log(`📝 Audio rejected - src: ${audioElement.src || 'none'}, duration: ${duration || 'none'}`);
//             }
//             return createSmartTypewriter(element, text, duration ? duration * 1000 : null, options);
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
    
//     /**
//      * Test audio element validity
//      */
//     function isAudioValid(audioElement, duration) {
//         if (!audioElement) {
//             console.log('🔊 No audio element provided');
//             return false;
//         }
        
//         if (!audioElement.src || audioElement.src.trim() === '' || audioElement.src === 'none') {
//             console.log('🔊 Invalid audio src:', audioElement.src);
//             return false;
//         }
        
//         if (!duration || duration <= 0 || isNaN(duration)) {
//             console.log('🔊 Invalid duration:', duration);
//             return false;
//         }
        
//         console.log('🔊 Audio validation passed');
//         return true;
//     }
    
//     // Export to global scope with enhanced functionality
//     window.TypewriterSync = {
//         start: startTypewriter,
//         createTextOnly: createTextOnlyTypewriter,
//         createSmart: createSmartTypewriter,
//         createAudioSync: createAudioSyncTypewriter,
//         estimateDuration: estimateReadingDuration,
//         isAudioValid: isAudioValid,
//         config: CONFIG,
        
//         // Utility function for debugging
//         debug: {
//             logAudioState: function(audioElement) {
//                 if (!audioElement) {
//                     console.log('🔊 DEBUG: No audio element');
//                     return;
//                 }
                
//                 console.log('🔊 DEBUG: Audio State:');
//                 console.log('  - src:', audioElement.src || 'none');
//                 console.log('  - readyState:', audioElement.readyState);
//                 console.log('  - paused:', audioElement.paused);
//                 console.log('  - ended:', audioElement.ended);
//                 console.log('  - duration:', audioElement.duration || 'unknown');
//                 console.log('  - currentTime:', audioElement.currentTime);
//                 console.log('  - volume:', audioElement.volume);
//                 console.log('  - error:', audioElement.error);
//             }
//         }
//     };
    
//     console.log('✅ Fixed Typewriter System Loaded - WITH AUDIO SUPPORT');
//     console.log('📋 Available methods:');
//     console.log('  - window.TypewriterSync.start(element, text, audioElement, duration)');
//     console.log('  - window.TypewriterSync.createTextOnly(element, text)');
//     console.log('  - window.TypewriterSync.createSmart(element, text, duration)');
//     console.log('  - window.TypewriterSync.createAudioSync(element, text, audio, duration)');
//     console.log('  - window.TypewriterSync.estimateDuration(text)');
//     console.log('  - window.TypewriterSync.isAudioValid(audio, duration)');
//     console.log('  - window.TypewriterSync.debug.logAudioState(audio)');
    
// })();