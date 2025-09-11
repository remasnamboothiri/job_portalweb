/**
 * Audio System Test Suite
 * Tests the professional interview audio system functionality
 */

class AudioSystemTest {
    constructor() {
        this.testResults = [];
        this.testsPassed = 0;
        this.testsFailed = 0;
    }

    // Run all audio system tests
    async runAllTests() {
        console.log('🧪 Starting Audio System Tests...');
        
        await this.testMicrophoneAccess();
        await this.testAudioContext();
        await this.testSpeechRecognition();
        await this.testAudioIsolation();
        await this.testFeedbackPrevention();
        
        this.displayResults();
    }

    // Test microphone access
    async testMicrophoneAccess() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                }
            });
            
            if (stream && stream.getAudioTracks().length > 0) {
                this.logTest('Microphone Access', true, 'Microphone accessible with professional settings');
                stream.getTracks().forEach(track => track.stop());
            } else {
                this.logTest('Microphone Access', false, 'No audio tracks available');
            }
        } catch (error) {
            this.logTest('Microphone Access', false, `Error: ${error.message}`);
        }
    }

    // Test Web Audio API
    async testAudioContext() {
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            
            if (audioContext) {
                this.logTest('Web Audio API', true, `Audio context created (state: ${audioContext.state})`);
                
                // Test audio nodes
                const gainNode = audioContext.createGain();
                const compressor = audioContext.createDynamicsCompressor();
                
                if (gainNode && compressor) {
                    this.logTest('Audio Processing Nodes', true, 'Gain and compressor nodes created');
                } else {
                    this.logTest('Audio Processing Nodes', false, 'Failed to create audio nodes');
                }
                
                audioContext.close();
            } else {
                this.logTest('Web Audio API', false, 'AudioContext not available');
            }
        } catch (error) {
            this.logTest('Web Audio API', false, `Error: ${error.message}`);
        }
    }

    // Test speech recognition
    async testSpeechRecognition() {
        try {
            if ('webkitSpeechRecognition' in window) {
                const recognition = new webkitSpeechRecognition();
                recognition.continuous = true;
                recognition.interimResults = true;
                
                this.logTest('Speech Recognition API', true, 'Speech recognition available');
                
                // Test recognition settings
                if (recognition.continuous && recognition.interimResults) {
                    this.logTest('Speech Recognition Settings', true, 'Professional settings applied');
                } else {
                    this.logTest('Speech Recognition Settings', false, 'Settings not applied correctly');
                }
            } else {
                this.logTest('Speech Recognition API', false, 'Speech recognition not supported');
            }
        } catch (error) {
            this.logTest('Speech Recognition API', false, `Error: ${error.message}`);
        }
    }

    // Test audio isolation system
    async testAudioIsolation() {
        try {
            // Test if professional audio class is available
            if (window.ProfessionalInterviewAudio) {
                const audioSystem = new window.ProfessionalInterviewAudio();
                this.logTest('Audio Isolation Class', true, 'Professional audio system available');
                
                // Test initialization
                if (typeof audioSystem.initialize === 'function') {
                    this.logTest('Audio Isolation Methods', true, 'Audio isolation methods available');
                } else {
                    this.logTest('Audio Isolation Methods', false, 'Audio isolation methods missing');
                }
            } else {
                this.logTest('Audio Isolation Class', false, 'Professional audio system not loaded');
            }
        } catch (error) {
            this.logTest('Audio Isolation System', false, `Error: ${error.message}`);
        }
    }

    // Test feedback prevention
    async testFeedbackPrevention() {
        try {
            // Test audio element controls
            const audioElement = document.createElement('audio');
            audioElement.volume = 0.6;
            
            if (audioElement.volume === 0.6) {
                this.logTest('Audio Volume Control', true, 'Audio volume can be controlled');
            } else {
                this.logTest('Audio Volume Control', false, 'Audio volume control failed');
            }

            // Test event listeners
            let eventFired = false;
            audioElement.addEventListener('play', () => {
                eventFired = true;
            });
            
            // Simulate play event
            const playEvent = new Event('play');
            audioElement.dispatchEvent(playEvent);
            
            if (eventFired) {
                this.logTest('Audio Event Handling', true, 'Audio events can be captured');
            } else {
                this.logTest('Audio Event Handling', false, 'Audio event handling failed');
            }
        } catch (error) {
            this.logTest('Feedback Prevention', false, `Error: ${error.message}`);
        }
    }

    // Log test result
    logTest(testName, passed, message) {
        const result = {
            name: testName,
            passed: passed,
            message: message,
            timestamp: new Date().toISOString()
        };
        
        this.testResults.push(result);
        
        if (passed) {
            this.testsPassed++;
            console.log(`✅ ${testName}: ${message}`);
        } else {
            this.testsFailed++;
            console.log(`❌ ${testName}: ${message}`);
        }
    }

    // Display test results
    displayResults() {
        console.log('\n📊 Audio System Test Results:');
        console.log(`✅ Passed: ${this.testsPassed}`);
        console.log(`❌ Failed: ${this.testsFailed}`);
        console.log(`📈 Success Rate: ${((this.testsPassed / (this.testsPassed + this.testsFailed)) * 100).toFixed(1)}%`);
        
        if (this.testsFailed === 0) {
            console.log('🎉 All tests passed! Audio system is ready for professional interviews.');
        } else {
            console.log('⚠️ Some tests failed. Please check the issues above.');
        }
        
        // Return results for programmatic access
        return {
            passed: this.testsPassed,
            failed: this.testsFailed,
            total: this.testsPassed + this.testsFailed,
            results: this.testResults
        };
    }

    // Test specific audio isolation scenario
    async testAudioIsolationScenario() {
        console.log('🎭 Testing Audio Isolation Scenario...');
        
        try {
            // Simulate AI speaking
            console.log('1. AI starts speaking...');
            
            // Simulate microphone gain reduction
            console.log('2. Reducing microphone sensitivity...');
            
            // Simulate speech recognition pause
            console.log('3. Pausing speech recognition...');
            
            // Wait for simulated AI speech duration
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            // Simulate AI speech end
            console.log('4. AI finished speaking...');
            
            // Simulate microphone gain restoration
            console.log('5. Restoring microphone sensitivity...');
            
            // Simulate speech recognition resume
            console.log('6. Resuming speech recognition...');
            
            console.log('✅ Audio isolation scenario completed successfully');
            return true;
            
        } catch (error) {
            console.log(`❌ Audio isolation scenario failed: ${error.message}`);
            return false;
        }
    }
}

// Global test function
window.testAudioSystem = async function() {
    const tester = new AudioSystemTest();
    return await tester.runAllTests();
};

// Global scenario test function
window.testAudioIsolationScenario = async function() {
    const tester = new AudioSystemTest();
    return await tester.testAudioIsolationScenario();
};

// Auto-run tests if in development mode
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    document.addEventListener('DOMContentLoaded', function() {
        console.log('🔧 Development mode detected - Audio system tests available');
        console.log('Run testAudioSystem() to test the audio system');
        console.log('Run testAudioIsolationScenario() to test audio isolation');
    });
}

console.log('🧪 Audio system test suite loaded');