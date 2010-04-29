from adc.twisted import ADCHubProtocol, HubUser
from twisted.internet.protocol import ClientFactory

class MyADCHubProtocol(ADCHubProtocol):
    """
    TODO: emit messages to hubwindow properly
    """
    
    def __init__(self, hubwindow):
      hubwindow = hubwindow;
      ADCHubProtocol.__init__(self);
      
      hubsignals = [
        ("hub-identified",  "hub-identified"),
        ("status",          "status"),
        ("message",         "message"),
        ("user-info",       "user-info"),
        ("user-quit",       "user-quit"),
        ("connection-made", "connectino-made"),
        ("connection-lost", "connectino-lost"),
      ];
      
      for fr, to in hubsignals:
        self.connect(fr, lambda *args: hubwindow.emit(to, *args));
      
      # private signals
      self.connect("direct-connect", self.onDirectConnect);
      hubwindow.connect("input-message-submit", self.onInputMessageSubmit);
    
    def onInputMessageSubmit(self, source, message):
      self.sendMessage(message);
    
    def getUser(self):
      return HubUser(NI="udoprog-test", SS=(1024 ** 5) * 10);
    
    def onDirectConnect(self, user):
      print "connect to", user.nick, user.ip4

class HubFactory(ClientFactory):
    protocol = MyADCHubProtocol
    
    def __init__(self, hubwindow, **kw):
        self.hubwindow = hubwindow;
        self.kw = kw;
    
    def buildProtocol(self, conn):
        self.protocol = MyADCHubProtocol(self.hubwindow, **self.kw);
        return self.protocol;

