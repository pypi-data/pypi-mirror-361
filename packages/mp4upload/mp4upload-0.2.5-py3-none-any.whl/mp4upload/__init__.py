from __future__ import unicode_literals
from .__meta__ import __version__, __version_info__  # noqa: F401
from . mp4upload import Mp4upload
try:
	from . import __version__ as vv
	version = vv
except:
	pass