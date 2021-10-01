import json
from app.model import create_connection, close_connection
import rethinkdb as r
from app import application as app
from flask import render_template , request,session,flash,redirect,url_for
import os
from werkzeug import secure_filename

app.secret_key='ADSDSDSFAW@!@!!33232'

ALLOWED_EXTENSIONS=set(['jpg','jpeg'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS

def check_duplicate(username):
    conn=create_connection()
    count=r.db('udio').table('users').filter({'username':username }).count().run(conn)
    if count > 0:
        return 1
    else:
        return 0

'''
@app.route('/find_rider',methods=['GET','POST'])
def find_riderr():
    if request.method=='GET':
        return "find rider"
    if request.method=='POST':
        to=request.form['to']
        from_place=request.form['from_place']
        conn=create_connection()
        data=r.db('udio').table('ride').filter({'from':from_place}).run(conn)
        close_connection(conn)
        return data
'''
@app.route('/create_ride',methods=['GET','POST'])
def create_ride(sender_id):
    if request.method=='GET':
        return "create rider"
    if request.method=='POST':
        from_place=request.form['from']
        to=request.form['to']
        conn=create_connection()
        data=list(r.db('udio').table('rides').insert([
            {
                'sender_id':sender_id,
                'from_place':from_place,
                'to_place':to,
                'date':r.now(),
                'completed':0,
                'rider_id':None

            }]).run(conn))
        print (data[0]['id'])
        user=r.db('udio').table('users').filter({'id':session['user'][0]['id'] }).prepend(data[0]['id']).run(conn)
        close_connection(conn)
        return "rider created"

@app.route('/reg',methods=['GET','POST'])
def sender_reg():
    if request.method=="GET":
        return render_template('main/snp.html')

    if request.method == "POST":
        firstname=request.form['firstname']
        lastname=request.form['lastname']
        address=request.form['address']
        dob=request.form['dob']
        licence=request.form['licence']
        username=request.form['username']
        password=request.form['password']
        country=request.form['country']
        state=request.form['state']
        district=request.form['district']
        pin=request.form['pin']
        mobile=request.form['mobile']
        email=request.form['email']
        file=request.files['file_upload']
        conn=create_connection()
        access=check_duplicate(username)
    if access==1:
        flash("Username already taken. Please use a different username")
        return render_template('main/login.html')
    else:

        if file and allowed_file(file.filename):
            filename=username+'.jpg'
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))

        else :
            return "Error!.Profile image uploaded is incompatible"
        r.db('udio').table('users').insert([
                { 'firstname':firstname,
                  'lastname':lastname,
                  'address':address,
                  'dob':dob,
                  'licence':licence,
                  'username':username,
                  'password':password,
                  'country':country,
                  'state':state,
                  'district':district,
                  'pin':pin,
                  'mobile':mobile,
                  'email':email,
                  'packages':[],
                  'rides':[],
                  'image_path':'static/tmp/'+filename
                  }
                ]).run(conn)
        close_connection(conn)
        return render_template('main/signup.html') 

@app.route('/selectride')
def select_ride():
    from_place=request.form['from']
    to_place=request.form['to']
    if from_place == to_place:
        flash ("Selected places are same")
        return render_template('admin/admin.html')
    else:
        conn=create_connection()
        rides=list(r.db('udio').table('users').filter((r.row['from_place']==from_place)).filter (r.row['to_place']==to_place).order_by(index='date').run(conn))
        conn.close()
        return render_template('admin/rides.html')

@app.route('/tracking',methods=['POST','GET'])
def tracking():
    if request.method=='GET':
        if 'user' in session:
            name=session['user'][0]['firstname']+session['user'][0]['lastname']
            return render_template('admin/tracking.html',name=name,img=session['user'][0]['image_path'])
    if request.method=='POST':
        ride_id=request.form['ride_id']
        return redirect(url_for('map_view',id=ride_id))
        return "track"

@app.route('/delivery')
def delivery():
    if 'user' in session:
        name=session['user'][0]['firstname']+session['user'][0]['lastname']
        conn=create_connection()
        rides=list(r.db('udio').table('rides').filter({'rider_id':session['user'][0]['id']}).run(conn,time_format="raw"))
        sender=list(r.db('udio').table('packages').filter({'sender_id':session['user'][0]['id']}).run(conn,time_format="raw"))
        #return json.dumps(rides)
        close_connection(conn)
        return render_template('admin/reviews.html',name=name,img=session['user'][0]['image_path'],rides=rides,sender=sender)
    else :
        flash("You are not logged in ")
        return redirect(url_for('login.html'))


