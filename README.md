# Chess Analysis Tool

A Django web application for analyzing chess games from Chess.com using the Stockfish engine.

## Features

- Fetch last 100 games from any public Chess.com account
- Interactive web interface with Bootstrap styling
- Stockfish engine integration for position evaluation
- Game list view with detailed information
- API endpoints for programmatic access

## Local Setup

### 1. Clone the repository
```bash
git clone https://github.com/chiedu18/chess-analysis.git
cd chess-analysis
```

### 2. Create and activate virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up Stockfish
```bash
# Set environment variable for Stockfish path
# Windows (PowerShell)
$env:STOCKFISH_PATH="C:\path\to\stockfish.exe"

# macOS/Linux
export STOCKFISH_PATH="/path/to/stockfish"
```

### 5. Run database migrations
```bash
python manage.py migrate
```

### 6. Start the development server
```bash
python manage.py runserver
```

### 7. Visit the application
Open your browser and go to: http://127.0.0.1:8000/

## Usage

1. **Home Page**: Enter a Chess.com username to fetch games
2. **Test API**: Click "Test API" to verify Chess.com API connectivity
3. **Games List**: View fetched games in a table format
4. **Stockfish Test**: Run `python manage.py evalstart --depth 10` to test engine

## API Endpoints

- `GET /` - Home page with game fetching form
- `POST /api/fetch-games/` - Fetch games from Chess.com
- `GET /api/test/` - Test Chess.com API connectivity
- `GET /games/` - Display games list

## Management Commands

```bash
# Test Stockfish engine evaluation
python manage.py evalstart --depth 10

# Create superuser (optional)
python manage.py createsuperuser
```

## Dependencies

- Django 5.2+
- python-chess - Chess logic and board manipulation
- requests - HTTP client for Chess.com API
- stockfish-binaries - Stockfish chess engine

## Development

The project uses:
- **Bootstrap 5** for responsive UI
- **Chessboard.js** for interactive chess boards
- **Chess.js** for chess rules engine
- **SQLite** for development database

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the MIT License. 