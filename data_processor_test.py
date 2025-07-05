#!/usr/bin/env python3
"""
Test script for data_processor.py functionality using pytest
"""

import pytest
import pandas as pd
from data_processor import load_and_clean_csv, standardize_team_names, filter_target_teams, add_geographic_info

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
    df = load_and_clean_csv('2024_nba_data.csv')
    
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