// 🌳 Hubstree – Ontological Pipeline Server
// Backend básico em Node.js usando Express

const express = require('express');
const cors = require('cors');
const app = express();
const port = 3000;

// Middlewares
app.use(cors());
app.use(express.json());

// 🔗 Endpoint principal – Teste de status
app.get('/', (req, res) => {
    res.send('🌳 Hubstree API is running. Welcome to the Ontological Pipeline!');
});

// 🚀 Endpoint do pipeline ontológico
app.post('/pipeline', (req, res) => {
    const input = req.body.input;

    if (!input) {
        return res.status(400).json({ error: 'Input is required' });
    }

    const output = {
        keter: input,
        binah: `🔍 Análise estrutural de "${input}"`,
        chokhmah: `💡 Criação de metáforas e insights sobre "${input}"`,
        tiferet: `🎨 Wireframe gerado a partir de "${input}"`,
        gevurah: `🛠️ Análise crítica e riscos de "${input}"`,
        chesed: `🚀 Oportunidades e expansões para "${input}"`,
        netzach: `🔁 Persistência e automação de "${input}"`,
        hod: `🗂️ Organização, documentação e detalhamento de "${input}"`,
        yesod: `🔗 Consolidação e base de dados semântica de "${input}"`,
        malkuth: `🌐 Output final: landing page, relatório ou entrega para "${input}"`
    };

    res.json(output);
});

// 🏃 Start do servidor
app.listen(port, () => {
    console.log(`🚀 Hubstree API rodando em http://localhost:${port}`);
});
