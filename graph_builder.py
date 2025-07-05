import networkx as nx
from datetime import timedelta

# Geographic constraints for northbound and southbound trips
NORTHBOUND = {"Wizards": ["76ers", "Knicks", "Nets", "Celtics"],
              "76ers": ["Knicks", "Nets", "Celtics"],
              "Knicks": ["Celtics"], "Nets": ["Celtics"]}

SOUTHBOUND = {"Celtics": ["Knicks", "Nets", "76ers", "Wizards"],
              "Knicks": ["76ers", "Wizards"], "Nets": ["76ers", "Wizards"],
              "76ers": ["Wizards"]}

class GameNode:
    """
    Represents an individual NBA game (team, date, opponent, venue)
    """
    def __init__(self, team, date, opponent, venue, city_group=None):
        self.team = team
        self.date = date
        self.opponent = opponent
        self.venue = venue
        self.city_group = city_group  # For NYC handling

    def __hash__(self):
        return hash((self.team, self.date, self.opponent, self.venue))

    def __eq__(self, other):
        return (self.team, self.date, self.opponent, self.venue) == \
               (other.team, other.date, other.opponent, other.venue)

    def __repr__(self):
        return f"GameNode({self.team}, {self.date.strftime('%Y-%m-%d')}, {self.opponent}, {self.venue})"

def build_game_graph(cleaned_df):
    """
    Build a directed graph of NBA games with valid transitions as edges.
    Args:
        cleaned_df (pd.DataFrame): Cleaned NBA schedule data
    Returns:
        nx.DiGraph: Directed graph of games
    """
    G = nx.DiGraph()
    nodes = []
    # Create nodes
    for _, row in cleaned_df.iterrows():
        node = GameNode(
            team=row['Home'],
            date=row['Game Date'],
            opponent=row['Visitor'],
            venue=row['Arena'],
            city_group=row['city_group']
        )
        G.add_node(node)
        nodes.append(node)
    # Add edges
    add_edges_to_graph(G, nodes)
    return G

def is_consecutive_night(date1, date2):
    """
    Returns True if date2 is exactly 1 day after date1
    """
    return (date2 - date1) == timedelta(days=1)

def is_valid_geographic_transition(from_node, to_node, direction):
    """
    Checks if moving from from_node to to_node respects the north/south constraint.
    Handles NYC special case (Knicks/Nets same geo_order).
    Args:
        from_node (GameNode)
        to_node (GameNode)
        direction (str): 'northbound' or 'southbound'
    Returns:
        bool
    """
    from_team = from_node.team
    to_team = to_node.team
    if direction == 'northbound':
        # Allow NYC teams to transition to each other (Knicks <-> Nets)
        if from_node.city_group == 'NYC' and to_node.city_group == 'NYC' and from_team != to_team:
            return True
        return to_team in NORTHBOUND.get(from_team, [])
    elif direction == 'southbound':
        if from_node.city_group == 'NYC' and to_node.city_group == 'NYC' and from_team != to_team:
            return True
        return to_team in SOUTHBOUND.get(from_team, [])
    return False

def add_edges_to_graph(graph, nodes):
    """
    For each pair of nodes, add an edge if:
      - Games are on consecutive nights
      - Teams are different
      - Valid geographic transition (northbound and southbound)
    Adds both northbound and southbound edges for use in trip search.
    """
    for from_node in nodes:
        for to_node in nodes:
            if from_node == to_node:
                continue
            # Must be consecutive nights
            if not is_consecutive_night(from_node.date, to_node.date):
                continue
            # Must be different teams
            if from_node.team == to_node.team:
                continue
            # Northbound edge
            if is_valid_geographic_transition(from_node, to_node, 'northbound'):
                graph.add_edge(from_node, to_node, direction='northbound')
            # Southbound edge
            if is_valid_geographic_transition(from_node, to_node, 'southbound'):
                graph.add_edge(from_node, to_node, direction='southbound')

def get_team_geographic_order():
    """
    Returns dictionary mapping teams to geographic positions.
    {"Wizards": 1, "76ers": 2, "Knicks": 3, "Nets": 3, "Celtics": 4}
    """
    return {"Wizards": 1, "76ers": 2, "Knicks": 3, "Nets": 3, "Celtics": 4}