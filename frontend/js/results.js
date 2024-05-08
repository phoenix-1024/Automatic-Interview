function get_all_results() {
    fetch('http://localhost:8000/get_all_results')
        .then(response => response.json())
        .then(data => {
            console.log(data);
            let results = data['results'];
            let results_list = document.getElementById('results');
            for (let i = 0; i < results.length; i++) {
                let result = results[i];
                let result_div = document.createElement('div');

                let h2_job_result = document.createElement('h2');
                h2_job_result.textContent = `Result No.${result['rid']} for Job: ${result['job_id']}. ${result['job_name']}`;
                result_div.appendChild(h2_job_result);

                let p_status = document.createElement('p');
                p_status.textContent = result['status'];
                result_div.appendChild(p_status);

                let button_view = document.createElement('button');
                button_view.innerHTML = 'View';
                if (result['status'] == 'COMPLETED') {
                    button_view.disabled = false;
                } else {
                    button_view.disabled = true;
                }
                button_view.onclick = function() {
                    get_detailed_result(result['rid']);
                }
                result_div.appendChild(button_view);

                results_list.appendChild(result_div);
                
                
            }});          
            

}

// on window load run get_all_results
window.onload = get_all_results;

function reload_results() {
    let results_list = document.getElementById('results');  
    results_list.innerHTML = '';
    get_all_results();
}


function get_detailed_result(rid) {
    fetch("/get_results_by_id?rid=" + rid)
    .then(response => response.json())
    .then(data => {
        console.log(data);
        let result = data['result'];
        let details_div = document.getElementById('result_detail');
        details_div.innerHTML = '<h1>Result Details:</h1>';
        let avg_score_h2 = document.createElement('h2');
        avg_score_h2.textContent = `Average Score: ${result['avg_score']}`;
        details_div.appendChild(avg_score_h2);

        all_qas = result["results"]

        // qid, question, answer, cretria
        for (let i = 0; i < all_qas.length; i++) {
            let detail = all_qas[i];
            let detail_div = document.createElement('div');
            detail_div.classList.add('detail');
            
            let question_p = document.createElement('p');
            question_p.textContent = `Question: ${detail['question']}`;
            detail_div.appendChild(question_p);

            let answer_p = document.createElement('p');
            answer_p.textContent = `Answer: ${detail['answer']}`;
            detail_div.appendChild(answer_p);

            let criteria_p = document.createElement('p');
            criteria_p.textContent = `Criteria: ${detail['cretria']}`;
            detail_div.appendChild(criteria_p);

            let score_p = document.createElement('p');
            score_p.textContent = `Score: ${detail['score']}`;
            detail_div.appendChild(score_p);

            let summary_p = document.createElement('summary');
            summary_p.textContent = `Summary: ${detail['summary']}`;
            detail_div.appendChild(summary_p);

            details_div.appendChild(detail_div);
        }}
    )
}