import pandas as pd
from datetime import datetime

def load_and_clean_csv(filename):
    """
    Load and clean NBA schedule data from CSV file.
    
    Args:
        filename (str): Path to the CSV file containing NBA schedule data
        
    Returns:
        pandas.DataFrame: Cleaned DataFrame with standardized team names, 
                         filtered to target teams, and geographic information
    """
    # Load CSV using pandas
    df = pd.read_csv(filename)
    
    # Convert 'Game Date' column to datetime objects
    df['Game Date'] = pd.to_datetime(df['Game Date'], format='%m/%d/%Y')
    
    # Standardize team names (map full names to short names)
    df['Home'] = df['Home'].apply(standardize_team_names)
    df['Visitor'] = df['Visitor'].apply(standardize_team_names)
    
    # Filter to only target teams' home games
    df = filter_target_teams(df)
    
    # Add geographic ordering column
    df = add_geographic_info(df)
    
    # Sort by date for easier processing
    df = df.sort_values('Game Date').reset_index(drop=True)
    
    return df

def standardize_team_names(team_name):
    """
    Convert full team names to standardized short names.
    
    Args:
        team_name (str): Full team name (e.g., "Boston Celtics")
        
    Returns:
        str: Standardized short name (e.g., "Celtics")
    """
    team_mapping = {
        "Boston Celtics": "Celtics",
        "Philadelphia 76ers": "76ers", 
        "New York Knicks": "Knicks",
        "Brooklyn Nets": "Nets",
        "Washington Wizards": "Wizards"
    }
    
    return team_mapping.get(team_name, team_name)

def filter_target_teams(df):
    """
    Keep only rows where Home team is one of our 5 targets.
    
    Args:
        df (pandas.DataFrame): DataFrame with NBA schedule data
        
    Returns:
        pandas.DataFrame: Filtered DataFrame with only target teams' home games
    """
    target_teams = ["Wizards", "76ers", "Knicks", "Nets", "Celtics"]
    
    # Filter to only include home games for our target teams
    filtered_df = df[df['Home'].isin(target_teams)].copy()
    
    return filtered_df

def add_geographic_info(df):
    """
    Add geographic ordering information for trip planning.
    
    Args:
        df (pandas.DataFrame): DataFrame with NBA schedule data
        
    Returns:
        pandas.DataFrame: DataFrame with added geographic columns
    """
    # Geographic ordering: South to North
    # 1 = Wizards (Washington DC)
    # 2 = 76ers (Philadelphia) 
    # 3 = Knicks/Nets (New York City)
    # 4 = Celtics (Boston)
    
    geo_order_mapping = {
        "Wizards": 1,
        "76ers": 2, 
        "Knicks": 3,
        "Nets": 3,  # Same geographic position as Knicks
        "Celtics": 4
    }
    
    # Add geographic order column
    df['geo_order'] = df['Home'].map(geo_order_mapping)
    
    # Add city group for NYC handling (Knicks and Nets are in same city)
    df['city_group'] = df['Home'].apply(lambda x: 'NYC' if x in ['Knicks', 'Nets'] else x)
    
    return df