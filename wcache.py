# Python Verstion: 2.7


# imports
import urlparse
import urllib2


# An LFU web cache
class cache():
	# static members
	block_delimiter = chr(0x07)
	key_delimiter = chr(0x13)


	# cache: Integer, String String -> cache
	# Returns: a cache of the given capacity(in bytes) initialized
	# with the contents of the given filename.
	def __init__(self, capacity, origin_name, file_name):
		self.capacity = capacity
		self.origin_name = origin_name
		self.file_name = file_name
		self.size = 0
		# LFU: hottest entry at tail
		self.accessed = []
		self.mappings = self.__load_from_persistence__(self.file_name)


	def __load_from_persistence__(self, file_name):
		contents = None
		if os.path.isfile(file_name):
			fp = open(file_name, 'r')
			contents = fp.read()
			fp.close()
		else:
			fp = open(file_name, 'w+')
			fp.write(cache.block_delimiter)
			fp.close()
			contents = cache.block_delimiter
		return self.__generate_map__(contents)

	def __generate_map__(self, contents):
		mappings = {}
		if contents == None:
			return mappings
		contents = contents.split(cache.block_delimiter)
		for block in contents:
			if block != '':
				if cache.key_delimiter in block:
					key, value = block.split(cache.key_delimiter)
					mappings[key] = value
					self.accessed.append(key)
					self.size += len(value)
		return mappings


	def get(self, key):
		if key in self.mappings:
			self.accessed.remove(key)
			self.accessed.append(key)
			return self.mappings[key]
		return None
		

	def fetch_from_origin(self, path):
		url = urlparse.urlunparse(('http', self.origin_name, path, '', '', ''))
		return urllib2.urlopen(url).read()


	def add(self, key, value):
		if key not in self.mappings:
			if len(value) > self.capacity:
				print('Size greater than cache capacity. Exiting')
				sys.exit(1)
			self.__check_and_evict__(len(value))

			self.accessed.append(key)
			self.mappings[key] = value
			self.size += len(value)


	def __check_and_evict__(self, size):
		if self.size + size > self.capacity:
			i = 0
			total_size = 0
			while total_size <= size:
				total_size += len(self.mappings[self.accessed[i]])
				i += 1
			j = 0
			for j in range(i):
				self.__evict__(self.accessed[j])
			self.accessed = self.accessed[j:]


	def __evict__(self, key):
		self.size -= len(self.mappings.pop(key))


	def sync_persistence(self):
		contents = ''
		for key,value in self.mappings.iteritems():
			contents += key + cache.key_delimiter + value + cache.block_delimiter
		fp = open(self.file_name, 'w+')
		fp.write(contents)
		fp.close()

