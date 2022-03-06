import getopt, sys, os.path as osp
sys.path.insert(0, osp.dirname(osp.dirname(osp.abspath(__file__))))

from libs import subs
from libs.videoInput import videoInput as vi


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:],"t:",["title="])
        if len(opts) == 0:
            print('No Input provided')
    except getopt.GetoptError:
        print ('Invalid input ', sys.argv[1:] )
    for opt, arg in opts:
        if opt in ("-t", "--title"):
            title = arg
    
    # Test append
    #subs.subsAppend(title, 8)
    
    # Test backup
    subs.subsBackup(vi(title))


main()



