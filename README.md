# UFFS-Bot
[![](https://tokei.rs/b1/github/arturspon/UFFS-Bot?category=code)](https://github.com/arturspon/UFFS-Bot)
[![](https://img.shields.io/github/issues-raw/arturspon/UFFS-Bot.svg)](https://github.com/arturspon/UFFS-Bot/issues)

Um bot do Telegram para ajudar estudantes da UFFS no dia a dia.

## O que ele faz?
Até o momento, as seguintes funções estão implementadas:  
  
:heavy_check_mark: Visualização do cardápio do restaurante universitário;  
:heavy_check_mark: Envio automático do cardápio do RU diariamente/semanalmente;  
:heavy_check_mark: Visualização do cardápio de lanches da cantina;  
:heavy_check_mark: Visualização dos horários de ônibus;  
:heavy_check_mark: Visualização dos próximos eventos na UFFS;  
:heavy_check_mark: Download em PDF do calendário acadêmico;  
:heavy_check_mark: Visualização de datas importantes (rematrícula, ajuste, férias, etc).  

## Como utilizar
Inicie uma nova conversa no Telegram e procure por @UFFS_Bot.

## Ambiente

O bot é hospedado no [Heroku](https://www.heroku.com/) e utiliza a biblioteca [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) para enviar/receber requisições.

## Executando localmente
Antes de tudo, você precisa criar um bot em seu telegram, consultando o [@BotFather](https://core.telegram.org/bots#3-how-do-i-create-a-bot).  
Depois, crie um arquivo nomeado `.env` dentro da pasta `src/conf` e configure a API key do seu recém criado bot:  
```
telegramToken=SUA_CHAVE_AQUI
```  
Se você deseja rodar as funcionalidades do cardápio, também é necessário as chaves `htciId` e `htciKey`, que podem ser criadas na API [hcti.io](https://htmlcsstoimage.com/).

Para executar localmente, você deve executar o seguinte comando na pasta raíz do repositório:  
```python src/uffsBot.py```  
  
É necessário o Python 3 e as dependências podem ser instaladas com o comando:  
`pip install -r requirements.txt`

## Contribuindo
Por favor sinta-se a vontade para contribuir.  
Antes de fazer um *pull request*, crie um bot no Telegram e teste suas alterações.

## Licença
[MIT](https://choosealicense.com/licenses/mit/)
