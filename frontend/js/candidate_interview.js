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
        recording_button.textContent = 'Start Speech to Text';
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
            recording_button.textContent = 'Stop Speech to Text';
            recording_button.classList.remove('not_recording');
            recording_button.classList.add('recording');
        } else {
            console.log('MediaRecorder is not initialized');
        }
    }
}



let Questions = class {
    constructor() {
        this.questions = [];
        this.current_question = 0;
    }

    set_questions(questions) {
        
        console.log(`questions set ${questions}`);
        this.questions = questions;
    }

    get_current_question() {
        console.log(this.questions);
        console.log(this.questions[this.current_question]);
        return this.questions[this.current_question];
    }

    get_next_question() {
        if (this.current_question >= this.questions.length) {
            return null;
        } else {
            this.current_question += 1;
        }
        return this.questions[this.current_question];
    }

    get_prev_question() {
        if (this.current_question <= 0) {
            return null;
        } else {
            this.current_question -= 1;
        }
        return this.questions[this.current_question];
    }

}

let questionsInstance = new Questions();


function get_all_questions(job_id) {
    fetch('http://localhost:8000/get_all_question?job_id=' + job_id)
        .then(response => response.json())
        .then(data => {
            questionsInstance.set_questions(data['questions']);
            display_question(questionsInstance.get_current_question())
        })
}

function display_question(question) {
    document.getElementById('question').innerHTML = question['question'];
}

// run after the html is loaded
window.onload = function() {
    // get job_id from query parameter
    const urlParams = new URLSearchParams(window.location.search);
    const job_id = urlParams.get('job_id');

    if (job_id == null) {
        alert('job_id is required');
    }
    get_all_questions(job_id);
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


