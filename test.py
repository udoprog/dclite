from twisted.internet import gtk2reactor # for gtk-2.0
gtk2reactor.install()

from twisted.internet import reactor
from dclite.gui import GtkGui

if __name__ == "__main__":
    import sys

    import gtk;

    b = gtk.Builder();
    b.add_from_file("share/gui.ui");
    
    gui = GtkGui(b);
    gui.main_window.show_all();
    reactor.run();
