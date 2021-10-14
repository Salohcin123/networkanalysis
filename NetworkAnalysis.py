"""
Author: Nicholas Merante
Class: Explorations of Place and Space - Networks
Date: October 2021
"""

import random
import statistics

import networkx as nx
from networkx import Graph, degree_centrality, closeness_centrality, betweenness_centrality, eigenvector_centrality, \
    clustering

NODE_COUNT = 10  # The number of nodes in the network.
EDGE_PROBABILITY = 0.5  # The probability that an edge will exist when the network is created.
INFECTION_RATE = 0.1  # The probability that the infection will spread along each edge each day.

NETWORK_COUNT = 100000  # The number of networks to test.
DAYS_TO_RUN = 3  # The number of days for which the infection should spread.

# Each of the measures of centrality to test.
CENTRALITIES = ["random", "degree", "closeness", "clustering", "betweenness", "eigenvector"]


# Use this to only test one measure of centrality.
# CENTRALITIES = ["degree"]


def main() -> None:
    results = []
    for i in CENTRALITIES:
        print(i + ":")
        data = number_infected(NETWORK_COUNT, DAYS_TO_RUN, i)
        results.append(i + ": avg=" + str(statistics.mean(data)) + ", med=" + str(statistics.median(data)) +
                       ", mode=" + str(statistics.mode(data)) + ", stdev=" + str(statistics.stdev(data)))

    print("\nNetworks = " + str(NETWORK_COUNT) +
          ", Days = " + str(DAYS_TO_RUN) + ", Nodes = " + str(NODE_COUNT) +
          ", EP = " + str(EDGE_PROBABILITY) + ", IP = " + str(INFECTION_RATE))
    for i in results:
        print(i)

    # analysis = NetworkAnalysis(NODE_COUNT)
    # analysis.generate_new_network(NODE_COUNT, "degree")
    # analysis.print_edges(True)
    # analysis.print_immune()
    # print(analysis.spread_infection_for_n_days(4))


def number_infected(networks: int, days: int, centrality: str) -> list:
    """
    This method runs the simulation for the inputted number of days, analysing the certain centrality that
    is inputted. It creates a network, spreads the infection, and stores the number infected for the number of networks
    that the user enters. It prints its progress every 10,000 networks that are generated and analyzed.
    :param networks: The number of networks to analyze.
    :param days: The number of days the infection should spread.
    :param centrality: The type of centrality that should be measured in order to immunize the node of highest importance.
    :return: A list of integers that represents the number of infected individuals after n days for each network.
    """
    total = []
    analysis = NetworkAnalysis(NODE_COUNT, centrality)
    for i in range(networks):
        if i % 10000 == 0:
            print("Progress: " + str(i))
        analysis.generate_new_network(NODE_COUNT, centrality)
        total.append(analysis.spread_infection_for_n_days(days))
    return total


class NetworkAnalysis:
    network: Graph  # The network itself that holds edge information.
    infectionMatrix: list  # Keeps track of which nodes are infected.
    immune: int  # The value of this is the index of the node that is immune.

    def __init__(self, nodeCount, centrality):
        self.generate_new_network(nodeCount, centrality)

    def generate_new_network(self, nodeCount: int, immuneType: str):
        """
        Creates a new binomial network with nodeCount number of nodes and with immuneType being the measure of importance
        to determine immunity. Edges are created, a node is immunized, and a node is infected.
        :param nodeCount: The number of nodes in the network.
        :param immuneType: The measure of importance to determine which node to immunize.
        """
        network = nx.Graph()

        # Initializes the infectionMatrix list so every node is not infected with a value of False.
        self.infectionMatrix = []
        for i in range(0, nodeCount):
            self.infectionMatrix.append(False)

        self.immune = -1

        # Adds the correct number of nodes to the graph.
        for i in range(nodeCount):
            network.add_node(i)

        # Randomly adds edges between nodes based on the probability of an edge being created.
        for i in range(len(network.nodes)):
            for j in range(i + 1, len(network.nodes)):
                if (random.random() < EDGE_PROBABILITY):
                    network.add_edge(i, j)
        self.network = network

        self.immunize_node(immuneType)

        # Makes one random node have a True infected state.
        self.infect_random_node()

    def immunize_node(self, immuneType: str):
        """
        Immunizes a node based on the inputted degree. If several nodes are tied for importance,
        a random node from the list of leaders is selected.
        :param immuneType: The measure of importance to measure to immunize a node.
        """
        if immuneType == "degree":
            dictionary = degree_centrality(self.network)
        elif immuneType == "closeness":
            dictionary = closeness_centrality(self.network)
        elif immuneType == "clustering":
            dictionary = clustering(self.network)
        elif immuneType == "betweenness":
            dictionary = betweenness_centrality(self.network)
        elif immuneType == "eigenvector":
            dictionary = eigenvector_centrality(self.network)
        else:
            immune = random.randrange(len(self.infectionMatrix))
            return

        nodes = []
        max = -1
        for i in dictionary:
            if dictionary[i] > max:
                max = dictionary[i]
                nodes.clear()
            if dictionary[i] >= max:
                nodes.append(i)
        self.immune = nodes[random.randrange(len(nodes))]

    def infect_random_node(self):
        """
        Infects a random node in the matrix, ensuring it does not infect an immune node.
        """
        current_node = random.randrange(len(self.infectionMatrix))
        while current_node == self.immune:
            current_node = random.randrange(len(self.infectionMatrix))
        self.infectionMatrix[current_node] = True

    def spread_infection_for_n_days(self, days: int) -> int:
        """
        Spreads the infection for a certain number of days.
        :param days: The number of days the infection spreads.
        :return: The number of infected nodes after the infection is done spreading.
        """
        for i in range(days):
            self.spread_infection()
        total_infected = 0
        for i in range(len(self.infectionMatrix)):
            if self.infectionMatrix[i]:
                total_infected += 1
        return total_infected

    def spread_infection(self):
        """
        Causes the infection to spread along each edge with a probability of INFECTION_RATE.
        """
        updated_list = self.infectionMatrix.copy()
        for i in range(len(self.infectionMatrix)):
            if self.infectionMatrix[i]:
                for j in list(self.network.neighbors(i)):
                    if random.random() < INFECTION_RATE and j != self.immune:
                        updated_list[j] = True
        self.infectionMatrix = updated_list

    def print_network(self):
        """
        Prints each node in the network.
        """
        for i in list(self.network.nodes):
            print(i, end=", ")
        print()

    def print_edges(self, printEdgeInfo: bool):
        """
        Pritns every pair of nodes which have an edge.
        :param printEdgeInfo: If true, every edge combination will be printed.
        :return:
        """
        print("Number of Edges: " + str(len(self.network.edges)), end=" ")
        if (not printEdgeInfo):
            print()
            return
        for i in list(self.network.edges):
            print(i, end=", ")
        print()

    def print_infected(self):
        """
        Prints the list of indices of the nodes who are infected.
        """
        print(self.infectionMatrix)

    def print_immune(self):
        """
        Prints the index of the immune node.
        """
        print(self.immune)


if __name__ == '__main__':
    main()
