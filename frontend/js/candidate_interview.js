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
            // console.log('MediaRecorder created');
            // mediaRecorder.start(1000);
            // console.log('MediaRecorder started');
            
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
    console.log('Streaming audio to speech to text setup complete');
    socket.onmessage = function(event) {
        var text = event.data;
        // console.log('Received text: ', text);
        // console.log('Current answerElement value: ', answerElement.value);
        answerElement.value += text;
        // console.log('Updated answerElement value: ', answerElement.value);
    };
}

// Define mediaRecorder in a higher scope
var mediaRecorder;

// Function to start or stop speech to text
function toggleSpeechToText() {
    recording_button = document.getElementById('recButton');

    if (mediaRecorder && mediaRecorder.state === 'recording') {
        socket.send('stop');
        mediaRecorder.stop();
        console.log('MediaRecorder stopped');
        recording_button.classList.remove('recording');
        recording_button.classList.add('not_recording');
    } else {
        if (mediaRecorder) {
            socket.send('start');
            // we are defining how long to record
            //  before sending data to the server
            // so mediaRecorder.start(500) means it'll 
            // send data to the server every 500ms
            mediaRecorder.start(500);
            console.log('MediaRecorder started');
            recording_button.classList.remove('not_recording');
            recording_button.classList.add('recording');
        } else {
            console.log('MediaRecorder is not initialized');
        }
    }
}

//define socket in a higher scope
var socket;

// Usage example
if (checkMediaSupport()) {
    askForMediaPermission()
        .then(function(stream) {
            socket = setupWebSocket('ws://localhost:8000/speech_to_text');

            socket.onopen = function() {
                console.log('WebSocket connection opened.');
                startRecording(stream)
                    .then(function(mr) {
                        mediaRecorder = mr;
                        mediaRecorder.ondataavailable = function(e) {
                            // console.log('Data available');
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
                // retry after 500ms 
                setTimeout(function() {
                    socket = setupWebSocket('ws://localhost:8000/speech_to_text');
                }, 500);
            };
        })
        .catch(function(error) {
            console.error('Error:', error);
        });
} else {
    console.error('Media not supported on this browser.');
}
