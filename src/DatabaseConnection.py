import sqlite3

class DatabaseConnection:
    def fetchAll(self, query):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        return results

    def executeQuery(self, query):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        conn.close()

    def createTables(self):
        # Cria tabela para armazenar os chat_id dos usuarios possibilitando o envio de mensagens sem o chamado de comandos
        # campus armazena o campus do qual o usuario deseja saber o cardapio
        # Period armazena se ira receber o cardapio semanalmente ou diariamente ou não receber
        query = "CREATE TABLE IF NOT EXISTS users (chat_id INTEGER PRIMARY KEY, campus TEXT, period TEXT);"
        self.executeQuery(query)
        # Cria tabela para armazenar os links das imagens usados para exibir o cardápio
        # weekNumber armazena o dia da semana da url criada
        # imgUrl armazena o url da imagem criada
        # imgHtml armazena o html da tabela que virou imagem
        # campus armazena o campus do qual o usuario deseja saber o cardapio
        query = "CREATE TABLE IF NOT EXISTS images (id INTEGER PRIMARY KEY, weekNumber INTEGER, imgUrl TEXT, imgHtml TEXT, campus TEXT);"
        self.executeQuery(query)