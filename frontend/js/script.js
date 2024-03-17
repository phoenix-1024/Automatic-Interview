


function generate_questions() {
    var job_discription = document.getElementById("job_discription").value;
    var required_skills = document.getElementById("required_skills").value;

    // include required skills in job discription
    job_discription = job_discription + " required skills: " + required_skills;

    fetch('http://localhost:8000/generate_questions', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ job_discription: job_discription }),
    })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            display_questions(data);
        })
        .then(() => {
            document.getElementById("save_questions").disabled = false;
        })
        .catch((error) => {
            console.error('Error:', error);
        });
}

function display_questions(questions_json) {
    var questions = questions_json.questions;
    
    for (let i = 0; i < questions.length; i++) {
        add_question(questions[i]["question"], questions[i]["criteria"])
    }
}

function clear_all_questions() {
    document.getElementById("questions").innerHTML = "";
    // disable save button 
    document.getElementById("save_questions").disabled = true;
}

function disable_save_button_if_no_questions() {
    var question_div = document.getElementById("questions");
    var question_n_criteria = question_div.getElementsByClassName("question_n_criteria");
    if (question_n_criteria.length == 0) {
        document.getElementById("save_questions").disabled = true;
    }
}

function add_question(question_text = '', criteria_text = '') {
    var question_div = document.getElementById("questions");

    let question_n_criteria = document.createElement("div");
    question_n_criteria.className = "question_n_criteria";
        
    var question = document.createElement("textarea");
    question.className = "question";
    // question.id = `question_${i+1}`;
    question.setAttribute("rows", "4");
    question.setAttribute("cols", "50");

    var criteria = document.createElement("textarea");
    criteria.className = "criteria";
    // criteria.id = `criteria_${i+1}`;
    criteria.setAttribute("rows", "4");
    criteria.setAttribute("cols", "50");

    question.innerText = question_text;
    criteria.innerText = criteria_text;

    // question_no = document.createElement("h3");
    // question_no.innerText = `Question ${i+1}`;

    delete_button = document.createElement("button");
    delete_button.className = "delete_button";
    delete_button.innerText = "Delete";
    delete_button.addEventListener("click", function() {
        question_n_criteria.remove();
        disable_save_button_if_no_questions();
    });
    // console.log("added delete button")

    // question_n_criteria.appendChild(question_no);
    question_n_criteria.appendChild(delete_button);
    question_n_criteria.appendChild(question);
    question_n_criteria.appendChild(criteria);

    question_div.appendChild(question_n_criteria);

    // enable save button
    document.getElementById("save_questions").disabled = false;
}

// save questions to database
function save_questions() {
    var job_title = document.getElementById("job_title").value;
    if (job_title == "") {
        alert("Please enter job title");
        return;
    }
    var job_discription = document.getElementById("job_discription").value;
    if (job_discription == "") {
        alert("Please enter job discription");
        return;
    }
    
    var questions = [];
    var question_div = document.getElementById("questions");
    var question_n_criteria = question_div.getElementsByClassName("question_n_criteria");
    for (var i = 0; i < question_n_criteria.length; i++) {
        var question = question_n_criteria[i].getElementsByClassName("question")[0].value;
        var criteria = question_n_criteria[i].getElementsByClassName("criteria")[0].value;
        questions.push({ question: question, criteria: criteria });
    }
    fetch('http://localhost:8000/save_job', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({job_title: job_title,
            job_discription: job_discription,
            questions: questions }),
    })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            if (data.status == "success") {
                alert("Questions saved successfully");
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
}