document.getElementById('submitBtn').addEventListener('click', async () => {
  const inputText = document.getElementById('inputText').value.trim();

  if (!inputText) {
    alert('Por favor, digite algum texto para processar.');
    return;
  }

  try {
    const response = await fetch('http://localhost:3000/pipeline', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ input: inputText })
    });

    if (!response.ok) {
      throw new Error(`Erro: ${response.statusText}`);
    }

    const data = await response.json();

    document.getElementById('output').textContent = JSON.stringify(data, null, 2);
  } catch (error) {
    alert(`Falha na requisição: ${error.message}`);
  }
});
