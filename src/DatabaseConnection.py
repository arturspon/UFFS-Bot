import psycopg2
from conf.settings import databaseToken

class DatabaseConnection:
    def __init__(self):
        try:
            self.DATABASE_URL = databaseToken
            self.openConnection()
        except Exception as e:
            print('Não foi possível conectar ao database: ', e)

    def openConnection(self):
        self.conn = psycopg2.connect(self.DATABASE_URL, sslmode='require')
        self.conn.autocommit = True

    def fetchAll(self, query, args):
        try:
            self.cursor = self.conn.cursor()
            self.cursor.execute(query, args)
            results = self.cursor.fetchall()
            self.cursor.close()
            return results
        except Exception as e:
            print('Um erro ocorreu no fetchAll:', e, ', tentando reabrir a conexão')
            self.openConnection()
            return self.fetchAll(query, args)

    def executeQuery(self, query, args):
        try:
            self.cursor = self.conn.cursor()
            self.cursor.execute(query, args)
            self.cursor.close()
        except Exception as e:
            print('Um erro ocorreu no executeQuery:', e, ', tentando reabrir a conexão')
            self.openConnection()
            self.executeQuery(query, args)

    def createTables(self):
        self.cursor = self.conn.cursor()
        # Cria tabela para armazenar os chat_id dos usuarios possibilitando o envio de mensagens sem o chamado de comandos
        # campus armazena o campus do qual o usuario deseja saber o cardapio
        # Period armazena se ira receber o cardapio semanalmente ou diariamente ou não receber
        query = "CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, chat_id BIGINT, username TEXT, campus TEXT, period TEXT);"
        self.cursor.execute(query)
        # Cria tabela para armazenar os links das imagens usados para exibir o cardápio
        # weekNumber armazena o dia da semana da url criada
        # imgUrl armazena o url da imagem criada
        # imgHtml armazena o html da tabela que virou imagem
        # campus armazena o campus do qual o usuario deseja saber o cardapio
        query = "CREATE TABLE IF NOT EXISTS images (id SERIAL PRIMARY KEY, weekNumber INTEGER, imgUrl TEXT, imgHtml TEXT, campus TEXT);"
        self.cursor.execute(query)
        # Tabela criada para checar o status do cardápio
        query = "CREATE TABLE IF NOT EXISTS status (id SERIAL PRIMARY KEY, description TEXT, value BOOLEAN);"
        self.cursor.execute(query)
        self.cursor.close()