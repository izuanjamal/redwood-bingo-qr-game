from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
from supabase import create_client, Client
import qrcode
import io
import base64
import random
import string
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'redwood_bingo_secret_key_2024')
socketio = SocketIO(app, cors_allowed_origins="*")

# Supabase configuration
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')

if not supabase_url or not supabase_key:
    print("Warning: Supabase credentials not found. Check your .env file.")
    supabase = None
else:
    supabase: Client = create_client(supabase_url, supabase_key)

# In-memory fallback for when Supabase is not configured
games_memory = {}
players_memory = {}

class BingoGame:
    def __init__(self, game_id, host_name, from_db=False):
        self.game_id = game_id
        self.host_name = host_name
        self.players = {}
        self.current_calls = []
        self.is_active = False
        self.winner = None
        self.created_at = datetime.now()
        
        # Traditional bingo words/phrases for birthday party
        self.bingo_words = [
            "HAPPY BIRTHDAY", "CAKE", "CANDLES", "PRESENTS", "BALLOONS",
            "PARTY HAT", "MUSIC", "DANCING", "FRIENDS", "FAMILY",
            "LAUGHTER", "PHOTOS", "MEMORIES", "CELEBRATION", "WISHES",
            "CONFETTI", "STREAMERS", "GAMES", "FUN", "JOY",
            "SMILE", "CHEERS", "TOAST", "SURPRISE", "HUGS",
            "SINGING", "DECORATIONS", "FOOD", "DRINKS", "ENTERTAINMENT"
        ]
        
        if not from_db:
            self.save_to_db()
    
    def save_to_db(self):
        """Save game to Supabase database"""
        if not supabase:
            return
        
        try:
            game_data = {
                'game_id': self.game_id,
                'host_name': self.host_name,
                'current_calls': json.dumps(self.current_calls),
                'is_active': self.is_active,
                'winner': self.winner,
                'created_at': self.created_at.isoformat()
            }
            
            # Insert or update game
            supabase.table('games').upsert(game_data).execute()
            
        except Exception as e:
            print(f"Error saving game to database: {e}")
    
    def add_player(self, player_id, player_name):
        if player_id not in self.players:
            # Generate random bingo card
            card_words = random.sample(self.bingo_words, 25)
            player_data = {
                'name': player_name,
                'card': card_words,
                'marked': [False] * 25,
                'joined_at': datetime.now()
            }
            
            self.players[player_id] = player_data
            
            # Save player to database
            if supabase:
                try:
                    player_db_data = {
                        'player_id': player_id,
                        'game_id': self.game_id,
                        'player_name': player_name,
                        'card': json.dumps(card_words),
                        'marked': json.dumps([False] * 25),
                        'joined_at': player_data['joined_at'].isoformat()
                    }
                    supabase.table('players').upsert(player_db_data).execute()
                except Exception as e:
                    print(f"Error saving player to database: {e}")
            
            return True
        return False
    
    def mark_square(self, player_id, square_index):
        if player_id in self.players and 0 <= square_index < 25:
            word = self.players[player_id]['card'][square_index]
            if word in self.current_calls:
                self.players[player_id]['marked'][square_index] = True
                
                # Update player in database
                if supabase:
                    try:
                        supabase.table('players').update({
                            'marked': json.dumps(self.players[player_id]['marked'])
                        }).eq('player_id', player_id).execute()
                    except Exception as e:
                        print(f"Error updating player in database: {e}")
                
                return True
        return False
    
    def check_winner(self, player_id):
        if player_id not in self.players:
            return False
        
        marked = self.players[player_id]['marked']
        
        # Center square is always free
        marked[12] = True
        
        # Check rows
        for i in range(5):
            if all(marked[i*5 + j] for j in range(5)):
                return True
        
        # Check columns
        for j in range(5):
            if all(marked[i*5 + j] for i in range(5)):
                return True
        
        # Check diagonals
        if all(marked[i*5 + i] for i in range(5)):
            return True
        if all(marked[i*5 + (4-i)] for i in range(5)):
            return True
        
        return False
    
    def call_word(self, word):
        if word in self.bingo_words and word not in self.current_calls:
            self.current_calls.append(word)
            self.save_to_db()  # Save updated calls to database
            return True
        return False

def generate_game_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def generate_qr_code(game_id):
    # Generate QR code for joining the game
    # Use environment variable for production URL, fallback to localhost for development
    base_url = os.getenv('BASE_URL', 'http://localhost:5000')
    join_url = f"{base_url}/join/{game_id}"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(join_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64 for embedding in HTML
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return img_str

def get_game_from_db(game_id):
    """Load game from Supabase database"""
    if not supabase:
        return games_memory.get(game_id)
    
    try:
        # Get game data
        game_response = supabase.table('games').select('*').eq('game_id', game_id).execute()
        if not game_response.data:
            return None
        
        game_data = game_response.data[0]
        
        # Create game object
        game = BingoGame(game_id, game_data['host_name'], from_db=True)
        game.current_calls = json.loads(game_data['current_calls'] or '[]')
        game.is_active = game_data['is_active']
        game.winner = game_data['winner']
        game.created_at = datetime.fromisoformat(game_data['created_at'])
        
        # Get players data
        players_response = supabase.table('players').select('*').eq('game_id', game_id).execute()
        for player_data in players_response.data:
            game.players[player_data['player_id']] = {
                'name': player_data['player_name'],
                'card': json.loads(player_data['card']),
                'marked': json.loads(player_data['marked']),
                'joined_at': datetime.fromisoformat(player_data['joined_at'])
            }
        
        return game
        
    except Exception as e:
        print(f"Error loading game from database: {e}")
        return games_memory.get(game_id)

def save_game_to_memory(game):
    """Fallback to save game in memory"""
    games_memory[game.game_id] = game

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_game', methods=['POST'])
def create_game():
    host_name = request.form.get('host_name', 'Anonymous Host')
    game_id = generate_game_id()
    
    # Create new game
    game = BingoGame(game_id, host_name)
    
    # Save to memory as fallback
    save_game_to_memory(game)
    
    # Generate QR code
    qr_code = generate_qr_code(game_id)
    
    session['game_id'] = game_id
    session['is_host'] = True
    
    return render_template('host_dashboard.html', 
                         game_id=game_id, 
                         qr_code=qr_code,
                         host_name=host_name)

@app.route('/join/<game_id>')
def join_game(game_id):
    game = get_game_from_db(game_id)
    if not game:
        return render_template('error.html', message='Game not found!')
    
    return render_template('join_game.html', game_id=game_id)

@app.route('/join_game', methods=['POST'])
def join_game_post():
    game_id = request.form.get('game_id')
    player_name = request.form.get('player_name', 'Anonymous Player')
    
    game = get_game_from_db(game_id)
    if not game:
        return render_template('error.html', message='Game not found!')
    
    player_id = str(uuid.uuid4())
    
    if game.add_player(player_id, player_name):
        session['game_id'] = game_id
        session['player_id'] = player_id
        session['player_name'] = player_name
        
        # Update memory storage
        save_game_to_memory(game)
        
        return redirect(url_for('play_game'))
    else:
        return render_template('error.html', message='Could not join game!')

@app.route('/play')
def play_game():
    game_id = session.get('game_id')
    player_id = session.get('player_id')
    
    if not game_id or not player_id:
        return redirect(url_for('index'))
    
    game = get_game_from_db(game_id)
    if not game:
        return redirect(url_for('index'))
    
    player_data = game.players.get(player_id)
    if not player_data:
        return redirect(url_for('index'))
    
    return render_template('play_game.html', 
                         game_id=game_id,
                         player_data=player_data,
                         current_calls=game.current_calls)

@app.route('/setup')
def setup_database():
    """Setup Supabase database tables"""
    if not supabase:
        return "Supabase not configured. Please check your .env file."
    
    try:
        # Create games table
        supabase.table('games').select('*').limit(1).execute()
        # Create players table  
        supabase.table('players').select('*').limit(1).execute()
        return "Database tables are ready!"
    except Exception as e:
        return f"Database setup error: {e}. Please create the tables manually in Supabase."

# Socket.IO events
@socketio.on('connect')
def on_connect():
    game_id = session.get('game_id')
    if game_id:
        game = get_game_from_db(game_id)
        if game:
            join_room(game_id)
            if session.get('is_host'):
                emit('player_count', {'count': len(game.players)}, room=game_id)

@socketio.on('call_word')
def handle_call_word(data):
    game_id = session.get('game_id')
    if not session.get('is_host') or not game_id:
        return
    
    game = get_game_from_db(game_id)
    if not game:
        return
    
    word = data.get('word')
    
    if game.call_word(word):
        # Update memory storage
        save_game_to_memory(game)
        
        emit('word_called', {'word': word}, room=game_id)
        emit('update_calls', {'calls': game.current_calls}, room=game_id)

@socketio.on('mark_square')
def handle_mark_square(data):
    game_id = session.get('game_id')
    player_id = session.get('player_id')
    
    if not game_id or not player_id:
        return
    
    game = get_game_from_db(game_id)
    if not game:
        return
    
    square_index = data.get('square_index')
    
    if game.mark_square(player_id, square_index):
        # Update memory storage
        save_game_to_memory(game)
        
        if game.check_winner(player_id):
            player_name = game.players[player_id]['name']
            game.winner = player_name
            game.save_to_db()
            save_game_to_memory(game)
            emit('game_winner', {'winner': player_name}, room=game_id)
        else:
            emit('square_marked', {'square_index': square_index}, room=request.sid)

@socketio.on('disconnect')
def on_disconnect():
    game_id = session.get('game_id')
    if game_id:
        leave_room(game_id)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    host = '0.0.0.0' if not debug else 'localhost'
    
    socketio.run(app, debug=debug, host=host, port=port, allow_unsafe_werkzeug=True)