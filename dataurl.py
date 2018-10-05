import binascii
try:
    from urllib.parse import unquote_to_bytes
except:
    from urllib2 import unquote, toBytes
    def unquote_to_bytes(*args, **kwargs):
        return toBytes(unquote(*args, **kwargs))
import email.message
import io

from werkzeug.datastructures import FileStorage

__all__ = ['parse_data_url','DataResponse','DataHandler', 'DataURLStorage']

def parse_data_url(url):
	scheme, data = url.split(":",1)
	assert scheme == "data", "unsupported scheme: "+scheme
	content_type, data = data.split(",",1)
	# base64 urls might have a padding which might (should) be quoted:
	data = unquote_to_bytes(data)
	if content_type.endswith(";base64"):
		return binascii.a2b_base64(data), content_type[:-7] or None
	else:
		return data, content_type or None

class DataURLStorage(FileStorage):
    def __init__(self, url, filename=None, name=None):
        data, content_type = parse_data_url(url)
        stream = io.BytesIO(data)
        FileStorage.__init__(self, stream=stream, filename=filename, content_type=content_type, content_length=len(data))
        
    
# DataResponse exposes the mediatype and emulates some methods/properties of
# HTTPResponse: msg, headers, length, info, geturl, getheader and getheaders
class DataResponse(io.BytesIO):
	__slots__ = 'url','mediatype','msg','headers','length'
	def __init__(self,url):
		data, mediatype = parse_data_url(url)
		io.BytesIO.__init__(self,data)
		self.url = url
		self.mediatype = mediatype
		self.length = len(data)
		self.headers = self.msg = email.message.Message()
		if mediatype is not None:
			self.msg.add_header("Content-Type",mediatype)
	
	def getheader(self,name,default=None):
		headers = self.headers.get_all(name) or default
		if isinstance(headers, str) or not hasattr(headers, '__iter__'):
			return headers
		else:
			return ', '.join(headers)
	
	def getheaders(self):
		return list(self.headers.items())
	
	def geturl(self):
		return self.url
	
	def info(self):
		return self.headers

