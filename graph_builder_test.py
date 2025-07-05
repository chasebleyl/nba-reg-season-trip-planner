#!/usr/bin/env python3
"""
Test script for graph_builder.py functionality using pytest
"""

import pytest
import pandas as pd
from graph_builder import build_game_graph, GameNode, is_consecutive_night, is_valid_geographic_transition, get_team_geographic_order

@pytest.fixture
def sample_df():
    """Create a sample DataFrame for testing"""
    data = [
        # Wizards home, then 76ers, then Knicks, then Nets, then Celtics
        {"Game Date": pd.Timestamp("2024-10-24"), "Home": "Wizards", "Visitor": "Celtics", "Arena": "Capital One Arena", "city_group": "Wizards"},
        {"Game Date": pd.Timestamp("2024-10-25"), "Home": "76ers", "Visitor": "Wizards", "Arena": "Wells Fargo Center", "city_group": "76ers"},
        {"Game Date": pd.Timestamp("2024-10-26"), "Home": "Knicks", "Visitor": "76ers", "Arena": "Madison Square Garden (IV)", "city_group": "NYC"},
        {"Game Date": pd.Timestamp("2024-10-27"), "Home": "Nets", "Visitor": "Knicks", "Arena": "Barclays Center", "city_group": "NYC"},
        {"Game Date": pd.Timestamp("2024-10-28"), "Home": "Celtics", "Visitor": "Nets", "Arena": "TD Garden", "city_group": "Celtics"},
        # Add a same-night NYC pair for special case
        {"Game Date": pd.Timestamp("2024-10-27"), "Home": "Knicks", "Visitor": "Celtics", "Arena": "Madison Square Garden (IV)", "city_group": "NYC"},
    ]
    return pd.DataFrame(data)

def test_game_node_creation():
    """Test GameNode creation and properties"""
    node = GameNode("Wizards", pd.Timestamp("2024-10-24"), "Celtics", "Capital One Arena", "Wizards")
    
    assert node.team == "Wizards"
    assert node.date == pd.Timestamp("2024-10-24")
    assert node.opponent == "Celtics"
    assert node.venue == "Capital One Arena"
    assert node.city_group == "Wizards"

def test_game_node_hash_and_eq():
    """Test GameNode hash and equality"""
    node1 = GameNode("Wizards", pd.Timestamp("2024-10-24"), "Celtics", "Capital One Arena")
    node2 = GameNode("Wizards", pd.Timestamp("2024-10-24"), "Celtics", "Capital One Arena")
    node3 = GameNode("76ers", pd.Timestamp("2024-10-24"), "Celtics", "Capital One Arena")
    
    assert node1 == node2
    assert node1 != node3
    assert hash(node1) == hash(node2)

def test_is_consecutive_night():
    """Test consecutive night logic"""
    date1 = pd.Timestamp("2024-10-24")
    date2 = pd.Timestamp("2024-10-25")
    date3 = pd.Timestamp("2024-10-26")
    
    assert is_consecutive_night(date1, date2) == True
    assert is_consecutive_night(date2, date3) == True
    assert is_consecutive_night(date1, date3) == False  # Not consecutive

def test_get_team_geographic_order():
    """Test geographic order mapping"""
    geo_order = get_team_geographic_order()
    
    expected = {"Wizards": 1, "76ers": 2, "Knicks": 3, "Nets": 3, "Celtics": 4}
    assert geo_order == expected

def test_build_game_graph(sample_df):
    """Test graph building"""
    graph = build_game_graph(sample_df)
    
    # Check nodes
    assert graph.number_of_nodes() == 6, f"Expected 6 nodes, got {graph.number_of_nodes()}"
    
    # Check edges exist
    assert graph.number_of_edges() > 0, "Graph should have edges"
    
    # Check Wizards nodes exist
    wizards_nodes = [node for node in graph.nodes() if node.team == "Wizards"]
    assert len(wizards_nodes) > 0, "No Wizards nodes in graph"

def test_geographic_transitions():
    """Test geographic transition validation"""
    # Create test nodes
    wizards_node = GameNode("Wizards", pd.Timestamp("2024-10-24"), "Celtics", "Capital One Arena", "Wizards")
    sixers_node = GameNode("76ers", pd.Timestamp("2024-10-25"), "Wizards", "Wells Fargo Center", "76ers")
    knicks_node = GameNode("Knicks", pd.Timestamp("2024-10-26"), "76ers", "MSG", "NYC")
    nets_node = GameNode("Nets", pd.Timestamp("2024-10-27"), "Knicks", "Barclays", "NYC")
    celtics_node = GameNode("Celtics", pd.Timestamp("2024-10-28"), "Nets", "TD Garden", "Celtics")
    
    # Test northbound transitions
    assert is_valid_geographic_transition(wizards_node, sixers_node, 'northbound') == True
    assert is_valid_geographic_transition(sixers_node, knicks_node, 'northbound') == True
    assert is_valid_geographic_transition(knicks_node, celtics_node, 'northbound') == True
    
    # Test southbound transitions
    assert is_valid_geographic_transition(celtics_node, nets_node, 'southbound') == True
    assert is_valid_geographic_transition(nets_node, sixers_node, 'southbound') == True
    assert is_valid_geographic_transition(sixers_node, wizards_node, 'southbound') == True
    
    # Test invalid transitions (reverse direction)
    assert is_valid_geographic_transition(celtics_node, wizards_node, 'northbound') == False  # Wrong direction
    assert is_valid_geographic_transition(wizards_node, celtics_node, 'southbound') == False  # Wrong direction

def test_nyc_special_case():
    """Test NYC teams can transition between each other"""
    knicks_node = GameNode("Knicks", pd.Timestamp("2024-10-26"), "76ers", "MSG", "NYC")
    nets_node = GameNode("Nets", pd.Timestamp("2024-10-27"), "Knicks", "Barclays", "NYC")
    
    # NYC teams should be able to transition to each other in both directions
    assert is_valid_geographic_transition(knicks_node, nets_node, 'northbound') == True
    assert is_valid_geographic_transition(knicks_node, nets_node, 'southbound') == True
    assert is_valid_geographic_transition(nets_node, knicks_node, 'northbound') == True
    assert is_valid_geographic_transition(nets_node, knicks_node, 'southbound') == True 