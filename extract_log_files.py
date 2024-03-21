import os

BASE_PATH = './data/logs'


def unzip_log_files(zip_file):

    # Each ZIP file contains MULTIPLE *.logjez files
    # Each A.logjez file contains a logd.dat file that is the LOG file
    # This code extract all A.logjez file and rename its logd.dat to A.csv

    # unzip file
    # extracting only the .logjez files
    filepath = zip_file[:-4]
    os.system(f'7z e {zip_file} -o{filepath} *.logjez -r')

    # Remove unnecessary files
    os.system(f'rm {zip_file}')  # Zip file

    # list all files in the directory
    files = os.listdir(filepath)

    for file in files:
        # extract .logjez files
        # and rename to .csv
        if file.endswith('.logjez'):
            new_filename = file[:-7]
            os.system(
                f'7z e {filepath}/{file} -y -o{filepath}/{new_filename} \
                > /dev/null'
            )
            os.system(
                f'mv \
                {filepath}/{new_filename}/logd.dat \
                {filepath}/{new_filename}.csv'
            )
            os.system(
                f'rm -r {filepath}/{new_filename}'
            )

    os.system(f'chmod 777 -R {filepath}')
    os.system(f'rm {filepath}/*.logjez')


if __name__ == "__main__":
    for file in os.listdir(BASE_PATH):
        if file.endswith('.zip'):
            unzip_log_files(os.path.join(BASE_PATH, file))