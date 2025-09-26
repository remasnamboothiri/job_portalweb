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


/**
 * COMPLETE FIXED Typewriter System - WITH FULL AUDIO SUPPORT
 * This version properly handles all audio scenarios and text synchronization
 * Key fixes: Proper event handling, fallback mechanisms, complete debugging
 */

(function() {
    'use strict';
    
    console.log('📝 COMPLETE Fixed Typewriter System Loading - WITH FULL AUDIO SUPPORT...');
    
    // Configuration
    const CONFIG = {
        standardSpeed: 50,          // milliseconds per character for standard typing
        fastSpeed: 30,              // milliseconds per character for fast typing
        slowSpeed: 80,              // milliseconds per character for slow typing
        minDuration: 1000,          // minimum duration in milliseconds
        maxDuration: 15000,         // maximum duration in milliseconds
        audioSyncBuffer: 0.85       // Use 85% of audio duration for typing to finish before audio
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
            
            const speed = options.fast ? CONFIG.fastSpeed : 
                         options.slow ? CONFIG.slowSpeed : CONFIG.standardSpeed;
            
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
     * Smart duration typewriter - adjusts speed based on content length and target duration
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
            
            // Calculate optimal duration if not provided
            if (!targetDuration || targetDuration <= 0) {
                // Base duration on text length with reasonable bounds
                targetDuration = Math.max(CONFIG.minDuration, Math.min(text.length * 60, CONFIG.maxDuration));
            }
            
            const charDelay = Math.max(CONFIG.fastSpeed, Math.min(CONFIG.slowSpeed, targetDuration / text.length));
            
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
     * COMPLETE FIXED: Audio-synchronized typewriter with comprehensive error handling
     */
    function createAudioSyncTypewriter(element, text, audioElement, audioDuration) {
        return new Promise((resolve) => {
            if (!element || !text) {
                console.error('🔊 AUDIO SYNC: Invalid element or text, falling back to text-only');
                createTextOnlyTypewriter(element, text).then(resolve);
                return;
            }
            
            if (!audioElement || !audioElement.src || !audioDuration || audioDuration <= 0) {
                console.error('🔊 AUDIO SYNC: Invalid audio parameters, falling back to smart typewriter');
                createSmartTypewriter(element, text, null).then(resolve);
                return;
            }
            
            element.textContent = '';
            let index = 0;
            let typeInterval = null;
            let audioStarted = false;
            let typingStarted = false;
            let completed = false;
            
            // Use buffer percentage of audio duration to finish typing before audio ends
            const syncDuration = Math.max(1, audioDuration * CONFIG.audioSyncBuffer);
            const charDelay = Math.max(20, (syncDuration * 1000) / text.length);
            
            console.log(`🔊 AUDIO SYNC: ${text.length} chars, ${audioDuration}s audio, ${syncDuration}s sync, ${charDelay.toFixed(1)}ms per char`);
            
            // Complete function to prevent multiple resolutions
            const complete = () => {
                if (completed) return;
                completed = true;
                
                cleanup();
                resolve();
            };
            
            // Start typewriter function
            const startTypewriter = () => {
                if (typingStarted || completed) return;
                typingStarted = true;
                
                console.log('🔊 Starting synchronized typewriter');
                
                typeInterval = setInterval(() => {
                    if (index < text.length && !completed) {
                        element.textContent += text.charAt(index);
                        index++;
                    } else {
                        clearInterval(typeInterval);
                        typeInterval = null;
                        console.log('🔊 AUDIO SYNC: Typewriter completed');
                        complete();
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
                try {
                    audioElement.removeEventListener('play', onAudioPlay);
                    audioElement.removeEventListener('playing', onAudioPlaying);
                    audioElement.removeEventListener('ended', onAudioEnded);
                    audioElement.removeEventListener('error', onAudioError);
                    audioElement.removeEventListener('pause', onAudioPause);
                    audioElement.removeEventListener('canplay', onCanPlay);
                    audioElement.removeEventListener('loadstart', onLoadStart);
                    audioElement.removeEventListener('loadeddata', onLoadedData);
                } catch (e) {
                    console.warn('🔊 Error removing event listeners:', e);
                }
            };
            
            // Event handlers
            const onAudioPlay = () => {
                console.log('🔊 Audio play event fired');
                if (!audioStarted) {
                    audioStarted = true;
                    startTypewriter();
                }
            };
            
            const onAudioPlaying = () => {
                console.log('🔊 Audio actually playing');
                if (!audioStarted) {
                    audioStarted = true;
                    startTypewriter();
                }
            };
            
            const onAudioEnded = () => {
                console.log('🔊 Audio ended');
                if (index < text.length && !completed) {
                    // If audio ends before typewriter, complete text immediately
                    element.textContent = text;
                    console.log('🔊 Audio ended early - completing text');
                }
                complete();
            };
            
            const onAudioError = (event) => {
                console.error('🔊 Audio error occurred:', event.target.error);
                cleanup();
                console.log('🔊 Falling back to text-only due to audio error');
                if (!completed) {
                    createTextOnlyTypewriter(element, text).then(resolve);
                }
            };
            
            const onAudioPause = () => {
                console.log('🔊 Audio paused - continuing typewriter');
                // Don't stop typing when audio pauses, but ensure typing started
                if (!typingStarted && !completed) {
                    startTypewriter();
                }
            };
            
            const onCanPlay = () => {
                console.log('🔊 Audio can play');
            };
            
            const onLoadStart = () => {
                console.log('🔊 Audio load started');
            };
            
            const onLoadedData = () => {
                console.log('🔊 Audio data loaded');
            };
            
            // FIXED: Attach comprehensive event listeners
            try {
                audioElement.addEventListener('play', onAudioPlay);
                audioElement.addEventListener('playing', onAudioPlaying);
                audioElement.addEventListener('ended', onAudioEnded);
                audioElement.addEventListener('error', onAudioError);
                audioElement.addEventListener('pause', onAudioPause);
                audioElement.addEventListener('canplay', onCanPlay);
                audioElement.addEventListener('loadstart', onLoadStart);
                audioElement.addEventListener('loadeddata', onLoadedData);
                
                // Fallback timeout in case audio never starts
                setTimeout(() => {
                    if (!audioStarted && !typingStarted && !completed) {
                        console.warn('🔊 Audio start timeout - starting typewriter without audio sync');
                        startTypewriter();
                    }
                }, 3000);
                
                // Ultimate fallback - ensure completion
                setTimeout(() => {
                    if (!completed) {
                        console.warn('🔊 Ultimate timeout - completing typewriter forcefully');
                        if (index < text.length) {
                            element.textContent = text;
                        }
                        complete();
                    }
                }, (audioDuration + 10) * 1000); // Audio duration + 10 second buffer
                
            } catch (error) {
                console.error('🔊 Error setting up audio listeners:', error);
                cleanup();
                if (!completed) {
                    createTextOnlyTypewriter(element, text).then(resolve);
                }
            }
        });
    }
    
    /**
     * COMPLETE FIXED: Main typewriter function with full audio support and fallbacks
     */
    function startTypewriter(element, text, audioElement = null, duration = null, options = {}) {
        if (!element) {
            console.error('📝 MAIN: Invalid element provided');
            return Promise.resolve();
        }
        
        if (!text || typeof text !== 'string' || text.trim().length === 0) {
            console.error('📝 MAIN: Invalid text provided');
            element.textContent = 'Loading...';
            return Promise.resolve();
        }
        
        // Clear element immediately
        element.textContent = '';
        
        console.log('📝 MAIN: Starting typewriter system');
        console.log(`📝 Text: "${text.substring(0, 100)}${text.length > 100 ? '...' : ''}" (${text.length} chars)`);
        
        // Validate audio parameters
        const audioValid = isAudioElementValid(audioElement, duration);
        
        if (audioValid) {
            console.log('🔊 MAIN: Using audio-synchronized typewriter');
            console.log(`🔊 Audio: ${audioElement.src.substring(0, 50)}..., Duration: ${duration}s`);
            
            // Log audio element state
            logAudioElementState(audioElement);
            
            return createAudioSyncTypewriter(element, text, audioElement, duration);
        } else {
            console.log('📝 MAIN: Using smart typewriter (no valid audio)');
            
            if (audioElement) {
                console.log(`📝 Audio rejected: src="${audioElement.src || 'none'}", duration=${duration}`);
            }
            
            // Use duration if provided for smart typewriter
            const targetDuration = duration && duration > 0 ? duration * 1000 : null;
            return createSmartTypewriter(element, text, targetDuration, options);
        }
    }
    
    /**
     * Estimate natural reading duration based on text content
     */
    function estimateReadingDuration(text, wordsPerMinute = 150) {
        if (!text || typeof text !== 'string' || text.trim().length === 0) {
            return 3.0;
        }
        
        const wordCount = text.split(/\s+/).length;
        const baseDuration = (wordCount / wordsPerMinute) * 60;
        const withPauses = baseDuration * 1.3; // Add 30% for natural pauses
        
        // Ensure reasonable bounds
        return Math.max(2.0, Math.min(withPauses, 25.0));
    }
    
    /**
     * COMPLETE: Validate audio element and duration
     */
    function isAudioElementValid(audioElement, duration) {
        if (!audioElement) {
            console.log('🔊 VALIDATION: No audio element provided');
            return false;
        }
        
        if (!audioElement.src || typeof audioElement.src !== 'string') {
            console.log('🔊 VALIDATION: Invalid or missing audio src');
            return false;
        }
        
        const src = audioElement.src.trim();
        if (src === '' || src === 'none' || src === 'null' || src === 'undefined') {
            console.log('🔊 VALIDATION: Empty or placeholder audio src:', src);
            return false;
        }
        
        if (!duration || typeof duration !== 'number' || duration <= 0 || isNaN(duration)) {
            console.log('🔊 VALIDATION: Invalid duration:', duration);
            return false;
        }
        
        if (duration > 300) { // 5 minutes seems like a reasonable upper bound
            console.log('🔊 VALIDATION: Duration too long:', duration);
            return false;
        }
        
        console.log('🔊 VALIDATION: Audio validation passed');
        return true;
    }
    
    /**
     * Log comprehensive audio element state for debugging
     */
    function logAudioElementState(audioElement) {
        if (!audioElement) {
            console.log('🔊 AUDIO STATE: No audio element');
            return;
        }
        
        console.log('🔊 AUDIO STATE: Comprehensive audio element state:');
        console.log('  - src:', audioElement.src || 'none');
        console.log('  - readyState:', audioElement.readyState, getReadyStateText(audioElement.readyState));
        console.log('  - networkState:', audioElement.networkState, getNetworkStateText(audioElement.networkState));
        console.log('  - paused:', audioElement.paused);
        console.log('  - ended:', audioElement.ended);
        console.log('  - duration:', audioElement.duration || 'unknown');
        console.log('  - currentTime:', audioElement.currentTime);
        console.log('  - volume:', audioElement.volume);
        console.log('  - muted:', audioElement.muted);
        console.log('  - error:', audioElement.error ? audioElement.error.message : 'none');
        console.log('  - preload:', audioElement.preload);
        console.log('  - autoplay:', audioElement.autoplay);
    }
    
    function getReadyStateText(readyState) {
        const states = {
            0: 'HAVE_NOTHING',
            1: 'HAVE_METADATA',
            2: 'HAVE_CURRENT_DATA',
            3: 'HAVE_FUTURE_DATA',
            4: 'HAVE_ENOUGH_DATA'
        };
        return states[readyState] || 'UNKNOWN';
    }
    
    function getNetworkStateText(networkState) {
        const states = {
            0: 'NETWORK_EMPTY',
            1: 'NETWORK_IDLE',
            2: 'NETWORK_LOADING',
            3: 'NETWORK_NO_SOURCE'
        };
        return states[networkState] || 'UNKNOWN';
    }
    
    /**
     * Test function to validate typewriter functionality
     */
    function runDiagnostics(audioElement = null, duration = null) {
        console.log('🔧 DIAGNOSTICS: Running typewriter system diagnostics...');
        
        // Test 1: Basic text-only typewriter
        console.log('🔧 TEST 1: Text-only typewriter');
        const testElement1 = document.createElement('div');
        document.body.appendChild(testElement1);
        
        createTextOnlyTypewriter(testElement1, 'Test message', { fast: true }).then(() => {
            console.log('🔧 TEST 1: PASSED');
            document.body.removeChild(testElement1);
        }).catch(error => {
            console.error('🔧 TEST 1: FAILED', error);
            document.body.removeChild(testElement1);
        });
        
        // Test 2: Smart typewriter
        console.log('🔧 TEST 2: Smart typewriter');
        const testElement2 = document.createElement('div');
        document.body.appendChild(testElement2);
        
        createSmartTypewriter(testElement2, 'Test message for smart typewriter', 2000).then(() => {
            console.log('🔧 TEST 2: PASSED');
            document.body.removeChild(testElement2);
        }).catch(error => {
            console.error('🔧 TEST 2: FAILED', error);
            document.body.removeChild(testElement2);
        });
        
        // Test 3: Audio validation
        console.log('🔧 TEST 3: Audio validation');
        if (audioElement && duration) {
            const isValid = isAudioElementValid(audioElement, duration);
            console.log(`🔧 TEST 3: Audio validation result: ${isValid ? 'VALID' : 'INVALID'}`);
            if (isValid) {
                logAudioElementState(audioElement);
            }
        } else {
            console.log('🔧 TEST 3: No audio provided for testing');
        }
        
        console.log('🔧 DIAGNOSTICS: Complete');
    }
    
    // Export to global scope with comprehensive API
    window.TypewriterSync = {
        // Main functions
        start: startTypewriter,
        createTextOnly: createTextOnlyTypewriter,
        createSmart: createSmartTypewriter,
        createAudioSync: createAudioSyncTypewriter,
        
        // Utility functions
        estimateDuration: estimateReadingDuration,
        isAudioValid: isAudioElementValid,
        
        // Configuration
        config: CONFIG,
        
        // Debugging and diagnostics
        debug: {
            logAudioState: logAudioElementState,
            runDiagnostics: runDiagnostics,
            getReadyStateText: getReadyStateText,
            getNetworkStateText: getNetworkStateText
        },
        
        // Version info
        version: '2.0.0-complete-fixed'
    };
    
    console.log('✅ COMPLETE Fixed Typewriter System Loaded Successfully');
    console.log('📋 Available methods:');
    console.log('  - TypewriterSync.start(element, text, audioElement, duration, options)');
    console.log('  - TypewriterSync.createTextOnly(element, text, options)');
    console.log('  - TypewriterSync.createSmart(element, text, targetDuration, options)');
    console.log('  - TypewriterSync.createAudioSync(element, text, audioElement, duration)');
    console.log('  - TypewriterSync.estimateDuration(text, wordsPerMinute)');
    console.log('  - TypewriterSync.isAudioValid(audioElement, duration)');
    console.log('🔧 Debugging methods:');
    console.log('  - TypewriterSync.debug.logAudioState(audioElement)');
    console.log('  - TypewriterSync.debug.runDiagnostics(audioElement, duration)');
    console.log(`📦 Version: ${window.TypewriterSync.version}`);
    
})();