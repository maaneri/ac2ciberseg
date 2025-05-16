from flask import Flask, render_template, request, jsonify, session, url_for
from flask_wtf.csrf import CSRFProtect
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
import base64
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32)
csrf = CSRFProtect(app)

# Dicionário para armazenar as mensagens (simulando um banco de dados)
mensagens = []

# Dicionário para armazenar as chaves dos usuários
chaves_usuarios = {}

def gerar_par_chaves():
    """Gera um par de chaves RSA"""
    chave_privada = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    chave_publica = chave_privada.public_key()
    return chave_privada, chave_publica

def serializar_chave_publica(chave_publica):
    """Serializa a chave pública para formato PEM"""
    pem = chave_publica.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return base64.b64encode(pem).decode('utf-8')

@app.route('/')
def index():
    """Rota principal"""
    if 'user_id' not in session:
        # Gera um ID único para o usuário
        session['user_id'] = os.urandom(16).hex()
        # Gera par de chaves para o usuário
        chave_privada, chave_publica = gerar_par_chaves()
        chaves_usuarios[session['user_id']] = {
            'privada': chave_privada,
            'publica': chave_publica,
            'ultima_atividade': datetime.now()
        }
    else:
        # Atualiza timestamp de última atividade
        if session['user_id'] in chaves_usuarios:
            chaves_usuarios[session['user_id']]['ultima_atividade'] = datetime.now()
    
    return render_template('index.html')

@app.route('/enviar_mensagem', methods=['POST'])
def enviar_mensagem():
    """Rota para enviar mensagens"""
    dados = request.get_json()
    mensagem = dados.get('mensagem')
    destinatario = dados.get('destinatario')
    
    if not mensagem or not destinatario:
        return jsonify({'erro': 'Mensagem ou destinatário não fornecidos'}), 400
    
    # Verifica se o destinatário existe
    if destinatario not in chaves_usuarios:
        return jsonify({'erro': 'Destinatário não encontrado'}), 404
    
    try:
        # Criptografa a mensagem com a chave pública do destinatário
        chave_publica_destinatario = chaves_usuarios[destinatario]['publica']
        mensagem_bytes = mensagem.encode()
        mensagem_criptografada = chave_publica_destinatario.encrypt(
            mensagem_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # Armazena a mensagem criptografada junto com o texto original
        mensagens.append({
            'remetente': session['user_id'],
            'destinatario': destinatario,
            'mensagem': base64.b64encode(mensagem_criptografada).decode('utf-8'),
            'mensagem_original': mensagem,  # Armazena o texto original
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify({'sucesso': True})
    except Exception as e:
        print(f"Erro ao criptografar mensagem: {e}")
        return jsonify({'erro': 'Erro ao processar mensagem'}), 500

@app.route('/receber_mensagens')
def receber_mensagens():
    """Rota para receber mensagens"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'erro': 'Usuário não autenticado'}), 401
    
    try:
        # Filtra mensagens enviadas e recebidas pelo usuário
        minhas_mensagens = [m for m in mensagens if m['destinatario'] == user_id or m['remetente'] == user_id]
        
        # Descriptografa as mensagens recebidas e inclui as mensagens enviadas
        mensagens_processadas = []
        for msg in minhas_mensagens:
            try:
                if msg['destinatario'] == user_id:
                    # Descriptografa mensagens recebidas
                    mensagem_criptografada = base64.b64decode(msg['mensagem'])
                    chave_privada = chaves_usuarios[user_id]['privada']
                    mensagem_bytes = chave_privada.decrypt(
                        mensagem_criptografada,
                        padding.OAEP(
                            mgf=padding.MGF1(algorithm=hashes.SHA256()),
                            algorithm=hashes.SHA256(),
                            label=None
                        )
                    )
                    mensagem_texto = mensagem_bytes.decode()
                else:
                    # Para mensagens enviadas, usa o texto original
                    mensagem_texto = msg['mensagem_original']

                mensagens_processadas.append({
                    'remetente': msg['remetente'],
                    'destinatario': msg['destinatario'],
                    'mensagem': mensagem_texto,
                    'timestamp': msg['timestamp']
                })
            except Exception as e:
                print(f"Erro ao processar mensagem: {e}")
        
        # Ordena as mensagens por timestamp
        mensagens_processadas.sort(key=lambda x: x['timestamp'])
        
        return jsonify(mensagens_processadas)
    except Exception as e:
        print(f"Erro ao processar mensagens: {e}")
        return jsonify({'erro': 'Erro ao processar mensagens'}), 500

@app.route('/chave_publica')
def obter_chave_publica():
    """Rota para obter a chave pública do usuário atual"""
    user_id = session.get('user_id')
    if not user_id or user_id not in chaves_usuarios:
        return jsonify({'erro': 'Usuário não encontrado'}), 404
    
    chave_publica = chaves_usuarios[user_id]['publica']
    return jsonify({
        'user_id': user_id,
        'chave_publica': serializar_chave_publica(chave_publica)
    })

@app.route('/mensagens_criptografadas')
def mensagens_criptografadas():
    """Rota para visualizar mensagens criptografadas"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'erro': 'Usuário não autenticado'}), 401
    
    # Filtra mensagens enviadas e recebidas pelo usuário
    minhas_mensagens = [m for m in mensagens if m['destinatario'] == user_id or m['remetente'] == user_id]
    
    # Formata as mensagens para exibição
    mensagens_formatadas = []
    for msg in minhas_mensagens:
        mensagens_formatadas.append({
            'remetente': msg['remetente'],
            'destinatario': msg['destinatario'],
            'mensagem_criptografada': msg['mensagem'],
            'timestamp': msg['timestamp'],
            'tipo': 'enviada' if msg['remetente'] == user_id else 'recebida'
        })
    
    return render_template('mensagens_criptografadas.html', mensagens=mensagens_formatadas)

@app.route('/api/mensagens_criptografadas')
def api_mensagens_criptografadas():
    """API para obter mensagens criptografadas"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'erro': 'Usuário não autenticado'}), 401
    
    # Filtra mensagens enviadas e recebidas pelo usuário
    minhas_mensagens = [m for m in mensagens if m['destinatario'] == user_id or m['remetente'] == user_id]
    
    # Formata as mensagens para exibição
    mensagens_formatadas = []
    for msg in minhas_mensagens:
        mensagens_formatadas.append({
            'remetente': msg['remetente'],
            'destinatario': msg['destinatario'],
            'mensagem_criptografada': msg['mensagem'],
            'timestamp': msg['timestamp'],
            'tipo': 'enviada' if msg['remetente'] == user_id else 'recebida'
        })
    
    return jsonify(mensagens_formatadas)

if __name__ == '__main__':
    # Cria diretório static/js se não existir
    os.makedirs('static/js', exist_ok=True)
    app.run(debug=True) 