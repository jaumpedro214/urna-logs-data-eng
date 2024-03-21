import os
import tqdm
import time


if __name__ == "__main__":

    BASE_LOGS_PATH = "./data/logs"
    # list all directories in the base path
    directories = os.listdir(BASE_LOGS_PATH)
    command = "touch {} && iconv -f ISO-8859-1 -t UTF-8//TRANSLIT {} > {} && rm {}"

    tic = time.time()
    for directory in directories:
        path = BASE_LOGS_PATH + "/" + directory
        if not os.path.isdir(path):
            continue

        files = os.listdir(path)
        files = [file for file in files if file.endswith(".csv") and not file.endswith("_new.csv")]
        print(f"Processing directory {directory} with {len(files)} files")

        for file in tqdm.tqdm(files):
            # convert the encoding of the file
            filename = file.split(".")[0]
            new_filename = filename + "_new.csv"
            
            path_old_file = path + "/" + file
            path_new_file = path + "/" + new_filename

            os.system(command.format(path_new_file, path_old_file, path_new_file, path_old_file))
    toc = time.time()

    print(f"Conversion took {toc - tic} seconds")