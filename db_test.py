import MySQLdb
import configparser

def test_connection():
    # Read database configuration from the config file
    config = configparser.ConfigParser()
    config.read('utils/configs/sample_config.ini')

    try:
        db_config = config['DATABASE']
        
        # Connect to the MySQL database
        connection = MySQLdb.connect(
            host=db_config['host'],
            user=db_config['user'],
            passwd=db_config['password'],
            db=db_config['database'],
            port=int(db_config['port'])
        )
        
        if connection.open:
            print("✅ Successfully connected to the database!")
        else:
            print("❌ Failed to connect to the database.")
        
        # Close the connection
        connection.close()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_connection()
