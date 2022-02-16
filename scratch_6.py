import ftputil
password = "locatepassword"
def connectFTP():
    return ftputil.FTPHost("redlocate.free.bg","redlocate.free.bg",password)

connectFTP()

with connectFTP() as ftp:
    ftp.upload(f"favicon/favicon.ico", 'f.ico')