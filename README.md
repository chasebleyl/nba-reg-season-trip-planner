# NBA Trip Planner

This was hacked together to help me identify optimal sequencing of NBA home games in the northeast, so cities Washington DC, Philidelphia, New York City, & Boston.

An intelligent trip planning system that finds optimal NBA game viewing schedules across northeastern US cities, visiting multiple teams on consecutive nights while respecting geographic travel constraints.

## Vibe coding

This was heavily vibe-coded:
- I started in Claude, figuring out how this should be solved
- I copied/pasted generated prompt instructions from Claude into Cursor
- I iterated with Cursor on the implementation of each sub-section

Most of this likely could be improved. I don't care.

## 🏀 Problem Statement

Find optimal NBA game viewing schedules that:
- Visit 3-5 NBA teams across consecutive nights
- **MUST include Washington Wizards** (mandatory)
- Include other teams: Philadelphia 76ers, New York Knicks, Brooklyn Nets, Boston Celtics
- Respect geographic constraints: Only travel North OR South (no backtracking)
- Each game takes one night (can see both NYC teams on different nights)

## 🗺️ Geographic Ordering

**South to North**: Washington DC → Philadelphia → New York City → Boston  
**North to South**: Boston → New York City → Philadelphia → Washington DC

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd nba-reg-season-trip-planner
   ```

2. **Create and activate virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Running Tests

Run all tests to verify the implementation:
```bash
pytest -v
```

Run specific test modules:
```bash
pytest test_data_processor.py -v
pytest test_graph_builder.py -v
pytest test_nba_trip_planner.py -v
```

### Running the Trip Planner

Generate NBA trip schedules:
```bash
python nba_trip_planner.py
```

This will:
- Load and process the 2024-25 NBA schedule data
- Build a graph of valid game transitions
- Find all valid 3-5 night trips including Wizards
- Rank trips by length and travel efficiency
- Save results to `results/nba_trips_YYYYMMDD_HHMMSS.txt`

## 📁 Project Structure

```
nba-reg-season-trip-planner/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── .gitignore                   # Git ignore rules
├── 2024_nba_data.csv           # NBA schedule data
├── data_processor.py           # CSV parsing and data cleaning
├── graph_builder.py            # Graph construction and edge creation
├── nba_trip_planner.py         # Main algorithm and execution
├── test_data_processor.py      # Data processor tests
├── test_graph_builder.py       # Graph builder tests
├── test_nba_trip_planner.py    # End-to-end tests
└── results/                    # Output directory for trip schedules
```

## 🔧 Key Components

### Data Processor (`data_processor.py`)
- Loads and cleans NBA schedule CSV data
- Standardizes team names (e.g., "Boston Celtics" → "Celtics")
- Filters to target teams' home games
- Adds geographic ordering information

### Graph Builder (`graph_builder.py`)
- Creates directed graph of NBA games
- Nodes represent individual games (team, date, opponent, venue)
- Edges represent valid consecutive-night transitions
- Respects geographic direction constraints
- Handles NYC special case (Knicks/Nets same location)

### Trip Planner (`nba_trip_planner.py`)
- Uses DFS to find all valid 3-5 night trips
- Ensures Wizards inclusion in all trips
- Prevents team repetition within trips
- Ranks trips by length and travel efficiency
- Generates detailed output with timestamps

## 📊 Output Format

The system generates detailed trip reports including:

- **Direction**: NORTHBOUND or SOUTHBOUND
- **Cities**: Actual cities visited in order (Washington DC, Philadelphia, New York City, Boston)
- **Travel Efficiency**: Number of geographic jumps
- **Schedule**: Detailed game information (dates, teams, opponents, venues)

Example output:
```
Trip 1:
  Direction: SOUTHBOUND
  Cities: Boston -> New York City -> Washington DC
  Travel Efficiency: 2 jumps
  Schedule:
    Night 1: Celtics vs Miami Heat
           Date: 2024-12-02
           Venue: TD Garden
    ...
```

## 🧪 Testing

The project includes tests:

- **Unit tests** for each component
- **Integration tests** for the complete pipeline
- **Edge case tests** (e.g., zero 5-night trips)
- **Constraint validation** (geographic, consecutive nights, team repetition)

Run tests with:
```bash
pytest -v
```

## 📋 Requirements

- **pandas** ≥ 2.0.0: Data manipulation and CSV processing
- **networkx** ≥ 3.0: Graph algorithms and path finding
- **pytest** ≥ 7.0.0: Testing framework

## 🎯 Algorithm Overview

1. **Data Processing**: Clean and filter NBA schedule data
2. **Graph Construction**: Build directed graph with valid transitions
3. **Path Finding**: Use DFS to find all valid 3-5 night trips
4. **Ranking**: Sort by trip length (5 > 4 > 3) and travel efficiency
5. **Output**: Generate detailed reports with timestamps

## 🔍 Key Constraints Implemented

- ✅ Consecutive nights only (no gaps)
- ✅ Geographic flow (north-only or south-only travel)
- ✅ Wizards inclusion mandatory
- ✅ No team repetition within a single trip
- ✅ NYC teams (Knicks/Nets) treated as separate nights but same geographic location
- ✅ Trip length 3-5 nights
- ✅ Travel efficiency optimization

## 📈 Results

All trips are ranked by travel efficiency and include detailed scheduling information.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE). 