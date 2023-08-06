from Network import Node, Edge, Packet
import random
import networkx as nx


class NetworkStats:
  def __init__(self):
    self.total_path_length = 0.
    self.total_time = 0.
    self.dropped_packets = 0
    self.timed_out_packets = 0

  def print_load_results(self, n):
    # Print packet stats for debugging.
    print(" avg path length: ", self.total_path_length / n)
    print(" avg transmission time: ", self.total_time / n)
    print(" timed out packets: ", (float(self.timed_out_packets)))
    print(" total dropped packets : ", (self.dropped_packets))

class NetworkSimulator:

  def __init__(self, num_nodes):
    # each node is connected to 7 other nodes
    self.G = nx.connected_watts_strogatz_graph(num_nodes, 7, 0.9)
    self.nodes = list(self.G.nodes)
    # Generate and associate attributes to node and edges in G.
    self.node_attrs = {node: Node() for node in self.G.nodes}
    self.edge_attrs = {edge: Edge() for edge in self.G.edges}
    # Node queues, requires reset after simulation
    self.node_queues = {}

  def network_viz(self):
    nx.draw(self.G, with_labels=True)

  def edge_attribute(self, n1, n2):
    if (n1, n2) in self.edge_attrs: 
      return self.edge_attrs[(n1, n2)]
    if (n2, n1) in self.edge_attrs: 
      return self.edge_attrs[(n2, n1)]
    return None
 

  def traverseEdge(self, packet, src, dst):
    # add dest node to path of packet
    packet.addToPath(dst)
    # get attributes of destination
    dest = self.node_attrs[dst]
    # get edge attributes from src to dest
    edge = self.edge_attribute(src, dst)
    # get time to travel from source to dest
    travelTime = edge.getTravelTime()

    # propogation time & queue waiting time
    packet.totalTime += travelTime + dest.packet_queue_time * len(self.node_queues.get(dst, []))
    # decide if packet dropped or not
    packet.dropped = edge.isDropped()
    return travelTime

  def generate_packet(self):
    n1 = random.choice(self.nodes)
    n2 = random.choice(self.nodes)
    # until source and destination not same
    while n1 == n2:
      n2 = random.choice(self.nodes)
    return Packet(n1, n2)

  def generate_packets(self, n):
    return [self.generate_packet() for i in range(n)]
 
  # Iterate through node queues and propagate packets through the network.
  def propagate_packets(self, packet_router, network_stats):
    # list of nodes which have packets
    nodes = list(self.node_queues.keys())

    for node in nodes:
      # Pop a node from the queue to process its packets.
      queue = self.node_queues[node]
      # get the packet on that nodes queue start
      packet_to_route = queue.pop()
      # if no more packets in the node queue, delete node 
      if not self.node_queues[node]: 
        del self.node_queues[node]

      # route packet by one step
      next_node = packet_router.routePacketSingleStep(packet_to_route, node)

      # Stop propogating packets if they are timed out.
      # max time 1500ms
      if packet_to_route.totalTime >10000:
        network_stats.total_time += packet_to_route.totalTime
        network_stats.timed_out_packets += 1
        continue

      # Reroute packet to beginning if packet was dropped.
      if next_node is None:
        network_stats.dropped_packets += 1
        next_node = packet_to_route.src
        packet_to_route.reset(packet_to_route.totalTime)
 
      # Handle the next node.
      if next_node == packet_to_route.dst:
        # Packet routed successfully to dst.
        network_stats.total_path_length += len(packet_to_route.path)
        network_stats.total_time += packet_to_route.totalTime
      else:
        # Add next node to appropriate queue.
        if next_node not in self.node_queues: 
          self.node_queues[next_node] = []
        self.node_queues[next_node].append(packet_to_route)
    return network_stats
 
  # Sends out a new batch of packets.
  def send_packets(self, packets, packet_index, packets_per_batch):
    for index in range(packet_index, min(packet_index + packets_per_batch, len(packets))):
      packet = packets[index]
      if packet.src not in self.node_queues: 
        self.node_queues[packet.src] = []
      self.node_queues[packet.src].append(packet)
    return packet_index + packets_per_batch

  def train_Q(self, packets, packet_router,packets_per_batch):
    network_stats = NetworkStats()
    packet_index = 0
    # Process batches of packets at a time.
    while self.node_queues or packet_index < len(packets):
      if not self.node_queues:
        packet_index = self.send_packets(packets, packet_index, packets_per_batch)
      network_stats = self.propagate_packets(packet_router, network_stats)

    network_stats.print_load_results(len(packets))