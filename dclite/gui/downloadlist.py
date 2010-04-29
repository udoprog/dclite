import gtk

class DownloadEntry:
  def __init__(self, list, **kw):
    self.list = list;
    self.iter = None;
    
    self.nick = kw.get("nick", "No Nick");
    self.status = kw.get("status", "No Status");
    self.progress = kw.get("progress", 0);
    self.progress_text = kw.get("progress_text", "");
    self.update();
  
  def update(self, **kw):
    if "nick" in kw:            self.nick = kw.get("nick");
    if "status" in kw:          self.status = kw.get("status");
    if "progress" in kw:        self.progress = kw.get("progress");
    if "progress_text" in kw:   self.progress_text = kw.get("progress_text");
    
    if self.iter is None:
      self.iter = self.list.append([self.nick, self.status, self.progress, self.progress_text]);
    else:
      self.list.set(self.iter, 0, self.nick, 1, self.status, 2, self.progress, 3, self.progress_text);
  
  def destroy(self):
    self.list.remove(self.iter);

class DownloadList(gtk.TreeView):
  def __init__(self):
    gtk.TreeView.__init__(self);
    
    self.list = gtk.ListStore(str, str, int, str);
    col1 = gtk.TreeViewColumn("Nickname")
    col2 = gtk.TreeViewColumn("Status")
    col3 = gtk.TreeViewColumn("Progress");

    col1.set_clickable(True);
    col1.set_reorderable(True);
    col1.set_sort_order(gtk.SORT_DESCENDING);
    col1.set_sort_column_id(0);

    col2.set_clickable(True);
    col2.set_reorderable(True);
    col2.set_sort_order(gtk.SORT_DESCENDING);
    col2.set_sort_column_id(1);

    col3.set_clickable(True);
    col3.set_reorderable(True);
    col3.set_sort_order(gtk.SORT_DESCENDING);
    col3.set_sort_column_id(2);
    
    cell = gtk.CellRendererText();
    col1.pack_start(cell, False);
    col1.add_attribute(cell, 'text', 0)
    
    cell = gtk.CellRendererText();
    col2.pack_start(cell, False);
    col2.add_attribute(cell, 'text', 1)
    
    cell = gtk.CellRendererProgress();
    col3.pack_start(cell, True);
    col3.add_attribute(cell, 'value', 2)
    col3.add_attribute(cell, 'text', 3)

    def on_event(source, n):
      if source.get_sort_order() == gtk.SORT_ASCENDING:
        source.set_sort_order(gtk.SORT_DESCENDING);
      else:
        source.set_sort_order(gtk.SORT_ASCENDING);
      
      source.set_sort_column_id(n);
    
    col1.connect("clicked", on_event, 0);
    col2.connect("clicked", on_event, 1);
    col3.connect("clicked", on_event, 2);
    
    self.set_model(self.list);
    self.append_column(col1);
    self.append_column(col2);
    self.append_column(col3);

  def createEntry(self, **kw):
    return DownloadEntry(self.list, **kw);
