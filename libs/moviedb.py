import re, urllib.request as r, urllib.error as err, json, os.path as osp

class movieDB:

    def __init__(self, title, dump=False):
        print('Checking Movie DB for info..........')
        self.title = None
        self.match = 0
        self.__dump = dump
        # split so if was provided with _s etc
        self.__search = re.split('\s|_|-|\n', title)
        self.__setInfo()
        
    def __setrequest(self):
        url = 'https://api.themoviedb.org/3/search/movie?'
        # TODO Likely should use keystore or env var etc - but think this will do..
        try:
            with open(osp.realpath(osp.join(osp.dirname(osp.abspath(__file__)),'../config/secret/api-key')), 'r') as apik:
                api_key = apik.read()
        except:
            print('Issue getting your api-key, have you set it up? Check README for info')
            exit(2)

        self.__url = url + 'api_key=' + api_key

    def __getMovieDBresponse(self, search):
        query_url = '&query=' + '+'.join(search)
        req = r.Request(self.__url + query_url)
        try:
            response = r.urlopen(req)

        except err.HTTPError as e:      
            print('issue getting movie db info, error code:=', e.getcode())
            exit(2)
        response = json.loads(response.read().decode('utf-8'))
        if self.__dump: print('RESPONSE :',response)
        results = response['results']
        # function for list sort key
        def release_date(res):
            try:
                return res['release_date']
            except KeyError:
                return '1900-01-01'
        results.sort(key=release_date, reverse=True)
        self.__result = results

    def __getInfo(self):
        self.__setrequest()
        self.__getMovieDBresponse(self.__search)
        # Blurays sometimes have movie studio etc at the beginning of the name so if nothing found pop them out until down to one word
        search = self.__getCleanSearch()
        while len(self.__result) == 0 and len(search) > 1:
            search.pop(0)
            self.__getMovieDBresponse(search)
        # Try the other way round as some have info on the end of the bluray name
        search = self.__getCleanSearch()
        while len(self.__result) == 0 and len(search) > 1:
            search.pop()
            self.__getMovieDBresponse(search)
            
    def __getCleanSearch(self):
        cleanSearch = self.__search[:]
        # remove 'UHD'from title to ensure it doesn't interfere with movie db search
        try:
            cleanSearch.remove('Uhd')
        except:
            pass
        return cleanSearch
        
        
    def __setInfo(self):     
        self.__getInfo()
        self.result_count = len(self.__result)
        if self.result_count > 0:
            print('Movie info found...........')
            match_count = 0
            
            for result in self.__result:
                if result['title'] == ' '.join(self.__search):
                    #title match and only do first match
                    if self.title == None: self.__setKeys(result)
                    match_count = match_count + 1
            if self.title != None:
                self.match  = 100 - ((match_count - 1)*10)
            else:
                self.__setKeys(self.__result[0])
                self.match=50
                
            print(self.match,'% match')
            self.x264_tune = None
            if '16' in self.genre_ids:
                print('Animation found............')
                self.x264_tune = 'animation'   
    
                
    def __setKeys(self, result):
        for key in result:
            exec("self." + key + " = " + self.__clean(result[key]))
            if self.__dump: print(key,':', result[key])
        
    def __clean(self,val):
        return "'''" + re.sub('[\\|//|:]', '', str(val)) + "'''"
        
                
