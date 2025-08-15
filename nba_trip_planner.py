import networkx as nx
import os
import sys
from datetime import datetime
from utils.data_processor import load_and_clean_csv
from utils.graph_builder import build_game_graph

def find_all_valid_trips(graph):
    """
    Find all valid trips that include Wizards games.
    
    Args:
        graph (nx.DiGraph): Game graph with valid transitions
        
    Returns:
        list: List of valid trip paths (each path is a list of GameNode objects)
    """
    all_trips = []
    
    # Get all Wizards games as potential anchors
    wizards_games = [node for node in graph.nodes() if node.team == "Wizards"]
    
    for wizards_game in wizards_games:
        # Find northbound trips (starting with Wizards)
        northbound_trips = find_northbound_trips(graph, wizards_game)
        all_trips.extend(northbound_trips)
        
        # Find southbound trips (ending with Wizards)
        southbound_trips = find_southbound_trips(graph, wizards_game)
        all_trips.extend(southbound_trips)
    
    return all_trips

def find_northbound_trips(graph, wizards_game):
    """
    Find northbound trips starting from a Wizards game.
    
    Args:
        graph (nx.DiGraph): Game graph
        wizards_game (GameNode): Starting Wizards game
        
    Returns:
        list: List of valid northbound trip paths
    """
    trips = []
    
    def dfs_northbound(current_node, visited_teams, path):
        # Add current node to path
        current_path = path + [current_node]
        current_teams = visited_teams | {current_node.team}
        
        # If path is 3-5 games and includes Wizards, it's valid
        if 3 <= len(current_path) <= 5 and "Wizards" in current_teams:
            trips.append(current_path)
        
        # Continue DFS if under max length
        if len(current_path) < 5:
            for neighbor in graph.successors(current_node):
                # Check if edge is northbound
                if graph.edges[current_node, neighbor].get('direction') == 'northbound':
                    # Check if we haven't visited this team yet
                    if neighbor.team not in current_teams:
                        dfs_northbound(neighbor, current_teams, current_path)
    
    # Start DFS from Wizards game
    dfs_northbound(wizards_game, set(), [])
    return trips

def find_southbound_trips(graph, wizards_game):
    """
    Find southbound trips ending at a Wizards game.
    
    Args:
        graph (nx.DiGraph): Game graph
        wizards_game (GameNode): Ending Wizards game
        
    Returns:
        list: List of valid southbound trip paths
    """
    trips = []
    
    def dfs_southbound(current_node, visited_teams, path):
        # Add current node to path
        current_path = path + [current_node]
        current_teams = visited_teams | {current_node.team}
        
        # If we reached Wizards and path is 3-5 games, it's valid
        if current_node.team == "Wizards" and 3 <= len(current_path) <= 5:
            trips.append(current_path)
        
        # Continue DFS if under max length
        if len(current_path) < 5:
            for neighbor in graph.successors(current_node):
                # Check if edge is southbound
                if graph.edges[current_node, neighbor].get('direction') == 'southbound':
                    # Check if we haven't visited this team yet
                    if neighbor.team not in current_teams:
                        dfs_southbound(neighbor, current_teams, current_path)
    
    # Start DFS from all possible starting points
    for start_node in graph.nodes():
        if start_node.team != "Wizards":
            dfs_southbound(start_node, set(), [])
    
    return trips

def rank_trips(trips):
    """
    Rank trips by length (descending) and travel efficiency.
    
    Args:
        trips (list): List of trip paths
        
    Returns:
        dict: Ranked trips grouped by length and direction
    """
    if not trips:
        return {}
    
    # Remove duplicates (same games in same order)
    unique_trips = []
    seen = set()
    for trip in trips:
        trip_key = tuple((node.team, node.date) for node in trip)
        if trip_key not in seen:
            seen.add(trip_key)
            unique_trips.append(trip)
    
    # Group by length
    trips_by_length = {}
    for trip in unique_trips:
        length = len(trip)
        if length not in trips_by_length:
            trips_by_length[length] = []
        trips_by_length[length].append(trip)
    
    # Sort within each length group by travel efficiency
    # (fewer geographic jumps = more efficient)
    for length in trips_by_length:
        trips_by_length[length].sort(key=lambda trip: calculate_travel_efficiency(trip))
    
    return trips_by_length

def calculate_travel_efficiency(trip):
    """
    Calculate travel efficiency score (lower = more efficient).
    
    Args:
        trip (list): List of GameNode objects
        
    Returns:
        int: Travel efficiency score
    """
    if len(trip) <= 1:
        return 0
    
    # Count geographic jumps (changes in geo_order)
    jumps = 0
    geo_order = {"Wizards": 1, "76ers": 2, "Knicks": 3, "Nets": 3, "Celtics": 4}
    
    for i in range(1, len(trip)):
        prev_order = geo_order[trip[i-1].team]
        curr_order = geo_order[trip[i].team]
        if prev_order != curr_order:
            jumps += 1
    
    return jumps

def format_output(ranked_trips):
    """
    Create human-readable trip descriptions and export to results/ directory.
    
    Args:
        ranked_trips (dict): Ranked trips grouped by length
        
    Returns:
        str: Summary of results
    """
    # Create results directory if it doesn't exist
    os.makedirs("results", exist_ok=True)
    
    # Generate timestamp hash for filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"results/nba_trips_{timestamp}.txt"
    
    output_lines = []
    output_lines.append("NBA TRIP PLANNER RESULTS")
    output_lines.append("=" * 50)
    output_lines.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output_lines.append("")
    
    total_trips = sum(len(trips) for trips in ranked_trips.values())
    output_lines.append(f"Total valid trips found: {total_trips}")
    output_lines.append("")
    
    # Always show headers for all trip lengths (5, 4, 3 nights)
    for length in [5, 4, 3]:
        trips = ranked_trips.get(length, [])
        output_lines.append(f"=== {length}-NIGHT TRIPS ({len(trips)} found) ===")
        output_lines.append("")
        
        if trips:
            for i, trip in enumerate(trips, 1):
                output_lines.append(f"Trip {i}:")
                
                # Determine direction
                geo_order = {"Wizards": 1, "76ers": 2, "Knicks": 3, "Nets": 3, "Celtics": 4}
                first_order = geo_order[trip[0].team]
                last_order = geo_order[trip[-1].team]
                
                if first_order < last_order:
                    direction = "NORTHBOUND"
                elif first_order > last_order:
                    direction = "SOUTHBOUND"
                else:
                    direction = "LOCAL"
                output_lines.append(f"  Direction: {direction}")

                # Add Cities line (unique, ordered)
                cities = []
                seen = set()
                # Map teams to actual city names
                city_mapping = {
                    "Wizards": "Washington DC",
                    "76ers": "Philadelphia", 
                    "Knicks": "New York City",
                    "Nets": "New York City",
                    "Celtics": "Boston"
                }
                for game in trip:
                    city = city_mapping.get(game.team, game.team)
                    if city not in seen:
                        seen.add(city)
                        cities.append(city)
                output_lines.append(f"  Cities: {' -> '.join(cities)}")

                output_lines.append(f"  Travel Efficiency: {calculate_travel_efficiency(trip)} jumps")
                output_lines.append("  Schedule:")
                
                for j, game in enumerate(trip, 1):
                    output_lines.append(f"    Night {j}: {game.team} vs {game.opponent}")
                    output_lines.append(f"           Date: {game.date.strftime('%Y-%m-%d')}")
                    output_lines.append(f"           Venue: {game.venue}")
                    output_lines.append("")
                
                output_lines.append("-" * 30)
                output_lines.append("")
        else:
            output_lines.append("  No valid trips found for this length.")
            output_lines.append("")
    
    # Write to file
    output_content = "\n".join(output_lines)
    with open(filename, "w") as f:
        f.write(output_content)
    
    return output_content

def main():
    """
    Main execution function for NBA trip planner.
    """
    # Check for command line argument
    if len(sys.argv) < 2:
        print("Usage: python nba_trip_planner.py <csv_filename>")
        print("Example: python nba_trip_planner.py 2025_nba_data.csv")
        return 1
    
    csv_filename = sys.argv[1]
    
    # If filename doesn't include path, check in data/csv directory
    if not os.path.sep in csv_filename:
        csv_path = os.path.join('data', 'csv', csv_filename)
    else:
        csv_path = csv_filename
    
    # Check if file exists
    if not os.path.exists(csv_path):
        print(f"Error: File '{csv_path}' not found.")
        print("Available data files:")
        data_csv_dir = os.path.join('data', 'csv')
        if os.path.exists(data_csv_dir):
            for file in os.listdir(data_csv_dir):
                if file.endswith('.csv'):
                    print(f"  {file}")
        return 1
    
    print(f"NBA Trip Planner - Loading and processing data from {csv_filename}...")
    
    try:
        # Load and clean data
        print("1. Loading NBA schedule data...")
        df = load_and_clean_csv(csv_path)
        print(f"   Loaded {len(df)} games for target teams")
        
        # Build graph
        print("2. Building game graph...")
        graph = build_game_graph(df)
        print(f"   Created graph with {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges")
        
        # Find trips
        print("3. Finding valid trips...")
        trips = find_all_valid_trips(graph)
        print(f"   Found {len(trips)} potential trips")
        
        # Rank trips
        print("4. Ranking trips...")
        ranked_trips = rank_trips(trips)
        
        # Format and output results
        print("5. Formatting output...")
        output = format_output(ranked_trips)
        
        # Print summary
        print("\n" + "=" * 50)
        print("TRIP PLANNING COMPLETE!")
        print("=" * 50)
        
        total_trips = sum(len(trips) for trips in ranked_trips.values())
        print(f"Total valid trips found: {total_trips}")
        
        for length in sorted(ranked_trips.keys(), reverse=True):
            trips = ranked_trips[length]
            print(f"{length}-night trips: {len(trips)}")
        
        # Get the actual filename that was created
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"results/nba_trips_{timestamp}.txt"
        print(f"\nResults saved to: {filename}")
        print("\nTop 3 trips:")
        
        # Show top 3 trips
        count = 0
        for length in sorted(ranked_trips.keys(), reverse=True):
            for trip in ranked_trips[length]:
                if count >= 3:
                    break
                print(f"  {length}-night trip: {' -> '.join(node.team for node in trip)}")
                count += 1
            if count >= 3:
                break
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    main()