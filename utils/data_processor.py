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
    
    # Normalize column names to handle different formats
    df = normalize_column_names(df)
    
    # Convert 'Game Date' column to datetime objects (handle different formats)
    df['Game Date'] = parse_game_dates(df['Game Date'])
    
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

def normalize_column_names(df):
    """
    Normalize column names to handle different CSV formats.
    
    Args:
        df (pandas.DataFrame): Raw DataFrame from CSV
        
    Returns:
        pandas.DataFrame: DataFrame with normalized column names
    """
    # Create column mapping for different formats
    column_mapping = {
        'Start (ET)': 'Game Time',
        'Visitor/Neutral': 'Visitor', 
        'Home/Neutral': 'Home'
    }
    
    # Rename columns if they exist
    df = df.rename(columns=column_mapping)
    
    return df

def parse_game_dates(date_series):
    """
    Parse game dates handling different date formats.
    
    Args:
        date_series (pandas.Series): Series containing date strings
        
    Returns:
        pandas.Series: Series with parsed datetime objects
    """
    # Try different date formats
    formats_to_try = [
        '%m/%d/%Y',  # 2024 format: "10/22/2024"
        '%a, %b %d, %Y'  # 2025 format: "Wed, Oct 22, 2025"
    ]
    
    # First check a sample to determine format
    sample_date = str(date_series.iloc[0]).strip('"')
    
    for fmt in formats_to_try:
        try:
            # Test with first date
            datetime.strptime(sample_date, fmt)
            # If successful, apply to whole series
            return pd.to_datetime(date_series.str.strip('"'), format=fmt)
        except ValueError:
            continue
    
    # If no format worked, try pandas auto-detection
    try:
        return pd.to_datetime(date_series.str.strip('"'))
    except Exception as e:
        raise ValueError(f"Could not parse dates. Sample: {sample_date}. Error: {e}")

def standardize_team_names(team_name):
    """
    Convert full team names to standardized short names.
    
    Args:
        team_name (str): Full team name (e.g., "Boston Celtics") or city name (e.g., "Boston")
        
    Returns:
        str: Standardized short name (e.g., "Celtics")
    """
    team_mapping = {
        # Full team names (2024 format)
        "Boston Celtics": "Celtics",
        "Philadelphia 76ers": "76ers", 
        "New York Knicks": "Knicks",
        "Brooklyn Nets": "Nets",
        "Washington Wizards": "Wizards",
        # City names (2025 format)
        "Boston": "Celtics",
        "Philadelphia": "76ers",
        "New York": "Knicks", 
        "Brooklyn": "Nets",
        "Washington": "Wizards",
        # Already standardized names (pass through)
        "Celtics": "Celtics",
        "76ers": "76ers",
        "Knicks": "Knicks",
        "Nets": "Nets", 
        "Wizards": "Wizards"
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