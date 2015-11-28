import subprocess

import lib
from owade.constants import PROJECT_DIR, PROJECT_NAME, HASHCAT_DIR
import os

class PwDump(object):

    def __init__(self):
        pass

    def main(self, system, sam):
        """


        :rtype : object
        :param system:
        :param sam:
        :return:
        """
        user_hash = lib.dump_file_hashes(system, sam)
        elementos = user_hash.items()
        final_pass = dict()

        for username, mihash in elementos:
            print username
            print mihash
            print os.getcwd()
            fileRoute = HASHCAT_DIR + "/hash.txt"

            hash_file = open(fileRoute, 'w')
            hash_file.write(mihash + "\n")
            hash_file.close()
            subprocess.check_output(
                HASHCAT_DIR + "/hashcat-cli64.bin -m 1000 --rules=" + HASHCAT_DIR + "/perfect.rule " + fileRoute + " " + HASHCAT_DIR +
                "/rockyou.txt --outfile-format=2 --outfile=resultado.txt",
                shell=True)

            # Lectura del fichero creado
            f = open('resultado.txt', 'r+')
            for line in f.readlines():
                passwords = line.strip()
                if len(passwords) > 0:
                    final_pass[username] = passwords
            f.close()
            subprocess.check_output("rm resultado.txt", shell=True)
        # final pass returns dicctionary  that contains user -> password cracked
        return final_pass
