from owade.fileAnalyzer import programAnalyze
from owade.fileExtractor import extract

x = extract.GetFiles()
x.extractFiles("/media/lannister/TOSHIBA EXT/storage/image/777666AA_image","/media/lannister/TOSHIBA EXT/storage/ftp")

p = programAnalyze.ProgramAnalyze()
p.analyze("/media/lannister/TOSHIBA EXT/storage/ftp/777666AA_image_3")