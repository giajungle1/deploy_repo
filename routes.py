from flask import render_template, request, redirect, url_for, flash, send_file, session
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import pickle
import pandas as pd
import numpy as np
from models import db, User, Prediction
from config import Config
from underthesea import word_tokenize
import re

def preprocess_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^a-zàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ\s]', ' ', text)
    text = re.sub(r'\d+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    tokens = word_tokenize(text)
    return ' '.join(tokens)

def init_routes(app, model):
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            
            if User.query.filter_by(username=username).first():
                flash('Username already exists')
                return redirect(url_for('register'))
            
            user = User(username=username, password_hash=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful')
            return redirect(url_for('login'))
        
        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter_by(username=username).first()
            
            if user and check_password_hash(user.password_hash, password):
                login_user(user)
                return redirect(url_for('dashboard'))
            
            flash('Invalid username or password')
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('index'))

    @app.route('/dashboard', methods=['GET', 'POST'])
    @login_required
    def dashboard():
        prediction = None
        prediction_results = None
        input_text_for_prediction = ""

        if request.method == 'POST':
            input_text_for_prediction = request.form.get('text', '')
            session['last_input_text'] = input_text_for_prediction
            
            if input_text_for_prediction:
                processed_text = preprocess_text(input_text_for_prediction)
                
                text_tfidf = model['vectorizer'].transform([processed_text])
                
                predictions = []
                probabilities = []
                
                for i, (model_clf, threshold) in enumerate(zip(model['models'], model['thresholds'])):
                    if hasattr(model_clf, 'predict_proba'):
                        probs = model_clf.predict_proba(text_tfidf)[:, 1]
                        if probs[0] >= threshold:
                            predictions.append(model['keywords'][i])
                            probabilities.append(probs[0])
                
                sorted_results = sorted(zip(predictions, probabilities), key=lambda x: x[1], reverse=True)
                
                if sorted_results:
                    prediction = sorted_results[0][0]
                else:
                    prediction = "Không tìm thấy từ khóa phù hợp"
                
                prediction_results = sorted_results

                new_prediction = Prediction(
                    text=input_text_for_prediction,
                    keyword=prediction,
                    user_id=current_user.id
                )
                db.session.add(new_prediction)
                db.session.commit()
                
        
        text_to_display = session.get('last_input_text', "")
        
        

        history = Prediction.query.filter_by(user_id=current_user.id).order_by(Prediction.timestamp.desc()).all()

        return render_template('dashboard.html', 
                                prediction=prediction,
                                text=text_to_display, 
                                prediction_results=prediction_results,
                                history=history) 

    @app.route('/download_history')
    @login_required
    def download_history():
        predictions = Prediction.query.filter_by(user_id=current_user.id).all()
        data = {
            'Text': [p.text for p in predictions],
            'Keyword': [p.keyword for p in predictions],
            'Timestamp': [p.timestamp for p in predictions]
        }
        df = pd.DataFrame(data)
        csv_path = f'history_{current_user.username}.csv'
        df.to_csv(csv_path, index=False)
        return send_file(csv_path, as_attachment=True) 