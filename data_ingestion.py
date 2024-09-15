# import pandas as pd
# import sqlite3
# import os

# # Create the 'database' directory if it doesn't exist
# database_dir = "database"
# if not os.path.exists(database_dir):
#     os.makedirs(database_dir)

# # Define the path for the database file
# db_path = os.path.join(database_dir, "Sales.db")

# # Read the CSV file
# df = pd.read_csv("SalesSummerisedReport (8).csv")
# df.head()

# # Connect to the SQLite database in the 'database' directory
# connection = sqlite3.connect(db_path)

# try:
#     # Transfer data from DataFrame to SQLite database
#     df.to_sql(name="Sales", con=connection, if_exists='replace', index=False)
#     print(f"Data successfully transferred to {db_path}")
# except Exception as e:
#     print(f"An error occurred: {e}")
# finally:
#     # Close the connection
#     connection.close()
#     print("Database connection closed")



print("------------------------------------------------------------------------------")
print("Next speaker: Customer Support Agent")
print('\n')
print("Customer Support Agent (to chat_manager):")
print('\n')
print("""Thank you for reaching out with your query. Our return policy allows you to return items within 30 days of purchase. 
Please ensure that the item is in its original condition, and include all original packaging and accessories. If you need assistance with your return or
additional information, please do not hesitate to contact us. We are here to help!""")