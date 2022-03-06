import getopt, sys, os.path as osp
sys.path.insert(0, osp.dirname(osp.dirname(osp.abspath(__file__))))
from libs.moviedb import movieDB as mdb

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
            
    test = mdb(title, dump=True)
    #test = mdb(title)
    print('Total results:=',test.result_count)
    print('Title:= ', test.title)
    
if __name__ == "__main__":
    main()