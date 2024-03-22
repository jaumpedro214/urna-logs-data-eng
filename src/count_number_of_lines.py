import duckdb
import time
import sys


STATES = [
    "AC", "AL", "AM", "AP", "BA", "CE", 
    "DF", "ES", "GO", "MA", "MG", "MS", 
    "MT", "PA", "PB", "PE", "PI", "PR", 
    "RJ", "RN", "RO", "RR", "RS", "SC", 
    "SE", "SP", "TO", "ZZ", "ALL"]

if __name__ == "__main__":
    # get the first sys arg
    uf = sys.argv[1]

    # if sys arg not in the brazilian states
    if uf not in STATES:
        print("Invalid state")
        sys.exit(1)

    tic = time.time()
    cursor = duckdb.connect("")

    if uf == "ALL":
        query = f"""
            SELECT 
                COUNT(*) 
            FROM '*.parquet'
        """
    else:
        query = f"""
            SELECT 
                COUNT(*) 
            FROM '{uf}.parquet'
        """
    
    cursor.execute(query)
    toc = time.time()
    print(f"Time taken to count number of lines in {uf}: {toc - tic} seconds")
    print(cursor.fetchall())
