from flask.globals import request
from sqlalchemy import create_engine
from sqlalchemy import engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from project_orm import User
from auth_utils import *
import numpy as np #for algebric calculations
import pandas as pd #essential for data reading,writing etc
import seaborn as sns #visualization library
import plotly.express as px #ploting parameter's
import matplotlib #visualization library.
import matplotlib.pyplot as plt #visualization library.
import sys #for System-specific parameters and functions.
from flask import Flask,session,flash,redirect,render_template,url_for
import warnings


def get_db():
    engine = create_engine('sqlite:///database.db')
    Session = scoped_session(sessionmaker(bind=engine))
    return Session()

def load_dataset():
    df=pd.read_csv('naukri_com-job_sample.csv') 
    return df

def preprocess_dataset(df):
    # all processing code
    pay_split = df['payrate'].str[0:-1].str.split('-', expand=True)
    pay_split[1] =  pay_split[1].str.strip()
    #remove comma 
    pay_split[1] = pay_split[1].str.replace(',', '')
    #remove all character in two condition
    # 1 remove if only character
    # 2 if start in number remove after all character
    pay_split[1] = pay_split[1].str.replace(r'\D.*','')
    pay_split[0] = pd.to_numeric(pay_split[0], errors='coerce')
    pay_split[1] = pd.to_numeric(pay_split[1], errors='coerce')
    pay=pd.concat([pay_split[0], pay_split[1]], axis=1, sort=False)
    pay.rename(columns={0:'min_pay', 1:'max_pay'}, inplace=True )
    df=pd.concat([df, pay], axis=1, sort=False)
    return df


warnings.filterwarnings('ignore')
plt.rcParams['figure.figsize'] = (10, 10)
app = Flask(__name__)
app.secret_key = "the basics of life with python"
df = load_dataset()
df = preprocess_dataset(df)

@app.route('/',methods=['GET','POST'])
def index():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if email and validate_email(email):
            if password and len(password)>=6:
                try:
                    sess = get_db()
                    user = sess.query(User).filter_by(email=email,password=password).first()
                    if user:
                        session['isauth'] = True
                        session['email'] = user.email
                        session['id'] = user.id
                        session['name'] = user.name
                        del sess
                        flash('login successfull','success')
                        return redirect('/home')
                    else:
                        flash('email or password is wrong','danger')
                except Exception as e:
                    flash(e,'danger')
    return render_template('index.html',title='login')

@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        cpassword = request.form.get('cpassword')
        if name and len(name) >= 3:
            if email and validate_email(email):
                if password and len(password)>=6:
                    if cpassword and cpassword == password:
                        try:
                            sess = get_db()
                            newuser = User(name=name,email=email,password=password)
                            sess.add(newuser)
                            sess.commit()
                            del sess
                            flash('registration successful','success')
                            return redirect('/')
                        except:
                            flash('email account already exists','danger')
                    else:
                        flash('confirm password does not match','danger')
                else:
                    flash('password must be of 6 or more characters','danger')
            else:
                flash('invalid email','danger')
        else:
            flash('invalid name, must be 3 or more characters','danger')
    return render_template('signup.html',title='register')

@app.route('/forgot',methods=['GET','POST'])
def forgot():
    return render_template('forgot.html',title='forgot password')

@app.route('/home',methods=['GET','POST'])
def home():
    if session.get('isauth'):
        username = session.get('name')
        return render_template('home.html',title=f'Home|{username}')
    flash('please login to continue','warning')
    return redirect('/')

@app.route('/about')
def about():
    return render_template('about.html',title='About Us')

@app.route('/logout')
def logout():
    if session.get('isauth'):
        session.clear()
        flash('you have been logged out','warning')
    return redirect('/')

@app.route('/analysis/1')
def analysis1():
    count_missing = df.isnull().sum()
    percent_missing =  count_missing* 100 / df.shape[0]
    missing_value_df = pd.DataFrame({'count_missing': count_missing,
                                 'percent_missing': percent_missing})

    missing_value_df.style.background_gradient(cmap='Spectral')

    unique_df = unique_df = pd.DataFrame([[df[i].nunique()]for i in df.columns], columns=['Unique Values'], index=df.columns)
    unique_df.style.background_gradient(cmap='magma')
    nrow,ncol=df.shape
    info1 = f'There are {nrow} rows and {ncol} colunms in the dataset'
    return render_template('analysis1.html',title='Analysis for values',
                           data=missing_value_df.to_html(),
                           unique_data = unique_df.to_html(), 
                           info1 = info1,
                           columns = df.columns.to_list())

if __name__ == "__main__":
    app.run(debug=True,threaded=True, host='0.0.0.0')


