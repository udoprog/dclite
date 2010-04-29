from .hubwindow import HubWindow
from .downloadlist import DownloadList

from ..highprotocol import HubFactory

from .. import utils

from twisted.internet import reactor

import gtk

import urlparse
import time

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
    "time_label",
    "speed_up_label",
    "speed_down_label",
    "main_statusbar",
  ];
  
  def __bind(self, getter):
    for w in self.widgets:
        wi = getter(w);
        assert wi is not None, "could not find widget: " + w;
        setattr(self, w, wi);
  
  def __init__(self, b):
    # speed lists, which contains a set of bytes which has been acquired since last poll
    self.speed_up = 0;
    self.speed_down = 0;
    
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
    
    self.entry = dl.createEntry(nick="nick4", status="Wider STATUS STUFF", progress=10, progress_text="TEST1");
    
    self.update_time()
    self.update_speeds();
  
  def push_status(self, message, context="Main"):
    context_id = self.main_statusbar.get_context_id(context)
    self.main_statusbar.push(context_id, message)
  
  def pop_status(self, context="Main"):
    context_id = self.main_statusbar.get_context_id(context)
    self.main_statusbar.pop(context_id)
  
  def add_speed_up(self, kb):
    self.speed_up += kb;
  
  def add_speed_down(self, kb):
    self.speed_down += kb;
  
  def update_time(self):
    self.now = time.time()
    self.time_label.set_text(time.strftime("%H:%M:%S"));

    self.speed_up += 1024 ** 5;
    
    # queue the next time update
    reactor.callLater(1 - (self.now % 1), self.update_time)
  
  def update_speeds(self):
    self.speed_up_label.set_text(utils.format_bandwidth(self.speed_up * 10))
    self.speed_down_label.set_text(utils.format_bandwidth(self.speed_down * 10))
    
    self.speed_up = 0;
    self.speed_down = 0;
    # queue the next time update
    reactor.callLater(1, self.update_speeds)
  
  def submit_quick_connect(self, source):
    uri = self.quick_connect_uri.get_text();

    parts = uri.split(":");
    
    if len(parts) == 1:
      host, port = parts[0], DEFAULT_PORT;
    else:
      host, port = parts[0], int(parts[1]);

    self.push_status("Connecting to hub: " + uri)
    
    self.connectHub(host, port);
    self.close_quick_connect(source);

  def connectHub(self, host, port):
    hub = self.newHub(host + ":" + str(port));
    
    connector = reactor.connectTCP(host, port, HubFactory(hub))
    
    hub.connect("connection-made", lambda _: self.push_status("Connection made: " + hub.get_name()))
    hub.connect("connection-lost", lambda _: self.push_status("Connection lost to: " + hub.get_name()))
    hub.connect("destroy", lambda _: connector.disconnect())
    hub.connect("on-message", lambda _, user, message: hub.appendStatus(time.strftime("%H:%M:%S") + " <" + user.nick + "> " + message))
    
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
