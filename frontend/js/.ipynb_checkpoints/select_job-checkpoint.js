window.onload = function() {
    // Your JavaScript function here
    get_jobs();
};

function get_jobs() {
    fetch('http://localhost:8000/jobs')
        .then(response => response.json())
        .then(data => {
            console.log(data);
            let jobs = data['jobs'];
            let jobs_list = document.getElementById('jobs list');
            jobs_list.innerHTML = '';
            for (let i = 0; i < jobs.length; i++) {
                let job = jobs[i];
                let job_div = document.createElement('div');
                // job_div.innerHTML = `
                //     <h2>${job['job_title']}</h2>
                //     <p>${job['job_discription']}</p>
                //     <button onclick="select_job(${job['id']})">Select</button>
                // `;
                var job_title = document.createElement("h2");
                job_title.innerHTML = job['job_title'];

                var job_discription = document.createElement("p");
                job_discription.innerHTML = job['job_discription'];

                var select_button = document.createElement("button");
                select_button.innerHTML = "Select";
                select_button.onclick = function() {
                    select_job(job['job_id']);
                };

                var delete_button = document.createElement("button");
                delete_button.innerHTML = "Delete";
                delete_button.className = "delete_button";
                delete_button.onclick = function() {
                    is_deleted = delete_job(job['job_id']).then(is_deleted => {
                        if (is_deleted) {
                            job_div.remove();
                            // alert("Job deleted successfully");
                        }
                    });
                };
                console.log("added delete button")

                job_div.appendChild(job_title);
                job_div.appendChild(job_discription);
                job_div.appendChild(select_button);
                job_div.appendChild(delete_button);

                jobs_list.appendChild(job_div);
            }
        });
}

function select_job(job_id) {
    console.log(job_id);
    window.location.href = `http://localhost:8000/static/candidate_interview.html?job_id=${job_id}`;
}

function delete_job(job_id) {

    console.log(job_id);
    return fetch(`http://localhost:8000/delete_job/${job_id}`, {
        method: 'delete',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
        if (data.status == "success") {
            return true;
        } else {
            return false;
        }
    });
}

