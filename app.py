from flask import Flask, render_template, json, request,redirect,session
from flask.ext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash
from flask import session

app = Flask(__name__)

mysql = MySQL()
 
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'abcd'
app.config['MYSQL_DATABASE_DB'] = 'StudentPortal'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)



app.secret_key = 'MART'

@app.route("/")
def main():
    return render_template('index.html')

@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')

@app.route('/showLogin')
def showLogin():
    return render_template('login.html')

@app.route('/validateLogin',methods=['POST'])
def validateLogin():
    try:
        _username = request.form['inputUsername']
        _password = request.form['inputPassword'] 
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_validateLogin',(_username,))
        data = cursor.fetchall()
        print data
        if len(data) > 0:
            if check_password_hash(str(data[0][4]),_password):
                session['user'] = data[0][0]
                # print session['user']
                return redirect('/userHome')
                #return render_template('userHome.html')
            else:
                return render_template('error.html',error = 'Wrong Email address or Password.')
        else:
            return render_template('error.html',error = 'Wrong Email address or Password.')
    except Exception as e:
        print "Unknown error 53"
        return render_template('error.html',error = str(e))
    finally:
        cursor.close()
        conn.close()

@app.route('/userHome')
def userHome():
    print "line 60"
    print session.get('user')
    if session.get('user'):
        return render_template('userHome.html')
    else:
        return render_template('error.html',error = 'Unauthorized Access')

@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')

@app.route('/signUp',methods=['POST'])
def signUp():
    try:
        _rollno = request.form['inputRollno']
        _username = request.form['inputUsername']
        _password = request.form['inputPassword']

        # validate the received values
        if _rollno and _username and _password:
            
            # All Good, let's call MySQL
            
            conn = mysql.connect()
            cursor = conn.cursor()
            _hashed_password = generate_password_hash(_password)
            cursor.callproc('sp_createUser3',(_rollno,_username, _hashed_password, "student"))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                return json.dumps({'message':'User created successfully !'})
            else:
                return json.dumps({'error':str(data[0])})
        else:
            return json.dumps({'html':'<span>Enter the required fields</span>'})

    except Exception as e:
        return json.dumps({'error':str(e)})
    finally:
        cursor.close() 
        conn.close()

@app.route('/createEventPage')
def createEventPage():
    if session.get('user'):
        return render_template('createEvent.html')
    else:
        return render_template('error.html',error = 'Unauthorized Access')


@app.route('/createEvent',methods=['POST'])
def createEvent():
    try:
        _eventname = request.form['inputEventname']
        _eventlink = request.form['inputEventlink']
        _eventtype = request.form['inputEventtype']
        _eventdatetime = request.form['inputEventdatetime']
        _eventuser_id = session['user']
        conn = mysql.connect()
        cursor = conn.cursor()
        print type(_eventuser_id)
        cursor.callproc('sp_getUserNamefromId',(_eventuser_id,))
        data = cursor.fetchall()
        print data
        _eventusername = data[0][0]
        print _eventusername
        cursor.close() 
        conn.close()
        # validate the received values
        if _eventname and _eventtype and _eventdatetime and _eventusername:
            
            # All Good, let's call MySQL
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_createEvent',(_eventname,_eventlink,_eventtype,_eventuser_id,_eventusername,_eventdatetime))
            data = cursor.fetchall()
            
            if len(data) is 0:
                conn.commit()
                return json.dumps({'message':'Event created successfully !'})
            else:
                return json.dumps({'error':str(data[0])})
            cursor.close() 
            conn.close()
        else:
            return json.dumps({'html':'<span>Enter the required fields</span>'})

    except Exception as e:
        print "Yahin se aara hai"
        return json.dumps({'error':str(e)})
        cursor.close() 
        conn.close()
    # finally:
    #     cursor.close() 
    #     conn.close()


if __name__ == "__main__":
    app.run(debug=True)



