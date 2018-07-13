from flask import *
from functools import wraps
from passlib.hash import sha256_crypt
from models.classes import *
from PIL import Image
from io import BytesIO
import base64
import os
import mlab

mlab.connect()
app = Flask(__name__)
app.secret_key = "secret_key"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sign_up', methods = ['GET', 'POST'])
def sign_up():
    if request.method == 'GET':
        return render_template('sign_up.html')
    elif request.method == 'POST':
        form = request.form
        username = form['username']
        email = form['email']
        password = sha256_crypt.encrypt(form['password'])

        try:
            new_user = User(email = email, username = username, password = password)
            new_user.save()
            flash("Thanks for registering!")
        except:
            if list(User.objects(email = email)) != []:
                flash("That email is already taken, please choose another")
                return render_template('sign_up.html')
            elif list(User.objects(username = username)) != []:
                flash("That username is already taken, please choose another")
                return render_template('sign_up.html')

        session['logged_in'] = True
        session['username'] = username
        return redirect(url_for('user',username = username))

@app.route('/log_in',methods = ['GET', 'POST'])
def log_in():
    if request.method == 'GET':
        return render_template('log_in.html')
    elif request.method == 'POST':
        form = request.form
        username = form['username']

        user = User.objects(username__exact = username).first()
        if user is not None:
            if sha256_crypt.verify(form['password'],user.password):
                session['logged_in'] = True
                session['username'] = request.form['username']

                flash("You are now logged in")
                return redirect(url_for('user',username = username))
            else:
                flash("Invalid password")
                return render_template('log_in.html')
        else:
            flash("Invalid username")
            return render_template('log_in.html')


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('log_in'))
    return decorated_function


@app.route('/user/<username>')
@login_required
def user(username):
    topics = Topic.objects(author__exact = session['username'])
    votes = Vote.objects(user_exact=session['username'])
    return render_template ('user.html', topics = topics, votes = votes)



def convert_image_to_string(img,image_size_MB):

    output = BytesIO()

    if image_size_MB < 1:
        img.save(output,format='JPEG')
    if image_size_MB < 5:
        img.save(output,format='JPEG',quality = 50)
    else:
        img.save(output,format ='JPEG', quality = 25)

    image_data = output.getvalue()

    image_bytes = base64.b64encode(image_data)
    image_string = image_bytes.decode()

    return image_string



@app.route('/new_topic', methods = ['GET', 'POST'])
@login_required
def new_topic():
    if request.method == 'GET':
        return render_template('new_topic.html')
    elif request.method =='POST':
        form = request.form
        question = form['question']
        group = form['group']
        try:
            image = request.files['image']
            image_size_MB = len(image.read())/1048576
            # print(image_size_MB)
            image_name = image.filename
            img = Image.open(image)

            if "png" in image_name:
                img = img.convert('RGB')

            image_string = convert_image_to_string(img,image_size_MB)
        except:
            image_size_MB = os.path.getsize("static\yes-and-no-signs_1325-370.jpg")/104857
            # print(image_size_MB)
            img = Image.open("static\yes-and-no-signs_1325-370.jpg")
            image_string = convert_image_to_string(img,image_size_MB)


        new_topic = Topic(question = question, group = group, image = image_string, author = session['username'])
        new_topic.save()
        flash("New topic created!!!")
        return redirect(url_for('user',username =session['username']))


@app.route('/topic/<topic_id>', methods =['GET','POST'])
def topic(topic_id):
    if request.method =='GET':
        topic = Topic.objects(id__exact= topic_id).first()
        votes= Vote.objects(topic = topic_id)
        return render_template ('topic.html',topic = topic, votes = votes)
    elif request.method =='POST':
        form = request.form
        choice = form['choice']
        topic = Topic.objects(id__exact=topic_id).first()
        topic.update(add_to_set__users_voted =session['username'])
        if choice =='yes':
            vote_yes = True
            count_yes = topic.votes_yes +1
            topic.update(votes_yes= count_yes)
        else:
            vote_yes = False
            count_no = topic.votes_no +1
            topic.update(votes_no= count_no)

        answer = form['answer']

        new_vote = Vote(topic = topic_id, answer = answer, user = session['username'],vote_yes = vote_yes)
        new_vote.save()
        flash("Voted")
        return redirect(url_for('user',username =session['username']))


@app.route('/log_out')
@login_required
def log_out():
    session.clear()
    return redirect(url_for('index'))



if __name__ == '__main__':
  app.run(debug=True)