import gi
gi.require_version('Gtk', '3.0')
gi.require_version('PangoCairo', '1.0')

from .app import Application
from .gui_utils import FileListPreview
from .document import Document, DocMovie
from .shapes import *
from . import settings as Settings

DocumentShape.Loader = Document

from . import extras
