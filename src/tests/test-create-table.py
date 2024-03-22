import duckdb

cursor = duckdb.connect('test.db')
print(cursor.execute(
    """
        CREATE OR REPLACE TABLE test_zz AS
        SELECT 
            * 
        FROM
        read_csv('/data/logs/2_ZZ/*_new.csv', filename=True)
    """
))

# Select the data from the table LIMIT 10