# Configuração para usar PyMySQL como substituto do mysqlclient
import pymysql

# Instala PyMySQL como MySQLdb
pymysql.install_as_MySQLdb()

# Força a versão para compatibilidade com Django 6.0
pymysql.version_info = (2, 2, 1, "final", 0)
