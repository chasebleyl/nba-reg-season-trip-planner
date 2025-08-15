import pandas as pd
import re
from datetime import datetime
import csv
import sys
import os

class NBASchedulePDFProcessor:
    def __init__(self):
        # Arena mappings based on team cities/names  
        self.arena_mappings = {
            'Atlanta': 'State Farm Arena',
            'Boston': 'TD Garden',
            'Brooklyn': 'Barclays Center', 
            'Charlotte': 'Spectrum Center',
            'Chicago': 'United Center',
            'Cleveland': 'Rocket Mortgage FieldHouse',
            'Dallas': 'American Airlines Center',
            'Denver': 'Ball Arena',
            'Detroit': 'Little Caesars Arena',
            'Golden State': 'Chase Center',
            'Houston': 'Toyota Center',
            'Indiana': 'Gainbridge Fieldhouse',
            'L.A. Clippers': 'Intuit Dome',
            'LA Clippers': 'Intuit Dome',
            'L.A. Lakers': 'Crypto.com Arena',
            'Memphis': 'FedExForum',
            'Miami': 'Kaseya Center',
            'Milwaukee': 'Fiserv Forum',
            'Minnesota': 'Target Center',
            'New Orleans': 'Smoothie King Center',
            'New York': 'Madison Square Garden',
            'Oklahoma City': 'Paycom Center', 
            'Orlando': 'Amway Center',
            'Philadelphia': 'Wells Fargo Center',
            'Phoenix': 'Footprint Center',
            'Portland': 'Moda Center',
            'Sacramento': 'Golden 1 Center',
            'San Antonio': 'Frost Bank Center',
            'Toronto': 'Scotiabank Arena',
            'Utah': 'Delta Center',
            'Washington': 'Capital One Arena'
        }
        
        # Special venues for international/neutral site games
        self.special_venues = {
            'A': 'Arena CDMX, Mexico City',
            'B': 'Uber Arena, Berlin',
            'D': 'The O2 Arena, London', 
            'E': 'Moody Center, Austin'
        }
        
        self.games = []
        self.failed_lines = []
        self.pdf_reader = None
    
    def check_pdf_exists(self, pdf_path):
        """Check if the PDF file exists in the filesystem"""
        if not os.path.exists(pdf_path):
            print(f"ERROR: PDF file not found: {pdf_path}")
            return False
        
        if not pdf_path.lower().endswith('.pdf'):
            print(f"ERROR: File is not a PDF: {pdf_path}")
            return False
        
        print(f"[OK] Found PDF file: {pdf_path}")
        return True
    
    def read_pdf_content(self, pdf_path):
        """Read PDF file content using available PDF parsers"""
        print(f"Reading PDF content from: {pdf_path}")
        
        # Try multiple PDF reading methods
        pdf_content = None
        
        # Method 1: Try pdfplumber (best for tabular data)
        pdf_content = self._try_pdfplumber(pdf_path)
        
        # Method 2: Try PyPDF2 if pdfplumber fails
        if not pdf_content:
            pdf_content = self._try_pypdf2(pdf_path)
        
        # Method 3: Try pymupdf if others fail
        if not pdf_content:
            pdf_content = self._try_pymupdf(pdf_path)
        
        if pdf_content:
            print(f"[OK] Successfully extracted {len(pdf_content)} characters from PDF")
            print(f"[OK] Found {len(pdf_content.split('\\n'))} lines in PDF")
            return pdf_content
        else:
            print("ERROR: Failed to read PDF with all available methods")
            return None
    
    def _try_pdfplumber(self, pdf_path):
        """Try reading PDF with pdfplumber"""
        try:
            import pdfplumber
            print("Attempting to read PDF with pdfplumber...")
            
            full_text = ""
            with pdfplumber.open(pdf_path) as pdf:
                print(f"PDF has {len(pdf.pages)} pages")
                
                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        full_text += page_text + "\\n"
                    print(f"  Processed page {page_num}")
            
            return full_text if full_text.strip() else None
            
        except ImportError:
            print("pdfplumber not available. Install with: pip install pdfplumber")
            return None
        except Exception as e:
            print(f"pdfplumber failed: {e}")
            return None
    
    def _try_pypdf2(self, pdf_path):
        """Try reading PDF with PyPDF2"""
        try:
            import PyPDF2
            print("Attempting to read PDF with PyPDF2...")
            
            full_text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                print(f"PDF has {len(pdf_reader.pages)} pages")
                
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        full_text += page_text + "\\n"
                    print(f"  Processed page {page_num}")
            
            return full_text if full_text.strip() else None
            
        except ImportError:
            print("PyPDF2 not available. Install with: pip install PyPDF2")
            return None
        except Exception as e:
            print(f"PyPDF2 failed: {e}")
            return None
    
    def _try_pymupdf(self, pdf_path):
        """Try reading PDF with PyMuPDF (fitz)"""
        try:
            import fitz  # PyMuPDF
            print("Attempting to read PDF with PyMuPDF...")
            
            full_text = ""
            doc = fitz.open(pdf_path)
            print(f"PDF has {len(doc)} pages")
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                page_text = page.get_text()
                if page_text:
                    full_text += page_text + "\\n"
                print(f"  Processed page {page_num + 1}")
            
            doc.close()
            return full_text if full_text.strip() else None
            
        except ImportError:
            print("PyMuPDF not available. Install with: pip install PyMuPDF")
            return None
        except Exception as e:
            print(f"PyMuPDF failed: {e}")
            return None
    
    def parse_pdf_content(self, pdf_content):
        """Parse the PDF content to extract NBA game data"""
        print("Parsing NBA schedule data from PDF content...")
        
        if not pdf_content:
            print("ERROR: No PDF content to parse")
            return False
        
        lines = pdf_content.split('\n')
        print(f"Processing {len(lines)} lines from PDF...")
        
        # DEBUG: Show first 20 lines to understand format
        print("\\n=== DEBUG: First 20 lines from PDF ===")
        for i, line in enumerate(lines[:20]):
            print(f"Line {i+1}: {repr(line)}")
        print("=== End DEBUG ===\\n")
        
        successful_parses = 0
        skipped_lines = 0
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Skip header/footer/metadata lines
            if self._should_skip_line(line):
                skipped_lines += 1
                if line_num <= 50:  # Show first 50 skipped lines for debugging
                    print(f"Skipped line {line_num}: {repr(line)}")
                continue
            
            # Split the line into individual game lines (handle multi-game lines)
            game_lines = self._split_into_game_lines(line)
            
            for game_line in game_lines:
                game_line = game_line.strip()
                if not game_line:
                    continue
                
                # Try to parse as a game line
                game_data = self._parse_game_line(game_line)
                if game_data:
                    self.games.append(game_data)
                    successful_parses += 1
                    print(f"[OK] Parsed game: {game_data}")
                else:
                    # Check if this looks like it should have been a game line
                    if self._looks_like_game_line(game_line):
                        self.failed_lines.append(f"Line {line_num}: {game_line}")
                        print(f"[WARN] Failed to parse potential game line {line_num}: {repr(game_line)}")
                        # DEBUG: Show what the regex pattern is trying to match
                        import re
                        pattern = r'^(\w{3}\.)\s+(\d{1,2}/\d{1,2}/\d{2,4})\s+(.+?)\s+(?:at|vs)\s+(.+?)\s+(\d{1,2}:\d{2}\s*(?:AM|PM))\s+(\d{1,2}:\d{2}\s*(?:AM|PM))(?:\s+(.*))?$'
                        match = re.match(pattern, game_line)
                        print(f"   DEBUG: Regex match result: {match}")
                        if match:
                            print(f"   DEBUG: Groups: {match.groups()}")
                    elif line_num <= 50:  # Show first 50 non-game lines for debugging
                        print(f"Non-game line {line_num}: {repr(game_line)}")
        
        print(f"[OK] Successfully parsed {successful_parses} games")
        print(f"[OK] Skipped {skipped_lines} non-game lines")
        
        if self.failed_lines:
            print(f"⚠ Failed to parse {len(self.failed_lines)} potential game lines")
            print("\\n=== Failed lines ===")
            for failed_line in self.failed_lines[:10]:  # Show first 10 failed lines
                print(failed_line)
            if len(self.failed_lines) > 10:
                print(f"... and {len(self.failed_lines) - 10} more")
            print("=== End failed lines ===\\n")
        
        return len(self.games) > 0
    
    def _should_skip_line(self, line):
        """Determine if a line should be skipped during parsing"""
        skip_patterns = [
            'DAY', 'DATE', 'TEAM 1', 'TEAM 2', 'LOCAL', 'ET', 'NAT TV', 'R #',
            'SUBJECT TO CHANGE', 'AS OF AUGUST', 'PAGE', 'SCHEDULE/ARENA NOTES:',
            'C - Emirates NBA Cup', 'A - Game to be played', 'B - Game to be played',
            'D - Game to be played', 'E - Games to be played', 'R - ESPN Radio',
            'ESPN Radio', 'SCHEDULE/ARENA NOTES', 'Emirates NBA Cup Group Play'
        ]
        
        line_upper = line.upper()
        
        # Check if line contains game data (day pattern) - handle multi-line content
        # Look for any day pattern followed by date pattern anywhere in the line
        has_game_data = re.search(r'(Mon\.|Tue\.|Wed\.|Thu\.|Fri\.|Sat\.|Sun\.)\s+\d{1,2}/\d{1,2}/\d{2,4}', line, re.DOTALL)
        
        # If line has game data, don't skip it even if it contains header text
        if has_game_data:
            return False
        
        # Skip if contains any skip pattern AND doesn't have game data
        if any(pattern in line_upper for pattern in skip_patterns):
            return True
        
        # Skip very short lines (likely not game data) - but be less aggressive
        if len(line) < 10:
            return True
        
        # Skip lines that are just page numbers or dates
        if re.match(r'^\d+$', line) or re.match(r'^\d{1,2}/\d{1,2}/\d{4}$', line):
            return True
        
        return False
    
    def _split_into_game_lines(self, line):
        """Split a line that may contain multiple games into individual game lines"""
        # Look for patterns that indicate the start of a new game
        # Games start with day abbreviations: Mon., Tue., Wed., Thu., Fri., Sat., Sun.
        game_pattern = r'(Mon\.|Tue\.|Wed\.|Thu\.|Fri\.|Sat\.|Sun\.)\s+\d{1,2}/\d{1,2}/\d{2,4}'
        
        # Find all matches of game starts
        matches = list(re.finditer(game_pattern, line))
        
        if len(matches) <= 1:
            # Only one or no games in this line, return as is
            return [line]
        
        # Split the line at each game start
        game_lines = []
        for i, match in enumerate(matches):
            start_pos = match.start()
            
            if i == 0:
                # First game - take from start to next game or end
                if i + 1 < len(matches):
                    end_pos = matches[i + 1].start()
                    game_lines.append(line[start_pos:end_pos].strip())
                else:
                    game_lines.append(line[start_pos:].strip())
            else:
                # Subsequent games - take from this game to next game or end
                if i + 1 < len(matches):
                    end_pos = matches[i + 1].start()
                    game_lines.append(line[start_pos:end_pos].strip())
                else:
                    game_lines.append(line[start_pos:].strip())
        
        return game_lines
    
    def _looks_like_game_line(self, line):
        """Check if a line looks like it should be a game line"""
        # Must contain date pattern
        if not re.search(r'\d{1,2}/\d{1,2}/\d{2,4}', line):
            return False
        
        # Must contain "at" or "vs"
        if ' at ' not in line and ' vs ' not in line:
            return False
        
        # Must contain time pattern
        if not re.search(r'\d{1,2}:\d{2}\s*(?:AM|PM)', line):
            return False
        
        return True
    
    def _parse_game_line(self, line):
        """Parse a single game line to extract game data"""
        
        # Main pattern for NBA schedule lines:
        # Day. Date Team1 at/vs Team2 LocalTime ETTime [TV Info] [Special Code]
        # Example: "Tue. 10/21/25 Houston at Oklahoma City 6:30 PM 7:30 PM NBC/Peacock R"
        # Example: "Thu. 1/15/26 Memphis vs Orlando 8:00 PM 2:00 PM Prime B"
        
        # More flexible pattern that handles various formats
        # Look for: Day. Date Team1 at/vs Team2 LocalTime ETTime [TV Info] [Special Code]
        pattern = r'^(\w{3}\.)\s+(\d{1,2}/\d{1,2}/\d{2,4})\s+(.+?)\s+(?:at|vs)\s+(.+?)\s+(\d{1,2}:\d{2}\s*(?:AM|PM))\s+(\d{1,2}:\d{2}\s*(?:AM|PM))(?:\s+(.*))?$'
        
        match = re.match(pattern, line)
        

        
        if match:
            day, date, visitor, home, local_time, et_time, extras = match.groups()
            
            # Clean up team names
            visitor = visitor.strip()
            home = home.strip()
            
            # Parse extras (TV info and special codes)
            tv_info = ''
            special_code = ''
            
            if extras:
                extras = extras.strip()
                
                # Check for special codes at the end (single letters A, B, C, D, E, R)
                if re.search(r'\s[ABCDER]$', extras):
                    special_code = extras[-1]
                    tv_info = extras[:-1].strip()
                else:
                    tv_info = extras
            
            return {
                'day': day,
                'date': date,
                'visitor': visitor,
                'home': home,
                'local_time': local_time,
                'et_time': et_time,
                'tv': tv_info,
                'special': special_code
            }
        
        # If the main pattern fails, try a more flexible approach
        # Look for day, date, teams, and times in any order
        day_pattern = r'(Mon\.|Tue\.|Wed\.|Thu\.|Fri\.|Sat\.|Sun\.)'
        date_pattern = r'(\d{1,2}/\d{1,2}/\d{2,4})'
        time_pattern = r'(\d{1,2}:\d{2}\s*(?:AM|PM))'
        
        day_match = re.search(day_pattern, line)
        date_match = re.search(date_pattern, line)
        time_matches = re.findall(time_pattern, line)
        
        if day_match and date_match and len(time_matches) >= 2:
            day = day_match.group(1)
            date = date_match.group(1)
            local_time = time_matches[0]
            et_time = time_matches[1]
            
            # Extract teams - look for "at" or "vs" between team names
            team_pattern = r'(.+?)\s+(?:at|vs)\s+(.+?)\s+' + re.escape(local_time)
            team_match = re.search(team_pattern, line)
            
            if team_match:
                visitor = team_match.group(1).strip()
                home = team_match.group(2).strip()
                
                # Extract TV info and special codes
                tv_info = ''
                special_code = ''
                
                # Look for special codes at the end
                if re.search(r'\s[ABCDER]$', line):
                    special_code = line[-1]
                    # Extract everything after the second time but before the special code
                    after_times = line.split(et_time, 1)[1].strip()
                    if after_times and after_times[-1] in 'ABCDER':
                        tv_info = after_times[:-1].strip()
                
                return {
                    'day': day,
                    'date': date,
                    'visitor': visitor,
                    'home': home,
                    'local_time': local_time,
                    'et_time': et_time,
                    'tv': tv_info,
                    'special': special_code
                }
        
        return None
    
    def identify_nba_cup_games(self):
        """Identify and mark NBA Cup games"""
        nba_cup_count = 0
        
        for game in self.games:
            # NBA Cup games are marked with 'C'
            if game['special'] == 'C':
                game['is_nba_cup'] = True
                nba_cup_count += 1
            else:
                game['is_nba_cup'] = False
        
        print(f"[OK] Identified {nba_cup_count} NBA Cup games")
        return nba_cup_count
    
    def normalize_data(self):
        """Normalize and clean up the parsed data"""
        print("Normalizing game data...")
        
        for game in self.games:
            # Normalize team names (remove extra spaces, fix common issues)
            game['visitor'] = self._normalize_team_name(game['visitor'])
            game['home'] = self._normalize_team_name(game['home'])
            
            # Normalize times
            game['local_time'] = self._normalize_time(game['local_time'])
            game['et_time'] = self._normalize_time(game['et_time'])
        
        print("[OK] Data normalization complete")
    
    def _normalize_team_name(self, team_name):
        """Normalize team name"""
        # Remove extra whitespace
        team_name = ' '.join(team_name.split())
        
        # Fix common variations
        replacements = {
            'L.A. Lakers': 'L.A. Lakers',
            'L.A. Clippers': 'LA Clippers',
            'LA Clippers': 'LA Clippers'
        }
        
        return replacements.get(team_name, team_name)
    
    def _normalize_time(self, time_str):
        """Normalize time format"""
        if not time_str:
            return ''
        
        # Ensure consistent spacing
        time_str = re.sub(r'(\d{1,2}:\d{2})\s*(AM|PM)', r'\1 \2', time_str)
        return time_str
    
    def _format_date_for_csv(self, day, date):
        """Convert date format from M/D/YY to 'Day, Mon DD, YYYY'"""
        try:
            parts = date.split('/')
            if len(parts) != 3:
                return f"{day} {date}"
            
            month, day_num, year = parts
            
            # Handle 2-digit year
            if len(year) == 2:
                year = '20' + year
            
            # Create datetime object
            dt = datetime(int(year), int(month), int(day_num))
            
            # Format as required
            formatted_date = dt.strftime("%a, %b %d, %Y")
            return formatted_date
            
        except Exception as e:
            print(f"Warning: Error formatting date {day} {date}: {e}")
            return f"{day} {date}"
    
    def _format_time_for_csv(self, time_str):
        """Convert time from '7:30 PM' to '7:30p'"""
        if not time_str:
            return ''
        
        # Remove spaces and convert to lowercase p/a format
        time_str = time_str.replace(' PM', 'p').replace(' AM', 'a')
        return time_str
    
    def _get_arena_name(self, home_team, special_code):
        """Get arena name for the home team"""
        if special_code in self.special_venues:
            return self.special_venues[special_code]
        
        # Look up arena by team name
        if home_team in self.arena_mappings:
            return self.arena_mappings[home_team]
        
        # Try partial matches
        for team, arena in self.arena_mappings.items():
            if team.lower() in home_team.lower() or home_team.lower() in team.lower():
                return arena
        
        # Fallback
        return f"{home_team} Arena"
    
    def _get_game_notes(self, game):
        """Get special notes for a game"""
        notes = []
        
        # NBA Cup games
        if game.get('is_nba_cup', False):
            notes.append('NBA Cup')
        
        # International/neutral site games
        special = game.get('special', '')
        if special == 'A':
            notes.append('Mexico City')
        elif special == 'B':
            notes.append('Berlin')
        elif special == 'D':
            notes.append('London')
        elif special == 'E':
            notes.append('Austin')
        
        # Christmas games
        if '12/25/' in game['date']:
            notes.append('Christmas Day')
        
        return ', '.join(notes)
    
    def write_to_csv(self, output_file):
        """Write the processed game data to CSV file"""
        if not self.games:
            print("ERROR: No games to write to CSV")
            return False
        
        print(f"Writing {len(self.games)} games to CSV: {output_file}")
        
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Game Date', 'Start (ET)', 'Visitor/Neutral', 'Home/Neutral', 'Arena', 'Notes']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Write header
                writer.writeheader()
                
                # Write game data
                for game in self.games:
                    writer.writerow({
                        'Game Date': self._format_date_for_csv(game['day'], game['date']),
                        'Start (ET)': self._format_time_for_csv(game['et_time']),
                        'Visitor/Neutral': game['visitor'],
                        'Home/Neutral': game['home'],
                        'Arena': self._get_arena_name(game['home'], game['special']),
                        'Notes': self._get_game_notes(game)
                    })
            
            print(f"[OK] Successfully wrote CSV file: {output_file}")
            return True
            
        except Exception as e:
            print(f"ERROR writing CSV file: {e}")
            return False
    
    def print_summary(self):
        """Print summary statistics"""
        if not self.games:
            print("No games to summarize")
            return
        
        nba_cup_games = sum(1 for game in self.games if game.get('is_nba_cup', False))
        international_games = sum(1 for game in self.games if game.get('special', '') in ['A', 'B', 'D', 'E'])
        christmas_games = sum(1 for game in self.games if '12/25/' in game['date'])
        
        # Get unique teams
        teams = set()
        for game in self.games:
            teams.add(game['visitor'])
            teams.add(game['home'])
        
        print("\\n" + "="*50)
        print("NBA SCHEDULE PROCESSING SUMMARY")
        print("="*50)
        print(f"Total games processed: {len(self.games)}")
        print(f"Unique teams found: {len(teams)}")
        print(f"NBA Cup games: {nba_cup_games}")
        print(f"International/Neutral games: {international_games}")
        print(f"Christmas Day games: {christmas_games}")
        
        if self.games:
            dates = [game['date'] for game in self.games]
            print(f"Season date range: {min(dates)} to {max(dates)}")
        
        if self.failed_lines:
            print(f"\\nWarning: {len(self.failed_lines)} lines failed to parse")
    
    def process_nba_schedule_pdf(self, pdf_path, output_csv):
        """Main method to process NBA schedule from PDF to CSV"""
        print("="*60)
        print("NBA SCHEDULE PDF PROCESSOR")
        print("="*60)
        print(f"Input PDF: {pdf_path}")
        print(f"Output CSV: {output_csv}")
        print()
        
        # Step 1: Check if PDF exists
        if not self.check_pdf_exists(pdf_path):
            return False
        
        # Step 2: Read PDF content
        pdf_content = self.read_pdf_content(pdf_path)
        if not pdf_content:
            return False
        
        # Step 3: Parse NBA game data from PDF content
        if not self.parse_pdf_content(pdf_content):
            return False
        
        # Step 4: Normalize data
        self.normalize_data()
        
        # Step 5: Identify NBA Cup games
        self.identify_nba_cup_games()
        
        # Step 6: Write to CSV
        if not self.write_to_csv(output_csv):
            return False
        
        # Step 7: Print summary
        self.print_summary()
        
        print("\\n" + "="*60)
        print("PROCESSING COMPLETE!")
        print("="*60)
        
        return True


def main():
    """Main function for command line usage"""
    if len(sys.argv) < 2:
        print("Usage: python nba_schedule_processor.py <pdf_file> [output_csv]")
        print("Example: python nba_schedule_processor.py nba_schedule.pdf nba_games.csv")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'nba_schedule_2025_26.csv'
    
    # Create processor and run
    processor = NBASchedulePDFProcessor()
    success = processor.process_nba_schedule_pdf(pdf_file, output_file)
    
    if success:
        print(f"\\nSuccess! NBA schedule exported to: {output_file}")
        sys.exit(0)
    else:
        print(f"\\nFailed to process NBA schedule from: {pdf_file}")
        sys.exit(1)


if __name__ == "__main__":
    main()
    