from adc.logger import Logger
from twisted.internet import reactor

from .highprotocol import HubFactory

class StatusFile:
  def __init__(self, cb):
    self.cb = cb;
  
  def write(self, s):
    self.cb(s);

import gtk
import gtk.glade

class HubStatus(gtk.VBox):
  delimiter = "\n";
  
  def __init__(self):
    gtk.VBox.__init__(self);
    self.text = gtk.TextView();
    self.text.set_editable(False);

    self.input = gtk.Entry();
    
    self.pack_start(self.text, True, True, 0)
    self.pack_start(self.input, False, False, 0)

    self.input.connect("activate", self.send_message)

    self.show_all();
  
  def append(self, s):
    buf = self.text.get_buffer();
    buf.insert_at_cursor(s + self.delimiter);
  
  def send_message(self, source):
    message = source.get_text();
    source.set_text("");
    self.parent.protocol.sendMessage(message);

class HubNickList(gtk.TextView):
  pass;

class HubWindow(gtk.HPaned):
  def __init__(self, tabs):
    gtk.HPaned.__init__(self);

    self.show();
    self.tabs = tabs;

    self.status = HubStatus();
    self.nicklist = HubNickList();

    self.add1(self.status);
    self.add2(self.nicklist);
    
    self.protocol = None;
  
  def setProtocol(self, protocol):
    self.protocol = protocol;
  
  def set_label(self, s):
    self.tabs.set_tab_label_text(self, s);
  
  def printStatus(self, s):
    self.status.append(s);

class GtkGui:
  widgets = [
    "main_window",
    "main_tabs",
    "quick_connect_window",
    "quick_connect_scheme",
    "quick_connect_uri",
    "quick_connect_cancel_btn",
    "quick_connect_connect_btn",
  ];

  def __bind(self):
    for w in self.widgets:
      if type(w) == tuple:
        wn, wf = w;
        wi = self.root.get_widget(wn);
        assert wi is not None, "could not find widget: " + w;
        wf(wi)
        setattr(self, wn, wi);
      else:
        wi = self.root.get_widget(w);
        assert wi is not None, "could not find widget: " + w;
        setattr(self, w, wi);
  
  def __init__(self, gladefile):
    self.root = gtk.glade.XML(gladefile);
    
    self.__bind();
    
    self.signals = {
      "open_quick_connect": self.open_quick_connect,
      "submit_quick_connect": self.submit_quick_connect,
      "close_quick_connect": self.close_quick_connect,
    };

    self.root.signal_autoconnect(self.signals);

  def submit_quick_connect(self, source):
    uri = self.quick_connect_uri.get_text();
    scheme = self.quick_connect_scheme.get_active_text();

    host, port = uri.split(":");

    hub = self.newHub(uri);
    reactor.connectTCP(host, int(port), HubFactory(hub));
    self.close_quick_connect(source);

  def open_quick_connect(self, source):
    self.quick_connect_window.show();
  
  def close_quick_connect(self, source):
    self.quick_connect_window.hide();
  
  def newHub(self, s):
    hub = HubWindow(self.main_tabs);
    self.main_tabs.append_page(hub, gtk.Label(s));
    self.main_tabs.set_tab_reorderable(hub, True);
    return hub;
