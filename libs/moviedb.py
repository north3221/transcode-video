import sys, re, urllib.request as r, urllib.error as err, json

class movieDB:

	def __init__(self, title):
		self.title = None
		# split so if was provided with _s etc
		self.__search = re.split('\s|_|-|\n', title)
		self.__setInfo()
		
	def __setrequest(self):
		url = 'https://api.themoviedb.org/3/search/movie?'
		# Likely should use keystore or env var etc - but think this will do..
		try:
			with open('config/secret/api-key', 'r') as apik:
				api_key = apik.read()
		except:
			print('Issue getting your api-key, have you set it up? Check README for info')
			exit(2)

		self.__url = url + 'api_key=' + api_key

	def __getMovieDBresponse(self):
		query_url = '&query=' + '+'.join(self.__search)
		req = r.Request(self.__url + query_url)
		try:
			response = r.urlopen(req)

		except err.HTTPError as e:		
			print('issue getting movie db info, error code:=', e.getcode())
			exit(2)
		
		self.__result = json.loads(response.read().decode('utf-8'))['results']

	def __getInfo(self):
		self.__setrequest()
		self.__getMovieDBresponse()
		# Blurays sometimes have movie stufio etc at the beggining of the name so if nothing found pop them out until down to one word
		while len(self.__result) == 0 and len(self.__search) > 1:
			self.__search.pop(0)
			self.__getMovieDBresponse()
			
	def __setInfo(self):
		self.__getInfo()
		if len(self.__result) > 0:
			for key in self.__result[0]:
				exec("self." + key + " = " + self.__clean(self.__result[0][key]))
				
	def __clean(self,val):
		return "'''" + re.sub('[\\|//|:]', '', str(val)) + "'''"
		
				
