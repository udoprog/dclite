from adc.twisted import ADCHubProtocol, HubUser
from twisted.internet.protocol import ClientFactory

class MyADCHubProtocol(ADCHubProtocol):
    def __init__(self, guiwindow):
      self.gui = guiwindow;
      self.gui.setProtocol(self);
      ADCHubProtocol.__init__(self);
    
    def connectionMade(self):
      ADCHubProtocol.connectionMade(self);
      self.gui.printStatus("connection made");
    
    def connectionLost(self, reason):
      ADCHubProtocol.connectionLost(self, reason);
      self.gui.printStatus("connection lost: " + str(reason.value));
    
    def onHubIdentified(self):
      if self.hub.name:
        self.gui.set_label(self.hub.name);
      else:
        self.gui.set_label(self.hub.version + " " + self.hub.peer.host + ":" + str(self.hub.peer.port));
    
    def onStatus(self, status):
      self.gui.printStatus(str(status));
    
    def onMessage(self, user, message):
      self.gui.printStatus("<" + user.nick + "> " + message);
    
    def getUser(self):
      return HubUser(nick="udoprog-test", sharesize=1024**3);

class HubFactory(ClientFactory):
    protocol = MyADCHubProtocol
    
    def __init__(self, gui, **kw):
        self.gui = gui;
        self.kw = kw;
    
    def buildProtocol(self, conn):
        self.protocol = MyADCHubProtocol(self.gui, **self.kw);
        return self.protocol;

