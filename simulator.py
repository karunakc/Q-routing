from network import NodeAttr, EdgeAttr, Packet
import random
import networkx as nx


class NetworkStats:
  #called
  def __init__(self):
    self.total_path_length = 0.
    self.total_time = 0.
    self.dropped_packets = 0.
 
class NetworkSimulator:

  #called
  def __init__(self, num_nodes, drop_node_fraction=0.2, drop_node_connectivity=0.5):
    num_drop_nodes = int(num_nodes * drop_node_fraction)
    num_constant_nodes = num_nodes - num_drop_nodes
    self.G = nx.connected_watts_strogatz_graph(num_constant_nodes, 3, 0.9)
    self.constant_nodes = list(self.G.nodes)
    
    self.node_attrs = {node: NodeAttr() for node in self.G.nodes}
    self.edge_attrs = {edge: EdgeAttr() for edge in self.G.edges}
    
    self.node_queues = {}

  def generate_packet(self):
    n1 = random.choice(self.constant_nodes)
    n2 = random.choice(self.constant_nodes)
    while n1 == n2:
      n2 = random.choice(self.constant_nodes)
    return Packet(n1, n2)
 
 
  #called
  def generate_packets(self, n):
    return [self.generate_packet() for i in range(n)]
 
  def print_load_results(self, n, network_stats):
    
    avg_length = network_stats.total_path_length / n
    avg_time = network_stats.total_time / n
    print(" avg path length:       %f" % avg_length)
    print(" avg transmission time: %f" % avg_time)
    
    print(" total dropped packets :   %d" % (network_stats.dropped_packets))
 

  def propagate_packets(self, packet_router, network_stats):
    
    nodes = list(self.node_queues.keys())
    for node in nodes:
      queue = self.node_queues[node]
      packet_to_route = queue.pop()
      if not self.node_queues[node]: 
        del self.node_queues[node]

      next_node = packet_router.routePacketSingleStep(packet_to_route, node)
      
      if next_node is None:
        network_stats.dropped_packets += 1
        next_node = packet_to_route.src
        
        packet_to_route.reset(totalTime = packet_to_route.totalTime)
        
      if next_node == packet_to_route.dst:
        
        network_stats.total_path_length += len(packet_to_route.path)
        network_stats.total_time += packet_to_route.totalTime
      else:
        
        if next_node not in self.node_queues: 
          self.node_queues[next_node] = []
        self.node_queues[next_node].append(packet_to_route)

    return network_stats
  
  def send_packets(self, packets, packet_index, packets_per_batch):
    for index in range(packet_index, min(packet_index + packets_per_batch, len(packets))):
      packet = packets[index]
      if packet.src not in self.node_queues: 
        self.node_queues[packet.src] = []
      self.node_queues[packet.src].append(packet)
 
    return packet_index + packets_per_batch
  
  #called
  def train_Q(self, packets, packet_router, packets_per_batch=100):
    network_stats = NetworkStats()
    packet_index = 0
    while self.node_queues or packet_index < len(packets):
      if not self.node_queues:
        packet_index = self.send_packets(packets, packet_index, packets_per_batch)
 
      network_stats = self.propagate_packets(packet_router, network_stats)
    self.print_load_results(len(packets), network_stats)