import gtk
import gobject

from .. import utils

class HubWindow(gtk.HPaned):
  __gsignals__ = {
    # when an input message is submitted
    "input-message-submit": (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_STRING,)),
    
    # when the hub has been identified
    "hub-identified": (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
    
    # emitted when status has been received on the hub
    "status": (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
    
    # emitted when user info has been received
    "user-info": (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
    
    # emitted when a user quits on this hub
    "user-quit": (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
    
    # emitted when a message is received on this hub
    "message": (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, gobject.TYPE_STRING)),
    
    # emitted when a connection is made on this hub
    "connection-made": (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, tuple()),
    
    # emitted when a connection is lost on this hub
    "connection-lost": (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, )),
  };
  
  def __init__(self, label_text="Hub Window"):
    gtk.HPaned.__init__(self);

    self.__name = label_text
    
    self.label = gtk.Label(self.__name);
    
    self.status = HubStatus();
    self.nicklist = HubNickList();
    
    self.pack1(self.status, True);
    self.pack2(self.nicklist, False);
    
    self.label.show();
    self.show_all();
    
    self.connect("connection-made", lambda _: self.appendStatus("connected"))
    self.connect("connection-lost", lambda _, reason: self.appendStatus("disconnected: " + str(reason.value)))
    self.connect("user-info", lambda _, user: self.nicklist.update_user(user))
    self.connect("user-quit", lambda _, user: self.nicklist.remove_user(user))
    self.connect("message", lambda _, user, message: self.appendStatus(time.strftime("%H:%M:%S") + " <" + user.nick + "> " + message))

  def get_name(self):
    return self.__name;

  def set_name(self, name):
    self.label.set_text(name)
    self.__name = name
  
  name = property(get_name, set_name)
  
  def appendStatus(self, s):
    self.status.append(s);

class HubStatus(gtk.VBox):
  delimiter = "\n";
  
  def __init__(self):
    gtk.VBox.__init__(self);
    self.text = gtk.TextView();
    self.text.set_editable(False);
    self.text.set_wrap_mode(gtk.WRAP_WORD);
    self.text.set_left_margin(4)
    self.text.set_right_margin(4)
    
    self.input = gtk.Entry();
    
    self.scrolledwindow = gtk.ScrolledWindow();
    self.scrolledwindow.add(self.text);
    self.scrolledwindow.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
    self.scrolledwindow.set_placement(gtk.CORNER_BOTTOM_LEFT)

    def on_size_allocate(source, event):
      adj = self.scrolledwindow.get_vadjustment();
      adj.set_value(adj.get_upper() - adj.get_page_size());
    
    self.text.connect("size-allocate", on_size_allocate)
    
    self.pack_start(self.scrolledwindow, True, True)
    self.pack_start(self.input, False, False)
    
    self.input.connect("activate", self.send_message)
    
    #self.set_border_width(4);
    self.set_spacing(4);
    self.show_all();
  
  def append(self, s):
    buf = self.text.get_buffer();
    buf.insert_at_cursor(s + self.delimiter);

  def send_message(self, source):
    message = source.get_text();
    source.set_text("");
    self.parent.emit("input_message_submit", message);

class HubNickList(gtk.TreeView):
  def __init__(self):
    gtk.TreeView.__init__(self);
    
    self.list = gtk.ListStore(str, str);
    
    col1 = gtk.TreeViewColumn("Nick")
    col2 = gtk.TreeViewColumn("Share")
    
    cell = gtk.CellRendererText();
    col1.pack_start(cell, True);
    col1.add_attribute(cell, 'text', 0)
    col1.set_sort_order(gtk.SORT_DESCENDING);
    col1.set_sort_column_id(0);
    
    cell = gtk.CellRendererText();
    col2.pack_start(cell, True);
    col2.add_attribute(cell, 'text', 1)
    col2.set_sort_order(gtk.SORT_DESCENDING);
    col2.set_sort_column_id(1);
    
    self.set_model(self.list);
    self.append_column(col1);
    self.append_column(col2);
    
    def on_event(source, n):
      if source.get_sort_order() == gtk.SORT_ASCENDING:
        source.set_sort_order(gtk.SORT_DESCENDING);
      else:
        source.set_sort_order(gtk.SORT_ASCENDING);
      
      source.set_sort_column_id(n);
    
    col1.connect("clicked", on_event, 0);
    col2.connect("clicked", on_event, 1);
    
    self.users = dict();
  
  def update_user(self, user):
    if user.sid in self.users:
      iter = self.users[user.sid];
      self.list.remove(iter);
    else:
      self.parent.appendStatus("User joined: " + user.nick);
    
    iter = self.list.append([user.nick, utils.format_bytes(user.sharesize)]);
    self.users[user.sid] = iter;
  
  def remove_user(self, user):
    if user.sid in self.users:
      iter = self.users[user.sid];
      self.list.remove(iter);
      self.users.pop(user.sid);
      self.parent.appendStatus("User quit: " + user.nick);
