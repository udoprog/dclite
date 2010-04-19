from .hubwindow import HubWindow
from .downloadlist import DownloadList

from ..highprotocol import HubFactory

from twisted.internet import reactor

import gtk

import urlparse

DEFAULT_PORT=1511
ADC_SCHEME="adc"
ADCS_SCHEME="adcs"

urlparse.uses_netloc.append(ADC_SCHEME)
urlparse.uses_netloc.append(ADCS_SCHEME)
    
class GtkGui:
  widgets = [
    "main_window",
    "quick_connect_uri",
    "quick_connect_window",
    "main_tabs",
    "download_list",
    "main_status",
    "aboutdialog",
  ];
  
  def __bind(self, getter):
    for w in self.widgets:
        wi = getter(w);
        assert wi is not None, "could not find widget: " + w;
        setattr(self, w, wi);
  
  def __init__(self, b):
    if isinstance(b, gtk.Builder):
      self.getter = b.get_object;
      self.__bind(self.getter);
      b.connect_signals(self);
    else:
      self.getter = b.get_widget;
      self.__bind(self.getter);
      b.signal_autoconnect(self);
    
    dl = DownloadList()
    self.download_list.add(dl)
    
    entry = dl.createEntry(nick="nick4", status="Wider STATUS STUFF", progress=10, progress_text="TEST1");
    entry = dl.createEntry(nick="nick5", progress=11, progress_text="TEST2");
    entry = dl.createEntry(nick="nick6", progress=12, progress_text="TEST3");
    entry = dl.createEntry(nick="nick2", progress=13, progress_text="TEST4");
    entry = dl.createEntry(nick="nick3", progress=14, progress_text="TEST5");
    entry = dl.createEntry(nick="nick1", progress=15, progress_text="TEST6");
    entry.destroy();
  
  def submit_quick_connect(self, source):
    uri = self.quick_connect_uri.get_text();

    parts = uri.split(":");
    
    if len(parts) == 1:
      host, port = parts[0], DEFAULT_PORT;
    else:
      host, port = parts[0], int(parts[1]);
    
    self.connectHub(host, port);
    self.close_quick_connect(source);

  def connectHub(self, host, port):
    hub = self.newHub(host + ":" + str(port));
    
    connector = reactor.connectTCP(host, port, HubFactory(hub))
    
    def on_destroy(source):
      connector.disconnect();
    
    hub.connect("destroy", on_destroy)

    self.main_window.show_all();
  
  def open_quick_connect(self, source):
    self.quick_connect_window.show();
  
  def close_quick_connect(self, source):
    self.quick_connect_window.hide();
  
  def open_aboutdialog(self, source):
    self.aboutdialog.show();
  
  def close_aboutdialog(self, source):
    self.aboutdialog.hide();

  def gtk_main_quit(self, source):
    reactor.stop();
  
  def appendStatus(self, s):
    buffer = self.main_status.get_buffer();
    buffer.append_at_cursor(s + "\n");

  def addTab(self, widget, label, focus=True):
    label_box = gtk.EventBox();
    label_box.add(label);
    label_box.show();
    
    def on_tab_click(self, event, tabs, widget):
      if event.type == gtk.gdk.BUTTON_PRESS:
        # this will automagically switch to whatever page you click on
        if event.button == 2:
          tabs.remove_page(tabs.page_num(widget));
          widget.destroy();
    
    label_box.connect("event", on_tab_click, self.main_tabs, widget);
    self.main_tabs.append_page(widget, label_box);
    self.main_tabs.set_tab_reorderable(widget, True);
    
    if focus:
      self.main_tabs.set_current_page(self.main_tabs.page_num(widget));
  
  def newHub(self, s):
    hub = HubWindow(s);
    self.addTab(hub, hub.label);
    return hub;
