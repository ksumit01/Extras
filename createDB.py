# import mysql.connector
# mydb = mysql.connector.connect(
#   host="localhost",
#   user="root",
#   passwd="password",
# )

# my_cursor = mydb.cursor()

# my_cursor.execute("CREATE DATABASE GA201_Zomato")
# my_cursor.execute("SHOW DATABASES")
# # for x in my_cursor:
# #   print(x)

from app import app, db, Menu, Orders 

# Create the application context
app.app_context().push()

# Create the database tables
db.create_all()

# Notify that the tables have been created
print("Database tables created successfully.")
