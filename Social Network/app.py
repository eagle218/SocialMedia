from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource, reqparse 
from flask import request
from flask import redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

from flask_session import Session
from flask import session, url_for
from flask_cors import CORS 
from flask import jsonify
from sqlalchemy import func

from sqlalchemy import DateTime
from datetime import datetime
from flask import request, jsonify
import secrets
import traceback

app = Flask(__name__)
api = Api(app)
CORS(app) 

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  
db = SQLAlchemy(app)
jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = 'your_secret_key_here'


app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


""" TEMPLATES  """

@app.route("/api/")
def index():
    if not session.get('user_id'):
        return render_template('login.html')
    return render_template('index.html', user_id=session.get('user_id'))

@app.route('/api/register')
def register():
    return render_template('register.html')

@app.route('/api/login')
def login():
    return render_template('login.html')

@app.route("/logout")
def logout():
    """Log user out."""

    session.clear()

    return redirect("/api/login")



@app.route('/api/post/create')
def post_creation():
    if not session.get('user_id'):
        return render_template('login.html')
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if user:
        api_key = user.api_key
        return render_template('createPost.html', api_key=api_key, user_id=user_id)
    else:
        print(f"User with ID {user_id} not found.")

@app.route('/api/post/myPosts')
def post_detail():
    user_id = session.get('user_id')
    if not user_id:
        return render_template('login.html')
    
    user = User.query.get(user_id)
    if not user:
        print("User not found")
        return render_template('login.html')
    
    user_posts = Post.query.filter_by(user_id=user.id).all()

    return render_template('myPostsDetail.html', user=user, user_posts=user_posts, user_id = user_id)

@app.route('/api/post/allPosts')
def all_posts():
    if not session.get('user_id'):
        print("not")
        return render_template('login.html')

    # Retrieve all posts from all users
    all_posts = Post.query.all()

    # Pass post IDs to the template
    post_ids = [post.id for post in all_posts]

    # Organize posts by user
    user_posts = {}
    for post in all_posts:
        if post.user not in user_posts:
            user_posts[post.user] = []
        user_posts[post.user].append(post.content)  # Assuming post content is in the 'content' attribute
    

    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if user:
        api_key = user.api_key
        return render_template('allPosts.html', user_posts=user_posts, api_key=api_key, post_ids=post_ids, user_id=user_id)
    else:
        print(f"User with ID {user_id} not found.")
    

@app.route('/api/token')
def get_token():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    return render_template('get_token.html', username=user.username, user_id=user_id)

"""  MODELS """

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    last_login = db.Column(db.DateTime)
    last_request = db.Column(db.DateTime)
    api_key = db.Column(db.String(128), unique=True, nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.password_hash}')"
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='posts', lazy=True)

    # Keep the likes relationship in the Post model
    likes = db.relationship('Like', backref='post', lazy=True)

    def __repr__(self):
        return f"Post('{self.content}', '{self.user.username}')"

        
class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    timestamp = db.Column(DateTime(timezone=True), server_default=func.now())
    user = db.relationship('User', backref='likes', lazy=True)

    def __repr__(self):
        return f"Like('{self.user.username}', '{self.post.content}')"

""" RESOURCES """

class UserRegistration(Resource):
    def post(self):
        try:
            data = request.get_json(force=True)  
            # Checking if a user with the same name exists
        
            existing_user = User.query.filter_by(username=data.get('username')).first()

            if existing_user:
                return {'message': 'Username is already taken'}, 400

            hashed_password = generate_password_hash(data.get('password'))

            new_user = User(username=data.get('username'), password_hash=hashed_password)
            new_user.api_key = secrets.token_hex(16)
            db.session.add(new_user)
            db.session.commit()

            session['user_id'] = new_user.id

            response_data = {'message': 'User registration successful', 'user_id': new_user.id, 'api_key': new_user.api_key, 'redirect_url': url_for('index')}
            return response_data, 201
        
        except Exception as e:
            return jsonify({'message': f'Error parsing JSON: {str(e)}'}), 400
        
class UserLogin(Resource):
    def post(self):
        data = request.get_json(force=True)
        username = data.get('username')
        password = data.get('password')
        existing_user = User.query.filter_by(username=username).first()

       
        if existing_user and existing_user.check_password(password):
            existing_user.last_login = datetime.utcnow()
            existing_user.last_request = datetime.utcnow()
            db.session.commit()

            session['user_id'] = existing_user.id
            response_data = {
                'message': 'User login successful', 
                'user_id': existing_user.id, 
                'redirect_url': url_for('index')
                }
            print(response_data)
            return response_data, 201  # Changed status code to 200 for success
        else:
            print("This")
            return {'message': 'Invalid username or password'}, 401


        
class CreatePostResource(Resource):
    def post(self):
        try:
            data = request.get_json()
            user_api_key = data['api_key']
            user = User.query.filter_by(api_key=user_api_key).first()

            if user:
                content = data['content']
                new_post = Post(content=content, user_id=user.id)
                db.session.add(new_post)
                db.session.commit()
                return {'message': 'Post created successfully', 'post_id': new_post.id}, 200
            else:
                return {'message': 'User not found'}, 400
        except KeyError:
            return {'message': 'Missing api_key in the request data'}, 400




class LikeResource(Resource):
    def post(self, post_id):
        try:
            data = request.get_json()

            user_api_key = data.get('api_key')

            user = User.query.filter_by(api_key=user_api_key).first()

            if user is None:
                return jsonify({'message': 'User not found'}), 400
            
            # Check if the user has already liked the post
            if Like.query.filter_by(user_id=user.id, post_id=post_id).first():
                return jsonify({'message': 'You have already liked this post'})

            # Create a new like
            new_like = Like(user_id=user.id, post_id=post_id)
            db.session.add(new_like)
            db.session.commit()

            return {'message': 'Post liked successfully'}, 202

        except Exception as e:
            return jsonify({'message': f'Error: {str(e)}'}), 500

class UnlikeResource(Resource):
    def delete(self, post_id):
        try:
            data = request.get_json()
            user_api_key = data.get('api_key')
            user = User.query.filter_by(api_key=user_api_key).first()

            if user is None:
                return jsonify({'message': 'User not found'}), 400
            
            like_entry = Like.query.filter_by(user_id=user.id, post_id=post_id).first()

            if like_entry:
                db.session.delete(like_entry)
                db.session.commit()
                return {'message': 'Post unliked successfully'}, 200
            else:
                return {'message': 'You have not liked this post'}, 404
        except Exception as e:
            return jsonify({'message': f'Error: {str(e)}'}), 500
        
class AnalyticsResource(Resource):
    def get(self):
        try:
            # Parse request data
            parser = reqparse.RequestParser()
            parser.add_argument('date_from', type=str, required=True, help='Date from is required (YYYY-MM-DD)')
            parser.add_argument('date_to', type=str, required=True, help='Date to is required (YYYY-MM-DD)')
            args = parser.parse_args()
            
            # Query analytics data
            analytics_data = (
                db.session.query(func.date(Like.timestamp).label('date'), func.count().label('like_count'))
                .filter(Like.timestamp.between(args['date_from'], args['date_to']))
                .group_by(func.date(Like.timestamp))
                .all()
            )
            # Convert the results to a dictionary
            analytics_dict = {str(date): like_count for date, like_count in analytics_data}

            return jsonify(analytics_dict)

        except Exception as e:
            # Handle exceptions (print or log the error, and return an appropriate response)
            print(f"An error occurred: {e}")
            return {'error': 'An error occurred'}, 500




class UserActivity(Resource):
    def get(self):
        username = request.args.get('username')

        if username:
            user = User.query.filter_by(username=username).first()

            if user:
                last_login = user.last_login.strftime("%Y-%m-%d %H:%M:%S") if user.last_login else None
                last_request = user.last_request.strftime("%Y-%m-%d %H:%M:%S") if user.last_request else None

                response_data = {
                    'last_login': last_login,
                    'last_request': last_request
                }

                return response_data
            else:
                return {'message': 'User not found'}, 404
        else:
            return {'message': 'Username parameter missing'}, 400

        
class TokenResource(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        return {'access_token': access_token}, 200
    
class GetTokenResource(Resource):
    def get(self):
        try:
            # Retrieving parameters from the URL
            username = request.args.get('username')
            if not username:
                return {'message': 'Missing username in the request parameters'}, 400

            user = User.query.filter_by(username=username).first()

            if user:
                api_key = user.api_key
                return {'api_key': api_key}, 200
            else:
                return {'message': f'User with username: {username} not found'}, 404
        except Exception as e:
            return {'message': f'Error: {str(e)}'}, 500

api.add_resource(UserRegistration, '/api/register')
api.add_resource(UserLogin, '/api/login')
api.add_resource(TokenResource, '/api/token')

api.add_resource(CreatePostResource, '/api/post/create')
api.add_resource(LikeResource, '/api/post/<int:post_id>/like')
api.add_resource(UnlikeResource, '/api/post/<int:post_id>/unlike')
api.add_resource(AnalyticsResource, '/api/analytics')
api.add_resource(UserActivity, '/user_activity')
api.add_resource(GetTokenResource, '/api/get_token')



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
        
