const submitBtn = document.getElementById('submitBtn');
const inputText = document.getElementById('inputText');
const output = document.getElementById('output');

submitBtn.addEventListener('click', async () => {
  const text = inputText.value.trim();

  if (!text) {
    alert('⚠️ Por favor, digite algum texto para processar.');
    return;
  }

  output.textContent = '⏳ Processando...';

  try {
    const response = await fetch('https://hubstree-mvp-2.onrender.com/pipeline', {
 
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ input: text })
    });

    if (!response.ok) {
      throw new Error(`Erro: ${response.statusText}`);
    }

    const data = await response.json();
    output.textContent = JSON.stringify(data, null, 2);
  } catch (error) {
    output.textContent = `❌ Erro ao processar: ${error.message}`;
  }
});
