import psycopg2
from conf.settings import databaseToken

class DatabaseConnection:
    def __init__(self):
        try:
            self.DATABASE_URL = databaseToken
            self.conn = psycopg2.connect(self.DATABASE_URL, sslmode='require')
            self.conn.autocommit = True
        except Exception as e:
            print('Não foi possível conectar ao database: ', e)

    def fetchAll(self, query):
        self.cursor = self.conn.cursor()
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        self.cursor.close()
        return results

    def executeQuery(self, query):
        self.cursor = self.conn.cursor()
        self.cursor.execute(query)
        self.cursor.close()

    def createTables(self):
        self.cursor = self.conn.cursor()
        # Cria tabela para armazenar os chat_id dos usuarios possibilitando o envio de mensagens sem o chamado de comandos
        # campus armazena o campus do qual o usuario deseja saber o cardapio
        # Period armazena se ira receber o cardapio semanalmente ou diariamente ou não receber
        query = "CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, chat_id INTEGER, username TEXT, campus TEXT, period TEXT);"
        self.executeQuery(query)
        # Cria tabela para armazenar os links das imagens usados para exibir o cardápio
        # weekNumber armazena o dia da semana da url criada
        # imgUrl armazena o url da imagem criada
        # imgHtml armazena o html da tabela que virou imagem
        # campus armazena o campus do qual o usuario deseja saber o cardapio
        query = "CREATE TABLE IF NOT EXISTS images (id SERIAL PRIMARY KEY, weekNumber INTEGER, imgUrl TEXT, imgHtml TEXT, campus TEXT);"
        self.executeQuery(query)
        # Tabela criada para checar o status do cardápio
        query = "CREATE TABLE IF NOT EXISTS status (id SERIAL PRIMARY KEY, description TEXT, value BOOLEAN);"
        self.executeQuery(query)
        self.cursor.close()