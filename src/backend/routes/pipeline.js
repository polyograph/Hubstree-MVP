const express = require('express');
const router = express.Router();

// Importa o controlador
const { processPipeline } = require('../controllers/pipelineController');

// Rota POST → Pipeline Ontológico
router.post('/', processPipeline);

// Exporta o roteador
module.exports = router;
