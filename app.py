from flask import Flask, session, jsonify, request
from flask_session import Session
from flask_cors import CORS
from videodb import *
from userdb import *
import jwt
import datetime
from models import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['SECRET_KEY'] = "your-secret-key-here"  # Change this to a secure secret
db.init_app(app)

# Initialize Flask-Session
Session(app)

# Allow only frontend origin with credentials support
CORS(app, origins=["http://localhost:5173"], supports_credentials=True)

# Create database tables
with app.app_context():
    db.create_all()

@app.route('/api/hello')
def hello():
    return {'message': 'Hello from Flask!'}

@app.route('/')
def home():
    return "Hello, BrainGrow AI!"

@app.route('/api/search')
def search():
    try:
        searchQuery = request.args.get('query')
        if not searchQuery:
            return jsonify({'error': 'Query parameter is required'}), 400
            
        videos = searchVideo(searchQuery)
        return jsonify([{
            'id': v.id,
            'title': v.title,
            'description': v.description,
            'url': v.url,
            'tags': v.tags,
            'imageUrl': v.imageUrl
        } for v in videos])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/video/<video_id>')
def get_video(video_id):
    try:
        # Assuming you have a getVideoById function in videodb
        video = getVideoById(video_id)
        if video:
            return jsonify({
                '_id': video.id,
                'title': video.title,
                'description': video.description,
                'author': video.author if hasattr(video, 'author') else 'Unknown',
                'date': video.date.isoformat() if hasattr(video, 'date') else None,
                'category': video.category if hasattr(video, 'category') else 'General',
                'views': video.views if hasattr(video, 'views') else 0,
                'likes': video.likes if hasattr(video, 'likes') else 0,
                'dislikes': video.dislikes if hasattr(video, 'dislikes') else 0,
                'url': video.url,
                'coverUrl': video.imageUrl
            })
        return jsonify({'error': 'Video not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])  # Changed to /api/login
def login():
    # Handle both Basic Auth and JSON body
    auth = request.authorization
    if not auth and request.json:
        # Handle JSON login
        username = request.json.get('username')
        password = request.json.get('password')
    elif auth:
        username = auth.username
        password = auth.password
    else:
        return jsonify({'error': 'Username and password required'}), 401
        
    try:
        user = userLogin(username, password)
        if user:
            token = jwt.encode({
                'user_id': user.id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, app.config['SECRET_KEY'], algorithm="HS256")
            
            return jsonify({
                'token': token,
                'user_id': user.id,
                'username': user.username
            })
        return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
            
        # Assuming you have a userRegister function
        user = userRegister(username, password, email)
        if user:
            return jsonify({
                'message': 'User created successfully',
                'user_id': user.id,
                'username': user.username
            }), 201
        return jsonify({'error': 'User creation failed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/profile')
def profile():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Authorization header missing'}), 401
    
    # Handle Bearer token format
    if token.startswith('Bearer '):
        token = token[7:]
    
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        user = userProfile(data['user_id'])
        if user:
            return jsonify({
                'user_id': user.id,
                'username': user.username,
                'tendency': user.tendency,
                'photoUrl': user.photoUrl
            })
        return jsonify({'error': 'User not found'}), 404
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=8080, debug=True)