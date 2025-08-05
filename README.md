# 🌲 Redwood Birthday Bingo QR Game with Supabase 🎉

A fun, interactive bingo game web application for birthday parties where guests can join by scanning a QR code. Now with persistent data storage using Supabase!

## Features

- **QR Code Join**: Guests can scan a QR code to instantly join the game
- **Real-time Multiplayer**: Host controls the game while multiple players participate simultaneously
- **Persistent Storage**: All games and player data are stored in Supabase database
- **Birthday Theme**: Pre-loaded with 30 birthday-themed words and phrases
- **Mobile Friendly**: Responsive design that works great on phones and tablets
- **Live Updates**: Uses WebSocket for real-time game updates
- **Visual Feedback**: Beautiful, colorful interface with animations and celebrations

## How to Play

1. **Host creates a game** - Enter your name and get a unique game ID and QR code
2. **Share the QR code** - Guests scan it or visit the link to join
3. **Guests get bingo cards** - Each player receives a unique 5x5 card with birthday words
4. **Host calls words** - Click words from the dashboard to call them out
5. **Players mark squares** - Players tap matching squares on their cards
6. **First to BINGO wins!** - Complete a row, column, or diagonal to win

## Setup Instructions

### Prerequisites
- Python 3.7 or higher
- A Supabase account (free tier available)
- Internet connection

### Supabase Setup

1. **Create a Supabase project**:
   - Go to [supabase.com](https://supabase.com)
   - Sign up for a free account
   - Create a new project

2. **Set up the database**:
   - Go to your Supabase project dashboard
   - Navigate to the SQL Editor
   - Copy and paste the contents of `supabase_schema.sql` into the editor
   - Run the SQL script to create the required tables

3. **Get your credentials**:
   - Go to Settings > API in your Supabase project
   - Copy your Project URL and anon/public key

### Application Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/izuanjamal/redwood-bingo-qr-game.git
   cd redwood-bingo-qr-game
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   ```

3. **Activate the virtual environment**:
   - On Windows: `.venv\\Scripts\\activate.bat`
   - On Mac/Linux: `source .venv/bin/activate`

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment variables**:
   - Copy `.env.example` to `.env`
   - Fill in your Supabase credentials:
   ```
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_KEY=your_supabase_anon_key
   FLASK_SECRET_KEY=your_flask_secret_key_here
   ```

### Running the Game

1. **Start the server**:
   ```bash
   python app.py
   ```

2. **Open your browser** and go to:
   ```
   http://localhost:5000
   ```

3. **Create a game** and share the QR code with your guests!

## Database Schema

The application uses two main tables:

### games
- `game_id`: Unique 6-character game identifier
- `host_name`: Name of the game host
- `current_calls`: JSON array of called words
- `is_active`: Boolean flag for game status
- `winner`: Name of the winner (if any)
- `created_at`, `updated_at`: Timestamps

### players
- `player_id`: Unique UUID for each player
- `game_id`: Reference to the game
- `player_name`: Player's display name
- `card`: JSON array of bingo card words
- `marked`: JSON array of marked squares (booleans)
- `joined_at`, `updated_at`: Timestamps

## Game Words

The game includes 30 birthday-themed words:
- HAPPY BIRTHDAY, CAKE, CANDLES, PRESENTS, BALLOONS
- PARTY HAT, MUSIC, DANCING, FRIENDS, FAMILY
- LAUGHTER, PHOTOS, MEMORIES, CELEBRATION, WISHES
- CONFETTI, STREAMERS, GAMES, FUN, JOY
- SMILE, CHEERS, TOAST, SURPRISE, HUGS
- SINGING, DECORATIONS, FOOD, DRINKS, ENTERTAINMENT

## Technical Stack

- **Backend**: Flask with Socket.IO for real-time communication
- **Database**: Supabase (PostgreSQL)
- **Frontend**: HTML, CSS, JavaScript with responsive design
- **QR Codes**: Generated using the `qrcode` Python library
- **Session Management**: Flask sessions for player/host identification

## Deployment

The application can be deployed to various platforms:

### Heroku
1. Add your Supabase credentials to Heroku config vars
2. Deploy using Git or GitHub integration

### Railway
1. Connect your GitHub repository
2. Add environment variables in the Railway dashboard

### Render
1. Connect your repository
2. Set environment variables in the Render dashboard

## Customization

You can easily customize the game by:
- Modifying the `bingo_words` list in `app.py` to change the words
- Updating the styling in the HTML templates
- Adding new features like sound effects or different game modes
- Changing colors and themes in the CSS

## Troubleshooting

### Common Issues

- **Game not found**: Make sure the game ID is correct and the game is still active
- **Players can't join**: Ensure all devices can access the host computer/server
- **Database connection errors**: Check your Supabase credentials in the `.env` file
- **QR code not working**: Make sure the URL in the QR code matches your server address

### Fallback Mode

If Supabase is not configured, the application will fall back to in-memory storage. This means:
- Games will only persist while the server is running
- Restarting the server will clear all games
- Multiple server instances won't share data

## Development

### Setting up for development

1. Follow the setup instructions above
2. The application runs in debug mode by default
3. Changes to Python files will auto-reload the server

### Contributing

Feel free to fork this project and add your own features! Some ideas:
- Different themes (wedding, graduation, etc.)
- Sound effects and animations
- Multiple game modes (different win conditions)
- Score tracking and leaderboards
- Tournament brackets
- Admin panel for managing games

## License

This project is open source and available under the MIT License.

---

🤖 Generated with [Memex](https://memex.tech)
Co-Authored-By: Memex <noreply@memex.tech>