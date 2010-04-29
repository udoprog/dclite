from adc.twisted import ADCHubProtocol, HubUser
from twisted.internet.protocol import ClientFactory

class MyADCHubProtocol(ADCHubProtocol):
    """
    TODO: emit messages to hubwindow properly
    """
    def __init__(self, hubwindow):
      hubwindow = hubwindow;
      ADCHubProtocol.__init__(self);
      
      def on_hub_identified(hub):
        hubwindow.emit("hub-identified", hub)

      def on_status(status):
        hubwindow.emit("status", status);
      
      def on_message(user, message):
        hubwindow.emit("on-message", user, message);

      def on_user_info(user):
        hubwindow.emit("user-info", user);
      
      def on_user_quit(user):
        hubwindow.emit("user-quit", user);
      
      def on_connection_made():
        hubwindow.emit("connection-made");
      
      def on_connection_lost(reason):
        hubwindow.emit("connection-lost", reason);
      
      self.connect("hub-identified", on_hub_identified);
      self.connect("status", on_status);
      self.connect("message", on_message);
      self.connect("user-info", on_user_info);
      self.connect("user-quit", on_user_quit);
      self.connect("connection-made", on_connection_made);
      self.connect("connection-lost", on_connection_lost);
      
      # private signals
      self.connect("get-user", self.getUser);
      self.connect("direct-connect", self.onDirectConnect);
      
      hubwindow.connect("input-message-submit", self.on_inputSendMessage);
    
    def on_inputSendMessage(self, source, message):
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

