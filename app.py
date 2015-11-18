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


def checkAdmin(_userID):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.callproc('sp_checkAdmin',(_userID,))
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    if data[0][0] == 'admin':
        return True 
    else:
        return False

def getAllUsers(): 
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.callproc('sp_getUsers',())
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    data = list(data)
    data = [list(elem) for elem in data]
    return data

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
        return render_template('error.html',error = str(e))
    finally:
        cursor.close()
        conn.close()

@app.route('/userHome')
def userHome():
    sessionUser = session.get('user')
    if sessionUser:

        isAdmin = checkAdmin(sessionUser)

        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_GetEvents',())
        data = cursor.fetchall()
        allEvents = data
        cursor.close() 
        conn.close()

        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_GetUserEvents',(sessionUser,))
        data = cursor.fetchall()
        allUserEvents = data
        cursor.close() 
        conn.close()

        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_getUserNamefromId',(sessionUser,))
        data = cursor.fetchall()
        currentusername = data[0][0]
        cursor.close() 
        conn.close()

        allEvents = list(allEvents)
        allEvents = [list(elem) for elem in allEvents]
        allUserEvents = list(allUserEvents)
        allUserEvents = [list(elem) for elem in allUserEvents]

        ## TODO: create view for getevents 
        if isAdmin:
            return render_template('userHome.html', allData = list(allEvents), 
                                                    modifyData= list(allEvents), 
                                                    isAdmin = isAdmin,
                                                    users = list(getAllUsers()),
                                                    currentUser = currentusername
                                                    )
        else: 
            return render_template('userHome.html', allData = list(allEvents), 
                                                    modifyData= list(allUserEvents), 
                                                    isAdmin = isAdmin,
                                                    currentUser = currentusername
                                                    )

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
                #redirect to login! 
                conn.commit()
                return redirect('/showLogin')
            else:
                return json.dumps({'error':str(data[0])})
        else:
            return json.dumps({'html':'<span>Enter the required fields</span>'})

    except Exception as e:
        return json.dumps({'error':str(e)})
    finally:
        cursor.close() 
        conn.close()

@app.route('/editProfilePage')
def editProfilePage():
    if session.get('user'):
        _userID = session.get('user')
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_getUserfromId',(_userID,))
        data = cursor.fetchall()
        print data
        username = data[0][1]
        rollNo = data[0][2]
        cursor.close() 
        conn.close()
        return render_template('editProfile.html',rollNo=rollNo,username=username)
    else:
        return render_template('error.html',error = 'Unauthorized Access')

@app.route('/editProfile',methods=['POST'])
def editProfile():
    try:
        # _username = request.form['inputUsername']
        _rollno = request.form['inputRollno']
        _userID = session.get('user')
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_editUserProfileData',(_userID,_rollno))
        conn.commit()
        cursor.close() 
        conn.close()
        # validate the received values
        return redirect('/userHome')
        

    except Exception as e:
        return json.dumps({'error':str(e)})
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
                #console.log("New event created"); 
                return redirect('/userHome')
            else:
                return render_template('error.html',error = str(data[0]))

            cursor.close() 
            conn.close()
        else:
            return json.dumps({'html':'<span>Enter the required fields</span>'})

    except Exception as e:
        return render_template('error.html',error ='Event exists. Hit Back on your browser!')
        cursor.close() 
        conn.close()
    # finally:
    #     cursor.close() 
    #     conn.close()


#INCOMPLETE
@app.route('/deleteUser/<int:_userID>')
def deleteUser(_userID):
    sessionUser = session.get('user')

    if sessionUser and checkAdmin(sessionUser):
        try:
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_deleteUser1',(_userID,))
            # data = cursor.fetchall()
            # print data
            cursor.close()
            conn.close()
            return redirect('/userHome')
        except Exception as e:
            return json.dumps({'error':str(e)})
            cursor.close() 
            conn.close()
    else:
        return render_template('error.html',error = 'Unauthorized Access')

@app.route('/modifyEventSendData/<int:_eventID>')
def modifyEventSendData(_eventID):
    sessionUser = session.get('user')
    if sessionUser:
        try:
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_GetEventFromID',(_eventID,))
            data = cursor.fetchall()
            print list(data)
            cursor.close()
            conn.close()
            return render_template('modifyEvent.html',event=list(data[0]))
        except Exception as e:
            return json.dumps({'error':str(e)})
            cursor.close() 
            conn.close()
    else:
        return render_template('error.html',error = 'Unauthorized Access')


@app.route('/modifyEvent',methods=['POST'])
def modifyEvent():
    try:
        _eventname = request.form['inputEventname']
        _eventlink = request.form['inputEventlink']
        _eventtype = request.form['inputEventtype']
        _eventdatetime = request.form['inputEventdatetime']
        print "We are here."
        _eventID = request.form['eventID']
        print _eventdatetime

        conn = mysql.connect()
        cursor = conn.cursor()
        #print type(_eventuser_id)
        cursor.callproc('sp_modifyEvent1',(_eventID,_eventname,_eventlink,_eventtype,_eventdatetime))
        conn.commit()
        cursor.close() 
        conn.close()
        # validate the received values
        return redirect('/userHome')
        

    except Exception as e:
        return json.dumps({'error':str(e)})
        cursor.close() 
        conn.close()


if __name__ == "__main__":
    app.run(debug=True)



