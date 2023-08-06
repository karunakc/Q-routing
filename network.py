import random as rnd

MIN_DROP_RATE = 0
MAX_DROP_RATE = 0.05
DROP_MULT = 1 / MAX_DROP_RATE
MIN_LATENCY = 0
MAX_LATENCY = 300
LATENCY_STD = 5
LOAD_MULTIPLIER = 0.01
LOAD_DECAY = 0.001
PACKET_QUEUE_TIME = 0.02


class NodeAttr:
  def __init__(self):
    self.packet_queue_time = rnd.gauss(PACKET_QUEUE_TIME, PACKET_QUEUE_TIME)


class EdgeAttr:
  def __init__(self):
    self.latency = rnd.randint(MIN_LATENCY, MAX_LATENCY)
    self.dropRate = float(rnd.randint(MIN_DROP_RATE * DROP_MULT, MAX_DROP_RATE  * DROP_MULT)) / DROP_MULT
    self.dropped_packets = 0

  def getTravelTime(self):
    return float(rnd.gauss(self.latency, LATENCY_STD))

  def isDropped(self):
    isDropped = rnd.randint(0, DROP_MULT) < self.dropRate * DROP_MULT
    
    if isDropped: 
      self.dropped_packets += 1
    return isDropped

  def reset(self):
    self.load = 0
    self.dropped_packets = 0


class Packet:
  def __init__(self, src, dst):
    self.src = src
    self.dst = dst
    self.path = [src]
    self.dropped = False
    self.totalTime = 0.

  def getMostRecentNode(self):
    return self.path[-1]

  def addToPath(self, node):
    self.path.append(node)

  def getSrc(self):
    return self.src

  def reset(self, totalTime=0., dropped=False):
    self.path = [self.src]
    self.dropped = dropped
    self.totalTime = totalTime

  def __str__(self):
    return " -> ".join(map(str, self.path))