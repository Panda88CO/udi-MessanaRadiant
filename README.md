# udi-MessanaRadiant
The node server is made to control MEssana Radiat heating and cooling system (www.radiantcooling.com).  My system only includes heating so I have not tested the cooling functions yet

Setup requires a key/token provided by messana.  IN addition you will need your system to be on your local network (you ened to provide the IP address)

The system sends a heartbeat every short poll interval (toggling between 1 and 0).  It also updates the most critical parameters then.  The longpoll updates all parameters
