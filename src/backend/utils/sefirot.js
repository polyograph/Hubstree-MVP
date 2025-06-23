// Funções auxiliares para cada sefirá do pipeline Hubstree

function keter(input) {
    return input;
}

function binah(input) {
    return `🔍 Análise estrutural de "${input}"`;
}

function chokhmah(input) {
    return `💡 Metáforas e insights sobre "${input}"`;
}

function tiferet(input) {
    return `🎨 Wireframe semântico baseado em "${input}"`;
}

function gevurah(input) {
    return `🛠️ Análise crítica, restrições e riscos de "${input}"`;
}

function chesed(input) {
    return `🚀 Expansão de oportunidades e melhorias para "${input}"`;
}

function netzach(input) {
    return `🔁 Automação, persistência e ciclos para "${input}"`;
}

function hod(input) {
    return `🗂️ Organização, documentação e formalização de "${input}"`;
}

function yesod(input) {
    return `🔗 Consolidação semântica e banco de dados intermediário para "${input}"`;
}

function malkuth(input) {
    return `🌐 Output final: landing page, relatório ou entrega baseada em "${input}"`;
}

// Exporta todas as funções para serem usadas no controller
module.exports = {
    keter,
    binah,
    chokhmah,
    tiferet,
    gevurah,
    chesed,
    netzach,
    hod,
    yesod,
    malkuth
};
