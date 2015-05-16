# wcache
An implementation of an LFU web cache in Python.

# Example

**The following code uses the cache with a write-behind policy to enhance performance.**

```python
# A daemon that keeps persisting the cache to disk at the given frequency in seconds
def write_to_persistence(frequency):
	global web_cache, cache_lock, terminate_wb
	while terminate_wb:
		time.sleep(frequency)
		with cache_lock:
			web_cache.sync_persistence()

# A function that prints the web page given its URL
def get(path):
	global web_cache, cache_lock
	contents = web_cache.get(path)
	if contents != None:
		print(contents)
	else:
		contents = web_cache.fetch_from_origin(path)
		print(contents)
		with cache_lock:
			web_cache.add(path, contents)

if __name__ == '__main__':
	import threading
	import wcache
	
	global web_cache, cache_lock, terminate_wb
	
	# wcache(size_in_bytes, origin_server, persistence_file_name)
	# 16 MB cache
	web_cache = wcache.cache(16*(2**20), 'www.originserver.com', 'cache_data.txt')

	cache_lock = threading.Lock()
	
	terminate_wb = False

	# commit frequency(seconds)
	# daemon executes every 5 minutes and persists to disk.
	commit_frequency = 5*60

	wb_daemon = threading.Thread(target=write_to_persistence, args=(commit_frequency,))
	wb_daemon.start()
	
	path = None
	while True:
		path = input('Enter a URL:')
		get(path)
	terminate_wb = False
```
