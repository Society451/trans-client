const form = document.getElementById('translate-form');
form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const text = document.getElementById('text').value.trim();
    const srcLang = document.getElementById('src-lang').value;
    const destLang = document.getElementById('dest-lang').value;
    const resultDiv = document.getElementById('result');

    if (text === "") {
        resultDiv.textContent = 'Please enter text to translate.';
        return;
    }

    resultDiv.textContent = 'Translating...';

    const response = await window.pywebview.api.translate(text, srcLang, destLang);
    resultDiv.innerHTML = `<strong>Translated Text:</strong> ${response.translated_text}<br><strong>Time Taken:</strong> ${response.time_taken} seconds`;
});
