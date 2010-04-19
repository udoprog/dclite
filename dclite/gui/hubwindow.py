import gtk
import gobject

class HubWindow(gtk.HPaned):
  def __init__(self, label_text="Hub Window"):
    gtk.HPaned.__init__(self);
    
    self.label = gtk.Label(label_text);
    
    self.status = HubStatus();
    self.nicklist = HubNickList();
    
    self.pack1(self.status, True);
    self.pack2(self.nicklist, False);
    
    self.label.show();
    self.show_all();

    def on_connection_made(source):
      source.appendStatus("connected");
    
    def on_connection_lost(source, reason):
      source.appendStatus("disconnected: " + str(reason.value));
  
    def on_user_info(source, user):
      source.nicklist.update_user(user);
    
    def on_user_quit(source, user):
      source.nicklist.remove_user(user);
    
    def on_message(source, user, message):
      import datetime
      now = datetime.datetime.now().strftime("%H:%M:%S")
      source.appendStatus(now + " <" + user.nick + "> " + message);

    self.connect("connection_made", on_connection_made)
    self.connect("connection_lost", on_connection_lost)
    self.connect("user_info", on_user_info)
    self.connect("user_quit", on_user_quit)
    self.connect("message", on_message)
  
  def set_label(self, s):
    self.label.set_text(s);
  
  def appendStatus(self, s):
    self.status.append(s);

gobject.signal_new("input_message_submit", HubWindow, gobject.SIGNAL_RUN_FIRST,
  gobject.TYPE_NONE, [gobject.TYPE_STRING])

gobject.signal_new("on_message", HubWindow, gobject.SIGNAL_RUN_FIRST,
  gobject.TYPE_NONE, [gobject.TYPE_PYOBJECT, gobject.TYPE_STRING])

gobject.signal_new("hub_identified", HubWindow, gobject.SIGNAL_RUN_FIRST,
  gobject.TYPE_NONE, [gobject.TYPE_PYOBJECT])

gobject.signal_new("status", HubWindow, gobject.SIGNAL_RUN_FIRST,
  gobject.TYPE_NONE, [gobject.TYPE_PYOBJECT])

gobject.signal_new("user_info", HubWindow, gobject.SIGNAL_RUN_FIRST,
  gobject.TYPE_NONE, [gobject.TYPE_PYOBJECT])

gobject.signal_new("user_quit", HubWindow, gobject.SIGNAL_RUN_FIRST,
  gobject.TYPE_NONE, [gobject.TYPE_PYOBJECT])

gobject.signal_new("message", HubWindow, gobject.SIGNAL_RUN_FIRST,
  gobject.TYPE_NONE, [gobject.TYPE_PYOBJECT, gobject.TYPE_STRING])

gobject.signal_new("connection_made", HubWindow, gobject.SIGNAL_RUN_FIRST,
  gobject.TYPE_NONE, [])

gobject.signal_new("connection_lost", HubWindow, gobject.SIGNAL_RUN_FIRST,
  gobject.TYPE_NONE, [gobject.TYPE_PYOBJECT])

class HubStatus(gtk.VBox):
  delimiter = "\n";
  
  def __init__(self):
    gtk.VBox.__init__(self);
    self.text = gtk.TextView();
    self.text.set_editable(False);
    self.text.set_wrap_mode(gtk.WRAP_WORD);
    
    self.input = gtk.Entry();
    
    self.scrolledwindow = gtk.ScrolledWindow();
    self.scrolledwindow.add(self.text);
    self.scrolledwindow.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
    self.scrolledwindow.set_placement(gtk.CORNER_BOTTOM_LEFT);
    
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

  def _format_sharesize(self, ss):
    ss = float(ss);
    
    if ss >= 1024:
      ss = ss / 1024;
    else:
      return str(ss) + " B";
    
    if ss >= 1024:
      ss = ss / 1024;
    else:
      return str(ss) + " KiB";
    
    if ss >= 1024:
      ss = ss / 1024;
    else:
      return str(ss) + " MiB";
    
    if ss >= 1024:
      ss = ss / 1024;
    else:
      return str(ss) + " GiB";
    
    if ss >= 1024:
      ss = ss / 1024;
    else:
      return str(ss) + " TiB";
    
    return str(ss) + " PiB";
  
  def update_user(self, user):
    if user.sid in self.users:
      iter = self.users[user.sid];
      self.list.remove(iter);
    else:
      self.parent.appendStatus("User joined: " + user.nick);
    
    iter = self.list.append([user.nick, self._format_sharesize(user.sharesize)]);
    self.users[user.sid] = iter;
  
  def remove_user(self, user):
    if user.sid in self.users:
      iter = self.users[user.sid];
      self.list.remove(iter);
      self.users.pop(user.sid);
      self.parent.appendStatus("User quit: " + user.nick);
