import sqlite3
import pandas as pd

def pd_to_sqlDB(input_df: pd.DataFrame,
                table_name: str,
                db_name: str = 'default.db') -> None:

    '''Take a Pandas dataframe `input_df` and upload it to `table_name` SQLITE table
    Args:
        input_df (pd.DataFrame): Dataframe containing data to upload to SQLITE
        table_name (str): Name of the SQLITE table to upload to
        db_name (str, optional): Name of the SQLITE Database in which the table is created. 
                                 Defaults to 'default.db'.
    '''

    # Step 1: Setup local logging
    import logging
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    # Step 2: Find columns in the dataframe
    cols = input_df.columns
    cols_string = ','.join(cols)
    val_wildcard_string = ','.join(['?'] * len(cols))

    # Step 3: Connect to a DB file if it exists, else crete a new file
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    logging.info(f'SQL DB {db_name} created')

    # Step 4: Create Table
    sql_string1 = f"""DROP TABLE IF EXISTS {table_name};"""
    sql_string2 = f"""CREATE TABLE {table_name} ({cols_string});"""
    cur.execute(sql_string1)
    cur.execute(sql_string2)
    logging.info(f'SQL Table {table_name} created with {len(cols)} columns')

    # Step 5: Upload the dataframe
    rows_to_upload = input_df.to_dict(orient='split')['data']
    sql_string = f"""INSERT INTO {table_name} ({cols_string}) VALUES ({val_wildcard_string});"""    
    cur.executemany(sql_string, rows_to_upload)
    logging.info(f'{len(rows_to_upload)} rows uploaded to {table_name}')
  
    # Step 6: Commit the changes and close the connection
    con.commit()
    con.close()

def sql_query_to_pd(sql_query_string: str, db_name: str ='default.db') -> pd.DataFrame:
    '''Execute an SQL query and return the results as a pandas dataframe
    Args:
        sql_query_string (str): SQL query string to execute
        db_name (str, optional): Name of the SQLITE Database to execute the query in.
                                 Defaults to 'default.db'.
    Returns:
        pd.DataFrame: Results of the SQL query in a pandas dataframe
    '''    
    # Step 1: Connect to the SQL DB
    con = sqlite3.connect(db_name)

    # Step 2: Execute the SQL query
    cursor = con.execute(sql_query_string)

    # Step 3: Fetch the data and column names
    result_data = cursor.fetchall()
    cols = [description[0] for description in cursor.description]

    # Step 4: Close the connection
    con.close()

    # Step 5: Return as a dataframe
    return pd.DataFrame(result_data, columns=cols)

def run_query(sql_str: str = ""):
  # Step 1: Read the csv file into a dataframe
  # Dataset from https://www.kaggle.com/gpreda/covid-world-vaccination-progress
  input_df = pd.read_csv('/content/test_data/country_vaccinations.csv')
  orders_df = pd.read_csv('/content/test_data/orders.csv')
  employees_df = pd.read_csv('/content/test_data/employees.csv')

  if sql_str.replace("\n", "").upper()=="REEMPLAZAR" or sql_str=="":
    print("-"*30 + ">" + "DATASET: country_vaccinations")
    input_df.info()
    print("\n\n")
    print("-"*30 + ">" + "DATASET: orders")
    orders_df.info()
    print("\n\n")
    print("-"*30 + ">" + "DATASET: employees")
    employees_df.info()
    # return (input_df.head(), orders_df.head(), employees_df.info())
    return ""
    
  # Step 2: Upload the dataframe to a SQL Table
  pd_to_sqlDB(input_df,
              table_name='country_vaccinations',
              db_name='default.db')
  pd_to_sqlDB(orders_df,
              table_name='orders',
              db_name='default.db')
  pd_to_sqlDB(employees_df,
              table_name='employees',
              db_name='default.db')

  # Step 3: Write the SQL query in a string variable
  # sql_query_string = """
  #     SELECT country, SUM(daily_vaccinations) as total_vaccinated
  #     FROM country_vaccinations 
  #     WHERE daily_vaccinations IS NOT NULL 
  #     GROUP BY country
  #     ORDER BY total_vaccinated DESC
  # """
  sql_query_string = sql_str

  # Step 4: Exectue the SQL query
  result_df = sql_query_to_pd(sql_query_string, db_name='default.db')
  return result_df