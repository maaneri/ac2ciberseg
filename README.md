# Aplicativo Web de Mensagens Criptografadas
Este é um sistema de troca de mensagens que assegura a privacidade das comunicações por meio de criptografia RSA e proteção contra ataques CSRF.

## Funcionalidades

- Utilização de criptografia assimétrica (RSA) para proteger mensagens
- Defesa contra ataques do tipo Cross-Site Request Forgery (CSRF)
- Interface web simples e intuitiva
- Atribuição de identificadores únicos para cada usuário
- Atualização dinâmica da caixa de mensagens

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

3. Realizar a troca de mensagens:
   - Ao acessar, o sistema atribui automaticamente um identificador exclusivo ao usuário.
   - Compartilhe esse ID com quem deseja se comunicar.
   - Para enviar uma mensagem, insira o ID do destinatário no campo indicado.
   - Escreva a mensagem e clique em “Enviar”.

## Segurança

- As mensagens são protegidas com criptografia RSA (2048 bits).
- Cada usuário possui um par exclusivo de chaves (pública e privada).
- As mensagens são cifradas com a chave pública do destinatário.
- Apenas o dono da chave privada consegue acessar o conteúdo das mensagens.
- Todas as requisições POST são protegidas por tokens CSRF.
- As chaves criptográficas são armazenadas temporariamente na memória durante a sessão do usuário.

