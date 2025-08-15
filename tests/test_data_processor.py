#!/usr/bin/env python3
"""
Test script for data_processor.py functionality using pytest
"""

import pytest
import pandas as pd
from datetime import datetime
from utils.data_processor import (
    load_and_clean_csv, 
    standardize_team_names, 
    filter_target_teams, 
    add_geographic_info,
    normalize_column_names,
    parse_game_dates
)

def test_standardize_team_names():
    """Test team name standardization"""
    test_teams = ["Boston Celtics", "Philadelphia 76ers", "New York Knicks", "Brooklyn Nets", "Washington Wizards"]
    expected = ["Celtics", "76ers", "Knicks", "Nets", "Wizards"]
    
    for team, expected_name in zip(test_teams, expected):
        result = standardize_team_names(team)
        assert result == expected_name, f"Expected {expected_name}, got {result} for {team}"

def test_filter_target_teams():
    """Test filtering to target teams"""
    # Create test data
    data = [
        {"Home": "Wizards", "Visitor": "Celtics"},
        {"Home": "76ers", "Visitor": "Wizards"},
        {"Home": "Lakers", "Visitor": "Celtics"},  # Non-target team
        {"Home": "Knicks", "Visitor": "Nets"},
    ]
    df = pd.DataFrame(data)
    
    filtered = filter_target_teams(df)
    assert len(filtered) == 3, f"Expected 3 teams, got {len(filtered)}"
    assert "Lakers" not in filtered['Home'].values, "Non-target team should be filtered out"

def test_add_geographic_info():
    """Test geographic information addition"""
    data = [
        {"Home": "Wizards", "Visitor": "Celtics"},
        {"Home": "76ers", "Visitor": "Wizards"},
        {"Home": "Knicks", "Visitor": "Nets"},
        {"Home": "Nets", "Visitor": "Celtics"},
        {"Home": "Celtics", "Visitor": "Wizards"},
    ]
    df = pd.DataFrame(data)
    
    result = add_geographic_info(df)
    
    # Check geo_order
    assert result.loc[result['Home'] == 'Wizards', 'geo_order'].iloc[0] == 1
    assert result.loc[result['Home'] == '76ers', 'geo_order'].iloc[0] == 2
    assert result.loc[result['Home'] == 'Knicks', 'geo_order'].iloc[0] == 3
    assert result.loc[result['Home'] == 'Nets', 'geo_order'].iloc[0] == 3
    assert result.loc[result['Home'] == 'Celtics', 'geo_order'].iloc[0] == 4
    
    # Check city_group
    assert result.loc[result['Home'] == 'Knicks', 'city_group'].iloc[0] == 'NYC'
    assert result.loc[result['Home'] == 'Nets', 'city_group'].iloc[0] == 'NYC'

def test_load_and_clean_csv():
    """Test complete data loading and cleaning pipeline"""
    df = load_and_clean_csv('data/csv/2024_nba_data.csv')
    
    # Verify basic structure
    assert len(df) > 0, "DataFrame should not be empty"
    assert 'Home' in df.columns, "Home column should exist"
    assert 'Game Date' in df.columns, "Game Date column should exist"
    
    # Verify target teams
    target_teams = {"Wizards", "76ers", "Knicks", "Nets", "Celtics"}
    actual_teams = set(df['Home'].unique())
    assert actual_teams == target_teams, f"Expected {target_teams}, got {actual_teams}"
    
    # Verify Wizards games exist
    wizards_games = df[df['Home'] == 'Wizards']
    assert len(wizards_games) > 0, "No Wizards games found"
    
    # Verify geographic info
    assert 'geo_order' in df.columns, "geo_order column should exist"
    assert 'city_group' in df.columns, "city_group column should exist"
    assert df['geo_order'].notna().all(), "All rows should have geographic order"
    
    # Verify NYC teams are grouped correctly
    nyc_teams = set(df[df['city_group'] == 'NYC']['Home'].unique())
    assert nyc_teams == {'Knicks', 'Nets'}, f"NYC teams should be Knicks and Nets, got {nyc_teams}"

def test_normalize_column_names():
    """Test column name normalization for different CSV formats"""
    # Test 2025 format (needs normalization)
    df_2025 = pd.DataFrame({
        'Game Date': ['2025-10-22'],
        'Start (ET)': ['7:00p'],
        'Visitor/Neutral': ['Cleveland'],
        'Home/Neutral': ['New York'],
        'Arena': ['Madison Square Garden'],
        'Notes': ['']
    })
    
    normalized = normalize_column_names(df_2025)
    
    # Check that columns were renamed correctly
    assert 'Game Time' in normalized.columns, "Start (ET) should be renamed to Game Time"
    assert 'Visitor' in normalized.columns, "Visitor/Neutral should be renamed to Visitor"
    assert 'Home' in normalized.columns, "Home/Neutral should be renamed to Home"
    assert 'Start (ET)' not in normalized.columns, "Start (ET) should be renamed"
    assert 'Visitor/Neutral' not in normalized.columns, "Visitor/Neutral should be renamed"
    assert 'Home/Neutral' not in normalized.columns, "Home/Neutral should be renamed"
    
    # Test 2024 format (already normalized)
    df_2024 = pd.DataFrame({
        'Game Date': ['10/22/2024'],
        'Game Time': ['7:30p'],
        'Visitor': ['New York Knicks'],
        'Home': ['Boston Celtics'],
        'Arena': ['TD Garden'],
        'Notes': ['']
    })
    
    normalized_2024 = normalize_column_names(df_2024)
    
    # Check that columns remain unchanged
    assert 'Game Time' in normalized_2024.columns, "Game Time should remain"
    assert 'Visitor' in normalized_2024.columns, "Visitor should remain"
    assert 'Home' in normalized_2024.columns, "Home should remain"

def test_parse_game_dates():
    """Test date parsing for different formats"""
    # Test 2024 format (MM/DD/YYYY)
    dates_2024 = pd.Series(['10/22/2024', '10/23/2024', '12/25/2024'])
    parsed_2024 = parse_game_dates(dates_2024)
    
    assert isinstance(parsed_2024.iloc[0], pd.Timestamp), "Should return datetime objects"
    assert parsed_2024.iloc[0].year == 2024, "Year should be parsed correctly"
    assert parsed_2024.iloc[0].month == 10, "Month should be parsed correctly"
    assert parsed_2024.iloc[0].day == 22, "Day should be parsed correctly"
    
    # Test 2025 format ("Day, Mon DD, YYYY")
    dates_2025 = pd.Series(['"Wed, Oct 22, 2025"', '"Fri, Oct 24, 2025"', '"Thu, Dec 25, 2025"'])
    parsed_2025 = parse_game_dates(dates_2025)
    
    assert isinstance(parsed_2025.iloc[0], pd.Timestamp), "Should return datetime objects"
    assert parsed_2025.iloc[0].year == 2025, "Year should be parsed correctly"
    assert parsed_2025.iloc[0].month == 10, "Month should be parsed correctly"
    assert parsed_2025.iloc[0].day == 22, "Day should be parsed correctly"
    
    # Test Christmas dates specifically (known edge case)
    christmas_2024 = pd.Series(['12/25/2024'])
    christmas_parsed = parse_game_dates(christmas_2024)
    assert christmas_parsed.iloc[0].month == 12, "Christmas month should be December"
    assert christmas_parsed.iloc[0].day == 25, "Christmas day should be 25th"

def test_standardize_team_names_extended():
    """Test team name standardization for both 2024 and 2025 formats"""
    # Test 2024 format (full team names)
    full_names = ["Boston Celtics", "Philadelphia 76ers", "New York Knicks", "Brooklyn Nets", "Washington Wizards"]
    expected = ["Celtics", "76ers", "Knicks", "Nets", "Wizards"]
    
    for team, expected_name in zip(full_names, expected):
        result = standardize_team_names(team)
        assert result == expected_name, f"Expected {expected_name}, got {result} for {team}"
    
    # Test 2025 format (city names)
    city_names = ["Boston", "Philadelphia", "New York", "Brooklyn", "Washington"]
    
    for city, expected_name in zip(city_names, expected):
        result = standardize_team_names(city)
        assert result == expected_name, f"Expected {expected_name}, got {result} for {city}"
    
    # Test already standardized names (pass-through)
    for name in expected:
        result = standardize_team_names(name)
        assert result == name, f"Standardized name {name} should pass through unchanged"
    
    # Test unknown team name
    unknown_result = standardize_team_names("Los Angeles Lakers")
    assert unknown_result == "Los Angeles Lakers", "Unknown team names should pass through unchanged"

def test_load_and_clean_csv_2025_format():
    """Test complete data loading and cleaning pipeline with 2025 format"""
    df = load_and_clean_csv('data/csv/2025_nba_data.csv')
    
    # Verify basic structure
    assert len(df) > 0, "DataFrame should not be empty"
    assert 'Home' in df.columns, "Home column should exist"
    assert 'Game Date' in df.columns, "Game Date column should exist"
    
    # Verify target teams
    target_teams = {"Wizards", "76ers", "Knicks", "Nets", "Celtics"}
    actual_teams = set(df['Home'].unique())
    assert actual_teams == target_teams, f"Expected {target_teams}, got {actual_teams}"
    
    # Verify Wizards games exist
    wizards_games = df[df['Home'] == 'Wizards']
    assert len(wizards_games) > 0, "No Wizards games found"
    
    # Verify geographic info
    assert 'geo_order' in df.columns, "geo_order column should exist"
    assert 'city_group' in df.columns, "city_group column should exist"
    assert df['geo_order'].notna().all(), "All rows should have geographic order"
    
    # Verify NYC teams are grouped correctly
    nyc_teams = set(df[df['city_group'] == 'NYC']['Home'].unique())
    assert nyc_teams == {'Knicks', 'Nets'}, f"NYC teams should be Knicks and Nets, got {nyc_teams}"
    
    # Verify dates are parsed correctly (2025 data should have 2025 dates)
    assert df['Game Date'].dt.year.unique()[0] >= 2025, "2025 data should have 2025 or later dates" 