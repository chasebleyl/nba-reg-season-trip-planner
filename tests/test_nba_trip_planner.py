#!/usr/bin/env python3
"""
Comprehensive test script for NBA trip planner end-to-end functionality using pytest
"""

import pytest
import pandas as pd
import os
from datetime import datetime
from utils.data_processor import load_and_clean_csv
from utils.graph_builder import build_game_graph
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from nba_trip_planner import find_all_valid_trips, rank_trips, format_output, calculate_travel_efficiency

@pytest.fixture
def processed_data():
    """Load and process the NBA data once for all tests"""
    return load_and_clean_csv('data/csv/2024_nba_data.csv')

@pytest.fixture
def game_graph(processed_data):
    """Build the game graph once for all tests"""
    return build_game_graph(processed_data)

def test_data_loading_and_processing(processed_data):
    """Test data loading and processing"""
    # Verify basic structure
    assert len(processed_data) > 0, "DataFrame should not be empty"
    assert 'Home' in processed_data.columns, "Home column should exist"
    assert 'Game Date' in processed_data.columns, "Game Date column should exist"
    
    # Verify target teams
    target_teams = {"Wizards", "76ers", "Knicks", "Nets", "Celtics"}
    actual_teams = set(processed_data['Home'].unique())
    assert actual_teams == target_teams, f"Expected {target_teams}, got {actual_teams}"
    
    # Verify Wizards games exist
    wizards_games = processed_data[processed_data['Home'] == 'Wizards']
    assert len(wizards_games) > 0, "No Wizards games found"

def test_graph_building(game_graph):
    """Test graph building"""
    # Verify graph has nodes
    assert game_graph.number_of_nodes() > 0, "Graph has no nodes"
    assert game_graph.number_of_edges() > 0, "Graph has no edges"
    
    # Verify Wizards nodes exist
    wizards_nodes = [node for node in game_graph.nodes() if node.team == "Wizards"]
    assert len(wizards_nodes) > 0, "No Wizards nodes in graph"

def test_trip_finding(game_graph):
    """Test trip finding"""
    trips = find_all_valid_trips(game_graph)
    
    # Verify trips exist
    assert len(trips) > 0, "No trips found"
    
    # Verify all trips include Wizards
    for trip in trips:
        teams_in_trip = {node.team for node in trip}
        assert "Wizards" in teams_in_trip, f"Trip missing Wizards: {teams_in_trip}"
    
    # Verify trip lengths are 3-5
    for trip in trips:
        assert 3 <= len(trip) <= 5, f"Invalid trip length {len(trip)}: {[node.team for node in trip]}"
    
    # Verify no team repetition within trips
    for trip in trips:
        teams_in_trip = [node.team for node in trip]
        unique_teams = set(teams_in_trip)
        assert len(teams_in_trip) == len(unique_teams), f"Team repetition in trip: {teams_in_trip}"

def test_trip_ranking(game_graph):
    """Test trip ranking"""
    trips = find_all_valid_trips(game_graph)
    ranked_trips = rank_trips(trips)
    
    # Verify ranking structure
    assert isinstance(ranked_trips, dict), "Ranked trips should be a dictionary"
    
    # Verify trips are grouped by length
    for length, trips_list in ranked_trips.items():
        assert 3 <= length <= 5, f"Invalid trip length in ranking: {length}"
        for trip in trips_list:
            assert len(trip) == length, f"Trip length mismatch in ranking"
    
    # Verify travel efficiency calculation
    for length, trips_list in ranked_trips.items():
        if len(trips_list) > 1:
            efficiencies = [calculate_travel_efficiency(trip) for trip in trips_list]
            # Check if sorted by efficiency (ascending)
            assert efficiencies == sorted(efficiencies), f"Trips not sorted by efficiency: {efficiencies}"

def test_output_formatting(game_graph):
    """Test output formatting"""
    trips = find_all_valid_trips(game_graph)
    ranked_trips = rank_trips(trips)
    output = format_output(ranked_trips)
    
    # Verify output file was created (with timestamp pattern)
    results_files = [f for f in os.listdir("results") if f.startswith("nba_trips_") and f.endswith(".txt")]
    assert len(results_files) > 0, "Output file not created"
    
    # Verify output content
    assert "NBA TRIP PLANNER RESULTS" in output, "Missing header in output"
    assert "Total valid trips found:" in output, "Missing trip count in output"
    
    # Verify all trip length headers are present (even with 0 trips)
    assert "=== 5-NIGHT TRIPS (" in output, "Missing 5-night trips header"
    assert "=== 4-NIGHT TRIPS (" in output, "Missing 4-night trips header"
    assert "=== 3-NIGHT TRIPS (" in output, "Missing 3-night trips header"

def test_geographic_constraints(game_graph):
    """Test geographic constraints"""
    trips = find_all_valid_trips(game_graph)
    ranked_trips = rank_trips(trips)
    
    # Check a few trips for geographic validity
    sample_trips = []
    for length, trips_list in ranked_trips.items():
        if trips_list:
            sample_trips.extend(trips_list[:2])  # Take first 2 from each length
    
    geo_order = {"Wizards": 1, "76ers": 2, "Knicks": 3, "Nets": 3, "Celtics": 4}
    
    for trip in sample_trips[:5]:  # Check first 5 trips
        teams = [node.team for node in trip]
        orders = [geo_order[team] for team in teams]
        
        # Check for geographic direction consistency
        # Either strictly increasing (northbound) or strictly decreasing (southbound)
        # or staying same (NYC teams)
        is_northbound = all(orders[i] <= orders[i+1] for i in range(len(orders)-1))
        is_southbound = all(orders[i] >= orders[i+1] for i in range(len(orders)-1))
        
        assert is_northbound or is_southbound, f"Invalid geographic flow: {teams} -> {orders}"

def test_consecutive_nights(game_graph):
    """Test consecutive nights constraint"""
    trips = find_all_valid_trips(game_graph)
    ranked_trips = rank_trips(trips)
    
    # Check a few trips for consecutive nights
    sample_trips = []
    for length, trips_list in ranked_trips.items():
        if trips_list:
            sample_trips.extend(trips_list[:2])  # Take first 2 from each length
    
    for trip in sample_trips[:5]:  # Check first 5 trips
        for i in range(len(trip) - 1):
            date1 = trip[i].date
            date2 = trip[i + 1].date
            days_diff = (date2 - date1).days
            assert days_diff == 1, f"Non-consecutive nights: {date1} -> {date2} ({days_diff} days)"

def test_zero_five_night_trips():
    """Test that output correctly handles zero 5-night trips"""
    # Create a mock ranked_trips with no 5-night trips
    mock_ranked_trips = {
        4: [],  # No 4-night trips either
        3: []   # No 3-night trips either
    }
    
    # Test the format_output function
    output = format_output(mock_ranked_trips)
    
    # Verify all headers are present
    assert "=== 5-NIGHT TRIPS (0 found) ===" in output, "5-night header missing or incorrect count"
    assert "=== 4-NIGHT TRIPS (0 found) ===" in output, "4-night header missing or incorrect count"
    assert "=== 3-NIGHT TRIPS (0 found) ===" in output, "3-night header missing or incorrect count"
    
    # Verify "No valid trips found" messages are present
    assert "No valid trips found for this length." in output, "Missing 'no trips found' message"
    
    # Verify total count is 0
    assert "Total valid trips found: 0" in output, "Total count should be 0"

def test_travel_efficiency_calculation():
    """Test travel efficiency calculation"""
    # Create mock trips to test efficiency calculation
    from utils.graph_builder import GameNode
    
    # Test trip with 2 jumps: Wizards -> 76ers -> Celtics
    trip1 = [
        GameNode("Wizards", pd.Timestamp("2024-10-24"), "Celtics", "Capital One Arena"),
        GameNode("76ers", pd.Timestamp("2024-10-25"), "Wizards", "Wells Fargo Center"),
        GameNode("Celtics", pd.Timestamp("2024-10-26"), "76ers", "TD Garden"),
    ]
    
    # Test trip with 1 jump: Knicks -> Nets -> Wizards
    trip2 = [
        GameNode("Knicks", pd.Timestamp("2024-10-24"), "Celtics", "MSG"),
        GameNode("Nets", pd.Timestamp("2024-10-25"), "Knicks", "Barclays"),
        GameNode("Wizards", pd.Timestamp("2024-10-26"), "Nets", "Capital One Arena"),
    ]
    
    efficiency1 = calculate_travel_efficiency(trip1)
    efficiency2 = calculate_travel_efficiency(trip2)
    
    assert efficiency1 == 2, f"Expected 2 jumps, got {efficiency1}"
    assert efficiency2 == 1, f"Expected 1 jump, got {efficiency2}"

def test_2025_format_integration():
    """Test complete pipeline with 2025 format CSV data"""
    # Load and process 2025 data
    processed_data_2025 = load_and_clean_csv('data/csv/2025_nba_data.csv')
    
    # Verify basic structure for 2025 data
    assert len(processed_data_2025) > 0, "2025 DataFrame should not be empty"
    assert 'Home' in processed_data_2025.columns, "Home column should exist in 2025 data"
    assert 'Game Date' in processed_data_2025.columns, "Game Date column should exist in 2025 data"
    
    # Verify target teams
    target_teams = {"Wizards", "76ers", "Knicks", "Nets", "Celtics"}
    actual_teams = set(processed_data_2025['Home'].unique())
    assert actual_teams == target_teams, f"Expected {target_teams}, got {actual_teams}"
    
    # Verify dates are in 2025+ range
    min_year = processed_data_2025['Game Date'].dt.year.min()
    assert min_year >= 2025, f"2025 data should have years >= 2025, got {min_year}"
    
    # Build graph with 2025 data
    game_graph_2025 = build_game_graph(processed_data_2025)
    assert game_graph_2025.number_of_nodes() > 0, "2025 graph has no nodes"
    assert game_graph_2025.number_of_edges() > 0, "2025 graph has no edges"
    
    # Find trips with 2025 data
    all_trips_2025 = find_all_valid_trips(game_graph_2025)
    assert len(all_trips_2025) > 0, "Should find valid trips in 2025 data"
    
    # Verify all trips include Wizards
    for trip in all_trips_2025:
        wizards_in_trip = any(node.team == "Wizards" for node in trip)
        assert wizards_in_trip, "All trips should include Wizards"
    
    # Rank trips
    ranked_trips_2025 = rank_trips(all_trips_2025)
    
    # Verify ranking structure
    for length in [3, 4]:  # Only check lengths that should have trips
        assert length in ranked_trips_2025, f"Length {length} should be in ranking"
        assert isinstance(ranked_trips_2025[length], list), f"Length {length} should map to list"
    
    # Check that we have at least some trips
    total_trips = sum(len(trips) for trips in ranked_trips_2025.values())
    assert total_trips > 0, "Should have some trips in ranking"
    
    # Test output formatting
    output_2025 = format_output(ranked_trips_2025)
    assert "NBA TRIP PLANNER RESULTS" in output_2025, "Output should contain header"
    assert "Total valid trips found:" in output_2025, "Output should contain trip count" 