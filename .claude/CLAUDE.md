# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NBA Regular Season Trip Planner - An intelligent scheduling system that finds optimal multi-night NBA game viewing trips across northeastern US cities (Wizards, 76ers, Knicks, Nets, Celtics) with geographic travel constraints.

## Commands

### Environment Setup
```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Development Commands
```bash
# Run the main application
python nba_trip_planner.py

# Run all tests
pytest -v

# Run specific test modules
pytest data_processor_test.py -v
pytest graph_builder_test.py -v
pytest nba_trip_planner_test.py -v
```

## Architecture

### Core Modules
1. **data_processor.py**: CSV data loading and cleaning
   - Entry point: `load_and_clean_csv()`
   - Filters to target teams' home games
   - Adds geographic ordering for trip planning

2. **graph_builder.py**: Directed graph construction
   - `GameNode` class represents individual games
   - `build_game_graph()` creates NetworkX graph with valid consecutive-night transitions
   - Enforces geographic constraints (northbound/southbound travel)

3. **nba_trip_planner.py**: Main DFS algorithm
   - Finds 3-5 night trips with mandatory Wizards games
   - Prevents team repetition within trips
   - Outputs timestamped results to `results/` directory

### Key Constraints
- **Geographic Order**: DC → Philadelphia → NYC → Boston (or reverse)
- **NYC Special Case**: Knicks and Nets treated as same location
- **Mandatory**: All trips must include Washington Wizards
- **Trip Length**: 3-5 consecutive nights only
- **Travel Direction**: Either northbound OR southbound, not mixed

### Data Flow
CSV Schedule → Data Processor → Graph Builder → Trip Planner → Results File

## Testing Approach

Use pytest for all testing. Tests are organized by module with comprehensive coverage of edge cases, geographic constraints, and integration scenarios.

## Future Season Support

The `202526/` directory contains infrastructure for processing future NBA seasons from PDF schedules using `parse_pdf.py`.