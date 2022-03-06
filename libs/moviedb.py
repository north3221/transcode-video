import re, urllib.request as r, urllib.error as err, json, os.path as osp

class movieDB:

    def __init__(self, title, user_check=False, dump=False):
        print('Checking Movie DB for info..........')
        self.title = None
        self.match = 0
        self.__dump = dump
        self.__api_key = None
        # split so if was provided with _s etc
        self.__search = re.split('\s|_|-|\n', title)
        self.__setInfo(user_check)
        
    def __setrequest(self):
        url = 'https://api.themoviedb.org/3/search/movie?'
        # TODO Likely should use keystore or env var etc - but think this will do..
        try:
            with open(osp.realpath(osp.join(osp.dirname(osp.abspath(__file__)),'../config/secret/api-key')), 'r') as apik:
                self.__api_key = apik.read()
        except:
            print('Issue getting your api-key, have you set it up? Check README for info')
            exit(2)

        self.__url = url + 'api_key=' + self.__api_key

    def __getMovieDBresponse(self, search):
        query_url = '&query=' + '+'.join(search)
        req = r.Request(self.__url + query_url)
        if self.__dump: print('REQUEST :',self.__url + query_url)
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
        #If still nothing put space between number
        search = self.__getCleanSearch()
        digits = sum(c.isdigit() for s in search for c in s)
        if digits > 0:  
            for s in search:
                if len(self.__result) == 0:
                    new_search = []
                    letters = (''.join(list(filter(str.isalpha, s))))
                    digits = (''.join(list(filter(str.isdigit, s))))
                    # first with '=' so only search movie db for this title
                    new_search.append('=' + letters + '%20' + digits)
                    self.__getMovieDBresponse(new_search)
                    if len(self.__result) > 0:
                        break
                    # try without '=' to search all
                    new_search = []
                    new_search.append(letters + '%20' + digits)
                    self.__getMovieDBresponse(new_search)

                        
    def __getCleanSearch(self):
        cleanSearch = self.__search[:]
        remove_list = ['UHD', 'UPK1', 'UPK2', 'UPB1']
        for remove in remove_list:
            try:
                cleanSearch.remove(remove)
            except:
                pass
                
        return cleanSearch
        
        
    def __setInfo(self, user_check):
        self.__getInfo()
        self.result_count = len(self.__result)
        if self.result_count == 0:
            print('No movie db results to check')
            return      
        print('Movie info found...........')

        if user_check:
            for i in range(0,self.result_count):
                print(i, ':', self.__result[i]['title'], self.__result[i]['release_date'])
            user_input = input('Please input the number of the correct movie db result: ')
            try:
                self.__setKeys(self.__result[int(user_input)])
            except:
                pass
        else:  
            match_count = 0
            for result in self.__result:
                if result['title'].replace(':', ' ').lower() == ' '.join(self.__search).lower():
                    # title match and only do first match
                    if self.title == None: self.__setKeys(result)
                    match_count = match_count + 1
            if self.title != None:
                self.match  = 100 - ((match_count - 1)*10)
            else:
                self.__setKeys(self.__result[0])
                self.match=50         
            print(self.match,'% match')
        
        self.x264_tune = None
        
        if len(self.genre_ids.strip('[]')) > 0:
            self.genre_ids = self.genre_ids.strip('[]').split(',')
            self.__setGenre()
            if 'Animation' in self.genres:
                print('Animation found............')
                self.x264_tune = 'animation'  
             
    
                
    def __setKeys(self, result):
        for key in result:
            exec("self." + key + " = " + self.__clean(result[key]))
            if self.__dump: print(key,':', result[key])
        
    def __clean(self,val):
        return "'''" + re.sub('[\\|//|:\']', '', str(val)) + "'''"
        
    def __setGenre(self):
        self.genre = None
        self.genres = []
        url= 'https://api.themoviedb.org/3/genre/movie/list?' + 'api_key=' + self.__api_key + '&query=12'
        req = r.Request(url)
        try:
            response = r.urlopen(req)
            response = json.loads(response.read().decode('utf-8'))
        except err.HTTPError as e:      
            print('issue getting movie db genre info, error code:=', e.getcode())
            print('using default')
            response = {'genres': [{'id': 28, 'name': 'Action'}, {'id': 12, 'name': 'Adventure'}, {'id': 16, 'name': 'Animation'}, {'id': 35, 'name': 'Comedy'}, {'id': 80, 'name': 'Crime'}, {'id': 99, 'name': 'Documentary'}, {'id': 18, 'name': 'Drama'}, {'id': 10751, 'name': 'Family'}, {'id': 14, 'name': 'Fantasy'}, {'id': 36, 'name': 'History'}, {'id': 27, 'name': 'Horror'}, {'id': 10402, 'name': 'Music'}, {'id': 9648, 'name': 'Mystery'}, {'id': 10749, 'name': 'Romance'}, {'id': 878, 'name': 'Science Fiction'}, {'id': 10770, 'name': 'TV Movie'}, {'id': 53, 'name': 'Thriller'}, {'id': 10752, 'name': 'War'}, {'id': 37, 'name': 'Western'}]}
        
        genre_ids=[]
        for id in self.genre_ids:
            genre_ids.append(int(id))
        for genre in response['genres']:
            if genre['id'] in genre_ids:
                self.genres.append(genre['name'])
                if genre['id'] == genre_ids[0]:
                    self.genre=genre['name']
