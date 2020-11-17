import getopt, sys
from moviedb import movieDB as mdb


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
            
    test = mdb(title, True)
    print('Total results:=',test.result_count)
    
if __name__ == "__main__":
    main()