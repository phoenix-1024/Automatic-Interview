


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
        .catch((error) => {
            console.error('Error:', error);
        });
}

function display_questions(questions_json) {
    var questions = questions_json.questions;
    var question_div = document.getElementById("questions");
    question_div.innerHTML = "";
    for (var i = 0; i < questions.length; i++) {
        var question_n_criteria = document.createElement("div");
        question_n_criteria.className = "question_n_criteria";
        
        var question = document.createElement("textarea");
        question.className = "question";
        question.id = `question_${i+1}`;
        question.setAttribute("rows", "4");
        question.setAttribute("cols", "50");
        
        var criteria = document.createElement("textarea");
        criteria.className = "criteria";
        criteria.id = `criteria_${i+1}`;
        criteria.setAttribute("rows", "4");
        criteria.setAttribute("cols", "50");

        question.innerText = `question ${i+1}: ` +  questions[i].question;
        criteria.innerText = `criteria ${i+1}: ` +  questions[i].criteria;
        question_n_criteria.appendChild(question);
        question_n_criteria.appendChild(criteria);

        question_div.appendChild(question_n_criteria);
    }
}