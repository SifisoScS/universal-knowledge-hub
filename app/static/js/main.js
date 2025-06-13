document.addEventListener('DOMContentLoaded', () => {
    // Sifiso Chat Assistant
    const toggleSifiso = document.getElementById('toggle-sifiso');
    const sifisoChat = document.getElementById('sifiso-chat');
    const sifisoInput = document.getElementById('sifiso-input');
    const sifisoMessages = document.getElementById('sifiso-messages');

    toggleSifiso.addEventListener('click', () => {
        sifisoChat.classList.toggle('hidden');
    });

    sifisoInput.addEventListener('keypress', async (e) => {
        if (e.key === 'Enter') {
            const message = sifisoInput.value;
            sifisoMessages.innerHTML += `<p class="text-gray-800 dark:text-gray-200">${message}</p>`;
            sifisoInput.value = '';

            const response = await fetch('/api/sifiso', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message })
            });
            const data = await response.json();
            sifisoMessages.innerHTML += `<p class="text-teal-600 dark:text-teal-400">Sifiso: ${data.reply}</p>`;
            sifisoMessages.scrollTop = sifisoMessages.scrollHeight;
        }
    });

    // Quiz Submission
    const quizForm = document.getElementById('quiz-form');
    if (quizForm) {
        let startTime = Date.now();
        quizForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const timeTaken = Math.round((Date.now() - startTime) / 1000); // Seconds
            const formData = new FormData(quizForm);
            formData.append('time_taken', timeTaken);
            const response = await fetch('/knowledge/submit', {
                method: 'POST',
                body: formData
            });
            const result = await response.json();
            alert(`Your score: ${result.score}/${result.total}`);
            window.location.reload();
        });
    }
});