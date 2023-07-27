from flask import Flask, render_template, request, redirect, url_for, flash
from flask import session as login_session

import pyrebase

config = {
  "apiKey": "AIzaSyDM-FNG5Rfj588aIDKhv-5sp2Pg5bVN23M",
  "authDomain": "kill-me-825b6.firebaseapp.com",
  "databaseURL": "https://kill-me-825b6-default-rtdb.europe-west1.firebasedatabase.app",
  "projectId": "kill-me-825b6",
  "storageBucket": "kill-me-825b6.appspot.com",
  "messagingSenderId": "754943630718",
  "appId": "1:754943630718:web:adc769fa16d96d6fa0272f",
  "databaseURL":"https://kill-me-825b6-default-rtdb.europe-west1.firebasedatabase.app/"
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'super-secret-key'


@app.route('/', methods=['GET', 'POST'])
def index():

    return render_template('index.html')


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user' in login_session and login_session['user'] is not None:
        uid = login_session['user']['localId']
        user = db.child('Users').child(uid).get().val()
        goals = db.child('Users').child(uid).child('goals').get().val()
        money = db.child('Users').child(uid).get().val()['userMoney']
        expense = db.child('Users').child(uid).child('expense').get().val()
        cost = db.child('Users').child(uid).child('expense').get().val()
        print(uid, user, goals, money, expense, cost)
        return render_template('profile.html', money=money, user = user, goals = goals)
    else:
        return redirect(url_for('signin'))


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    error = ""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            login_session['user'] = auth.sign_in_with_email_and_password(email, password)
            return redirect(url_for('profile'))
        except Exception as e:
            error = "Authentication failed"
            print(e)
    return render_template("signin.html")


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = ""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        username = request.form['username']
        userMoney = request.form['money_in_acount']
        try:
            login_session['user'] = auth.create_user_with_email_and_password(email, password)
            UID = login_session['user']['localId']
            user = {'email' : email, 'username' : username, 'userMoney' : userMoney, 'goals' : {'drugs' : 10000}, 'expense' : {}}
            db.child('Users').child(UID).set(user)
            return redirect(url_for('profile'))
        except Exception as e:
            error = "Authentication failed"
            print(e)

    return render_template("signup.html")


@app.route('/income', methods=['GET', 'POST'])
def income():
    error = ""
    if request.method == 'POST':
        income = int(request.form['income'])
        try:
            login_session['user'] = auth.get_account_info(email, password)
            UID = login_session['user']['localId']
            uMoney = db.child('Users').child(UID).child('userMoney').get().val()
            newmoney = uMoney + income 
            db.child('Users').child(UID).child('userMoney').set(newmoney)
        except Exception as e:
            error = "Authentication failed"
            print(e)

    return render_template('income_upsate.html')

@app.route('/expenses', methods=['GET', 'POST'])
def expenses():
    error = ""
    if request.method == 'POST':
        line_item = request.form['expense']
        cost = float(request.form['money'])
        try:
            login_session['user'] = auth.get_account_info(email, password)
            UID = login_session['user']['localId']
            expense = db.child('Users').child(UID).child('expense').get().val()
            expense[line_item] = cost
            db.child('Users').child(UID).child('expense').update(expense)
            usMoney = db.child('Users').child(UID).child('userMoney').get().val()
            nmoney = usMoney - cost 
            db.child('Users').child(UID).child('userMoney').update(nmoney)
        except Exception as e:
            error = "Authentication failed"
            print(e)
    return render_template('expense_update.html')

@app.route('/goals', methods=['GET', 'POST'])
def goals():
    error = ""
    if request.method == 'POST':
        goal_title = request.form['goal']
        money = float(request.form['money'])
        try:
            if 'user' in login_session and login_session['user'] is not None:
                UID = login_session['user']['localId']
                goals_data = db.child('Users').child(UID).child('goals').get().val()
                goals_data[goal_title] = money
                db.child('Users').child(UID).child('goals').set(goals_data)
            else:
                error = "User not authenticated"
        except Exception as e:
            error = "Authentication failed"
            print(e)
    return render_template('add_goals.html', error=error)


@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    error = ""
    if login_session['user'] != None:
        user = db.child('Users').child(login_session['user']['localId']).get().val()
        print(user)
        if request.method == 'POST':
            newUsername = request.form['newUsername']
            # newEmail = request.form('newEmail')
            # newPassword = request.form('newPassword')
            # oldPassword = request.form('oldPassword')
            try:
                # login_session['user'] = auth.create_user_with_email_and_password(email, password)
                UID = login_session['user']['localId']
                updated = {'username' : newUsername}
                db.child('Users').child(UID).update(updated)
                # db.child('Users').child(UID).child('email').update(newEmail)
                # if oPassword == oldPassword:
                #     db.child('Users').child(UID).child('password').update(newPassword)
                # else:
                #     error = "old password is incorrect"
                #     print(e)
                return redirect(url_for('profile'))
            except Exception as e:
                error = "Authentication failed"
                print(e)
    else:
        return redirect(url_for('signin'))
    return render_template('edit_profile.html')



@app.route('/signout')
def signout():
    login_session['user'] = None
    auth.current_user = None
    return redirect(url_for('signin'))



if __name__ == '__main__':
    app.run(debug=True)