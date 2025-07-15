document.addEventListener('DOMContentLoaded', () => {
    const summarizeBtn = document.getElementById('summarize-btn');
    const youtubeUrlInput = document.getElementById('youtube-url');
    const resultDiv = document.getElementById('result');

    summarizeBtn.addEventListener('click', async () => {
        const url = youtubeUrlInput.value.trim();
        if (!url) {
            resultDiv.innerHTML = '<p style="color: red;">Please enter a YouTube URL.</p>';
            return;
        }

        // Show loading indicator
        resultDiv.innerHTML = '<div class="loader"></div>';

        try {
            const response = await fetch('/summarize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();
            displayResult(data);

        } catch (error) {
            resultDiv.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
        }
    });

    function displayResult(data) {
        // Clear previous results
        resultDiv.innerHTML = '';

        // Display Summary
        const summarySection = document.createElement('div');
        summarySection.className = 'result-section';
        summarySection.innerHTML = `<h2>Summary & Key Insights (Japanese)</h2><p>${data.summary.replace(/\n/g, '<br>')}</p>`;
        resultDiv.appendChild(summarySection);

        // Display English Learning Content
        const learningSection = document.createElement('div');
        learningSection.className = 'result-section';
        learningSection.innerHTML = '<h2>English Learning Content</h2>';

        // Vocabulary
        const vocabList = document.createElement('ul');
        data.english_learning.vocabulary.forEach(item => {
            const li = document.createElement('li');
            li.innerHTML = `<strong>${item.word}:</strong> ${item.example}`;
            vocabList.appendChild(li);
        });
        learningSection.innerHTML += '<h3>Vocabulary</h3>';
        learningSection.appendChild(vocabList);

        // Grammar
        const grammarList = document.createElement('ul');
        data.english_learning.grammar.forEach(item => {
            const li = document.createElement('li');
            li.innerHTML = `<strong>${item.rule}:</strong> ${item.example}`;
            grammarList.appendChild(li);
        });
        learningSection.innerHTML += '<h3>Grammar</h3>';
        learningSection.appendChild(grammarList);

        resultDiv.appendChild(learningSection);
    }
});