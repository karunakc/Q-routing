import random

class Node:
  def __init__(self):
    # approx- 0.02ms per packet
    self.packet_queue_time = random.gauss(0.02, 0.02)


class Edge:
  def __init__(self):
    # Generate a random latency and drop rate within a range,
    # drawn from a uniform distribution.
    # min latency- 0ms
    # max latency- 300ms
    # random latency between 0 to 300ms
    self.latency = random.randint(0, 300)
    # minimum packet drop rate= 0%
    # maximum packet drop rate= 5%
    # a random drop rate between 0 to 10 
    self.dropRate = float(random.randint(0, 5)) / 100

    # number of dropped packets
    self.dropped_packets = 0
    
  def getTravelTime(self):
    # travel time for a particular packet
    # average latency
    # standard deviation of latency ~10
    return float(random.gauss(self.latency, 5))

  def isDropped(self):
    # randomly generate a number, 
    # compare with the drop rate to decide if packet has been dropped or not
    isDropped = random.randint(0, 20)/100 < self.dropRate 
    if isDropped: 
      self.dropped_packets += 1
    return isDropped


class Packet:
  def __init__(self, src, dst):
    # Initialize path to include the source / starting node.
    self.src = src
    self.dst = dst
    # Path of nodes that this packet has traversed.
    self.path = [src]
    # initially- packet not dropped
    self.dropped = False
    # totoal distance traversed by packet initially 0
    self.totalTime = 0.

  def addToPath(self, node):
    # add a node to the packet path
    self.path.append(node)

  def reset(self, totalTime ):
    # reset packet since it needs to be retransmitted from the source
    self.path = [self.src]
    self.dropped = False
    # even though restarting, total time needs to be old one
    self.totalTime = totalTime