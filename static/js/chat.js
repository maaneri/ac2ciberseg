let meuId = '';
let mensagensAnteriores = [];
let typingTimeout = null;

// Obtém o ID do usuário e sua chave pública
async function obterMeuId() {
    try {
        const response = await fetch('/chave_publica');
        const data = await response.json();
        meuId = data.user_id;
        document.getElementById('meuId').textContent = meuId;
        
        // Adiciona o ID ao título da página
        document.title = `Chat (ID: ${meuId.substring(0, 8)}...)`;
        
        // Adiciona animação de fade in
        document.getElementById('meuId').parentElement.style.opacity = '1';
    } catch (error) {
        console.error('Erro ao obter ID:', error);
        mostrarNotificacao('Erro ao conectar com o servidor', 'error');
    }
}

// Função para copiar o ID para a área de transferência
function copiarId() {
    navigator.clipboard.writeText(meuId)
        .then(() => mostrarNotificacao('ID copiado para a área de transferência!', 'success'))
        .catch(err => {
            console.error('Erro ao copiar:', err);
            mostrarNotificacao('Erro ao copiar ID', 'error');
        });
}

// Função para mostrar notificações
function mostrarNotificacao(mensagem, tipo) {
    const toast = document.createElement('div');
    toast.className = `toast ${tipo} show`;
    toast.innerHTML = `
        <div class="toast-header">
            <i class="fas fa-${tipo === 'success' ? 'check-circle' : 'exclamation-circle'} me-2"></i>
            <strong class="me-auto">Notificação</strong>
            <button type="button" class="btn-close" onclick="this.parentElement.parentElement.remove()"></button>
        </div>
        <div class="toast-body">${mensagem}</div>
    `;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// Função para mostrar indicador de digitação
function mostrarDigitando() {
    clearTimeout(typingTimeout);
    document.getElementById('typingIndicator').classList.add('active');
    typingTimeout = setTimeout(() => {
        document.getElementById('typingIndicator').classList.remove('active');
    }, 1000);
}

// Função para formatar data
function formatarData(data) {
    return new Intl.DateTimeFormat('pt-BR', {
        hour: '2-digit',
        minute: '2-digit'
    }).format(new Date(data));
}

// Função para enviar mensagem
async function enviarMensagem(event) {
    event.preventDefault();
    
    const destinatario = document.getElementById('destinatario').value;
    const mensagem = document.getElementById('mensagem').value;
    
    if (!mensagem.trim() || !destinatario.trim()) {
        mostrarNotificacao('Por favor, preencha todos os campos', 'error');
        return;
    }
    
    try {
        const response = await fetch('/enviar_mensagem', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
            },
            body: JSON.stringify({ destinatario, mensagem })
        });
        
        const data = await response.json();
        if (response.ok) {
            document.getElementById('mensagem').value = '';
            mostrarNotificacao('Mensagem enviada com sucesso!', 'success');
            atualizarMensagens();
        } else {
            mostrarNotificacao(data.erro || 'Erro ao enviar mensagem', 'error');
        }
    } catch (error) {
        console.error('Erro ao enviar mensagem:', error);
        mostrarNotificacao('Erro ao enviar mensagem', 'error');
    }
}

// Função para receber mensagens
async function receberMensagens() {
    try {
        const response = await fetch('/receber_mensagens');
        const mensagens = await response.json();
        
        if (JSON.stringify(mensagens) !== JSON.stringify(mensagensAnteriores)) {
            mensagensAnteriores = mensagens;
            const container = document.getElementById('mensagens');
            container.innerHTML = '';
            
            mensagens.forEach(msg => {
                const div = document.createElement('div');
                div.className = `message ${msg.remetente === meuId ? 'sent' : 'received'}`;
                
                // Determina o texto do remetente
                const remetenteTexto = msg.remetente === meuId ? 'Você' : 
                    `De: ${msg.remetente.substring(0, 8)}...`;
                
                div.innerHTML = `
                    <div class="user-id">
                        <i class="fas fa-${msg.remetente === meuId ? 'paper-plane' : 'user'} me-1"></i>
                        ${remetenteTexto}
                    </div>
                    <div class="message-content">${msg.mensagem}</div>
                    <div class="message-time">${formatarData(msg.timestamp)}</div>
                `;
                container.appendChild(div);
            });
            
            container.scrollTop = container.scrollHeight;
            
            // Se houver novas mensagens e a janela não estiver focada, notifica o usuário
            if (mensagens.length > mensagensAnteriores.length && !document.hasFocus()) {
                new Notification('Nova mensagem recebida!');
            }
        }
    } catch (error) {
        console.error('Erro ao receber mensagens:', error);
    }
}

// Atualiza as mensagens periodicamente
function atualizarMensagens() {
    receberMensagens();
}

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    obterMeuId();
    document.getElementById('formMensagem').addEventListener('submit', enviarMensagem);
    document.getElementById('mensagem').addEventListener('input', mostrarDigitando);
    
    // Solicita permissão para notificações
    if (Notification.permission !== 'granted') {
        Notification.requestPermission();
    }
    
    // Atualiza as mensagens a cada 2 segundos
    setInterval(atualizarMensagens, 2000);
}); 