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
pytest tests/test_data_processor.py -v
pytest tests/test_graph_builder.py -v
pytest tests/test_nba_trip_planner.py -v
```

### Processing Future NBA Seasons

For future NBA seasons, use the PDF parser in the `utils/` directory:

1. **Download the official NBA schedule PDF** from nba.com
2. **Parse the PDF to CSV format**:
   ```bash
   cd utils
   python parse_pdf.py <nba_schedule.pdf>
   ```
3. **Filter the generated CSV** to include only games for target teams (Washington, Philadelphia, New York, Brooklyn, Boston)
4. **Copy the filtered CSV** to the `data/csv/` directory

### Running the Trip Planner

Generate NBA trip schedules using any season's data:
```bash
python nba_trip_planner.py <csv_filename>
```

Examples:
```bash
# For 2024-25 season data
python nba_trip_planner.py 2024_nba_data.csv

# For 2025-26 season data  
python nba_trip_planner.py 2025_nba_data.csv
```

This will:
- Load and process the specified NBA schedule data
- Build a graph of valid game transitions
- Find all valid 3-5 night trips including Wizards
- Rank trips by length and travel efficiency
- Save results to `results/nba_trips_YYYYMMDD_HHMMSS.txt`

## 📝 CSV Data Format Specification

Input CSV files must conform to the following standardized format for compatibility with the trip planner:

### Required Headers
```csv
Game Date,Start (ET),Visitor,Home,Arena,Notes
```

### Column Specifications

1. **Game Date**: Game date in one of these formats:
   - `MM/DD/YYYY` (e.g., `10/22/2024`)
   - `"Day, Mon DD, YYYY"` (e.g., `"Wed, Oct 22, 2025"`)

2. **Start (ET)**: Game start time in Eastern Time
   - Format: `H:MMp` or `HH:MMp` (e.g., `7:30p`, `12:00p`)
   - Always include 'p' for PM or 'a' for AM

3. **Visitor**: Visiting team name
   - Use city names (e.g., `Boston`, `New York`, `Philadelphia`)
   - Full team names also supported (e.g., `Boston Celtics`, `New York Knicks`)

4. **Home**: Home team name  
   - Use city names (e.g., `Boston`, `New York`, `Philadelphia`)
   - Full team names also supported (e.g., `Boston Celtics`, `New York Knicks`)

5. **Arena**: Venue name
   - Full arena name (e.g., `TD Garden`, `Madison Square Garden`)

6. **Notes**: Optional additional information
   - Special game designations (e.g., `NBA Cup`, `Christmas Day`)
   - Can be empty

### Example Rows
```csv
Game Date,Start (ET),Visitor,Home,Arena,Notes
10/22/2024,7:30p,New York,Boston,TD Garden,
"Wed, Oct 22, 2025",7:00p,Cleveland,New York,Madison Square Garden,
12/25/2024,12:00p,San Antonio,New York,Madison Square Garden,Christmas Day
11/12/2024,7:00p,Atlanta,Boston,TD Garden,NBA Cup
```

### Target Teams
The system filters for home games of these five teams:
- **Washington Wizards** (Washington)
- **Philadelphia 76ers** (Philadelphia)  
- **New York Knicks** (New York)
- **Brooklyn Nets** (Brooklyn)
- **Boston Celtics** (Boston)

## 📁 Project Structure

```
nba-reg-season-trip-planner/
├── README.md                    # Project documentation
├── requirements.txt             # Python dependencies
├── .gitignore                   # Git ignore rules
├── CLAUDE.md                    # Claude Code guidance
├── nba_trip_planner.py         # Main entry point script
├── data/                        # NBA schedule data files
│   ├── csv/                   # Processed CSV schedule data
│   │   ├── 2024_nba_data.csv # 2024-25 season data
│   │   └── 2025_nba_data.csv # 2025-26 season data (filtered)
│   └── pdf/                   # Original PDF schedule files
│       └── 2025_schedule.pdf  # 2025-26 season PDF
├── utils/                       # Core utilities and modules
│   ├── __init__.py             # Python package marker
│   ├── data_processor.py       # CSV parsing and data cleaning
│   ├── graph_builder.py        # Graph construction and edge creation
│   └── parse_pdf.py            # PDF to CSV converter
├── tests/                       # Test files
│   ├── __init__.py             # Python package marker
│   ├── test_data_processor.py  # Data processor tests
│   ├── test_graph_builder.py   # Graph builder tests
│   └── test_nba_trip_planner.py # End-to-end integration tests
├── results/                     # Generated trip schedules
└── venv/                        # Virtual environment
```

## 🔧 Key Components

### Data Processor (`utils/data_processor.py`)
- Loads and cleans NBA schedule CSV data from multiple formats
- Handles different date formats (`10/22/2024` vs `"Wed, Oct 22, 2025"`)
- Normalizes column names across different CSV structures
- Standardizes team names (e.g., "Boston Celtics" → "Celtics", "Boston" → "Celtics")
- Filters to target teams' home games
- Adds geographic ordering information

### Graph Builder (`utils/graph_builder.py`)
- Creates directed graph of NBA games
- Nodes represent individual games (team, date, opponent, venue)
- Edges represent valid consecutive-night transitions
- Respects geographic direction constraints
- Handles NYC special case (Knicks/Nets same location)

### Trip Planner (`nba_trip_planner.py`)
- Main entry point script that orchestrates the entire process
- Uses DFS to find all valid 3-5 night trips
- Ensures Wizards inclusion in all trips
- Prevents team repetition within trips
- Ranks trips by length and travel efficiency
- Generates detailed output with timestamps

### PDF Parser (`utils/parse_pdf.py`)
- Converts official NBA schedule PDFs to CSV format
- Handles multiple PDF parsing libraries for robustness
- Extracts game data, dates, times, TV info, and special codes
- Identifies NBA Cup games and international venues
- Normalizes data to match expected CSV format

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
- **pdfplumber** ≥ 0.11.7: PDF processing (for future seasons)
- **pypdf2** ≥ 3.0.1: Alternative PDF processing
- **pymupdf** ≥ 1.26.3: PDF parsing library

## 🎯 Complete Workflow

### For New NBA Seasons (e.g., 2025-26)

1. **Download NBA Schedule PDF** from official NBA website
2. **Parse PDF to CSV**:
   ```bash
   cd utils
   python parse_pdf.py ../data/pdf/2025_schedule.pdf
   ```
3. **Filter to Target Teams**: Extract only games for Wizards, 76ers, Knicks, Nets, Celtics
4. **Save Filtered Data**: Copy filtered CSV to `data/csv/` directory as `YYYY_nba_data.csv`
5. **Generate Trip Plans**:
   ```bash
   python nba_trip_planner.py 2025_nba_data.csv
   ```

### Algorithm Overview

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