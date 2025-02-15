document.addEventListener('DOMContentLoaded', () => {
    fetch('backend/data/availLang.json')
        .then(response => response.json())
        .then(data => {
            const srcLangSelect = document.getElementById('src-lang');
            const destLangSelect = document.getElementById('dest-lang');
            data.languages.forEach(lang => {
                const option = document.createElement('option');
                option.value = lang.code;
                option.textContent = lang.name;
                srcLangSelect.appendChild(option.cloneNode(true));
                destLangSelect.appendChild(option);
            });
        });
});

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
