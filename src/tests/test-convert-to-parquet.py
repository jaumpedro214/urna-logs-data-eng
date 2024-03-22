import duckdb
import time
cursor = duckdb.connect('test.db')

tic = time.time()
cursor.execute(
    """
        COPY (
            SELECT 
                * 
            FROM read_csv('/data/logs/2_ZZ/*_new.csv', filename=True)
        ) TO 'test_zz.parquet' (FORMAT 'parquet');
    """
)
toc = time.time()
print(f"Time taken: {toc - tic} seconds")