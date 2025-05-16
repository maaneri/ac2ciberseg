# Sistema de Mensagens Seguras

Este é um sistema de mensagens seguras que utiliza criptografia RSA e proteção CSRF para garantir a segurança das comunicações.

## Funcionalidades

- Criptografia assimétrica (RSA) para mensagens
- Proteção contra ataques CSRF
- Interface web amigável
- Sistema de IDs únicos para usuários
- Atualização automática das mensagens

## Requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

## Instalação

1. Clone este repositório ou baixe os arquivos
2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Como Usar

1. Execute o servidor Flask:
```bash
python app.py
```

2. Abra o navegador e acesse:
```
http://localhost:5000
```

3. Para trocar mensagens:
   - Cada usuário receberá um ID único ao acessar o sistema
   - Copie seu ID e compartilhe com quem deseja trocar mensagens
   - Para enviar uma mensagem, cole o ID do destinatário no campo apropriado
   - Digite sua mensagem e clique em "Enviar"

## Segurança

- As mensagens são criptografadas usando RSA com chaves de 2048 bits
- Cada usuário tem seu próprio par de chaves (pública/privada)
- As mensagens são criptografadas com a chave pública do destinatário
- Apenas o destinatário pode descriptografar as mensagens com sua chave privada
- Proteção CSRF em todas as requisições POST
- As chaves são mantidas apenas em memória durante a sessão

