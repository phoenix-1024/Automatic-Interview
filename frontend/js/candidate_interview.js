// Check for media support on the browser
function checkMediaSupport() {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        return true;
    } else {
        return false;
    }
}

// Ask for media record permission
function askForMediaPermission() {
    return navigator.mediaDevices.getUserMedia({ audio: true });
}

// Start recording audio using getUserMedia
function startRecording(stream) {
    return new Promise(function(resolve, reject) {
        try {
            let options = { mimeType: 'audio/webm; codecs=opus' };
            let mediaRecorder = new MediaRecorder(stream, options);
            console.log('MediaRecorder created');
            mediaRecorder.start(1000);
            console.log('MediaRecorder started');
            
            resolve(mediaRecorder);
        } catch (error) {
            reject(error);
        }
    });
}

// Setup WebSocket to stream recorded media in real time
function setupWebSocket(url) {
    var socket = new WebSocket(url);
    return socket;
}

// Stream audio to speech to text endpoint and display the output text in "answer" element
function streamAudioToSpeechToText(socket, answerElement) {
    console.log('Streaming audio to speech to text started');
    socket.onmessage = function(event) {
        var text = event.data;
        answerElement.innerText = answerElement.value + " " + text;
    };
}


// Usage example
if (checkMediaSupport()) {
    askForMediaPermission()
        .then(function(stream) {
            var socket = setupWebSocket('ws://localhost:8000/speech_to_text');

            socket.onopen = function() {
                console.log('WebSocket connection opened.');
                startRecording(stream)
                    .then(function(mediaRecorder) {
                        mediaRecorder.ondataavailable = function(e) {
                            console.log('Data available');
                            // mediaRecorder.stop();
                            socket.send(e.data);
                            // mediaRecorder.start(2000);
                        };
                        streamAudioToSpeechToText(socket, document.getElementById('answer'));
                    })
                    .catch(function(error) {
                        console.error('Error:', error);
                    });
            };

            socket.onclose = function() {
                console.log('WebSocket connection closed.');
            };
        })
        .catch(function(error) {
            console.error('Error:', error);
        });
} else {
    console.error('Media not supported on this browser.');
}

let audioContext = new (window.AudioContext || window.webkitAudioContext)();
console.log("sample rate",audioContext.sampleRate);