import os
import json
from flask import request,render_template,g,redirect,session,url_for,flash
from app import application as app
from app.model import create_connection, close_connection
from rethinkdb.errors import RqlRuntimeError,RqlDriverError
import rethinkdb as r
from app.configuration import RDB_PORT,UDIO_DB,RDB_HOST


def get_location(place):
    geo=[]
    if place=='alappuzha':
        geo.append(9.498)
        geo.append(76.338)
    elif place=='ernakulam':
        geo.append(9.981)
        geo.append(76.299)
    elif place=='idukki':
        geo.append(9.981)
        geo.append(76.299)
    elif place=='kannur':
        geo.append(11.874)
        geo.append(75.370)
    elif place=='kasargod':
        geo.append(12.510)
        geo.append(74.985)
    elif place=='kottayam':
        geo.append(9.591)
        geo.append(76.522)
    elif place=='kozhikode':
        geo.append(11.258)
        geo.append(75.780)
    elif place=='malappuram':
        geo.append(11.073)
        geo.append(76.073)
    elif place=='palakkad':
        geo.append(10.786)
        geo.append(76.654)
    elif place=='trivandrum':
        geo.append(8.524)
        geo.append(76.936)
    elif place=='thrissur':
        geo.append(10.527)
        geo.append(76.214)
    elif place=='wayanad':
        geo.append(11.703)
        geo.append(76.083)

    return geo




APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static/tmp/')
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER

@app.route('/',methods=['GET','POST'])
@app.route('/home',methods=['GET','POST'])
def home():
        if request.method=='GET':
            title="Welcome to Udio"
            return render_template('home/udio.html',title=title)
        if request.method=='POST':
            return redirect(url_for('login'),code=307)

@app.before_request
def before_request():
    try:
        g.rdb_conn = r.connect(host=RDB_HOST, port=RDB_PORT,db=UDIO_DB)
    except RqlDriverError:
        abort(503, "Database connection could not be established.")

@app.teardown_request
def teardown_request(exception):
    try:
        g.rdb_conn.close()
    except AttributeError:
        pass

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='GET':
         if 'user' in session:
             return redirect(url_for('dashboard'))
         else:
            return render_template('main/login.html')
    elif request.method=='POST':
         username=request.form['username']
         password=request.form['password']
         if username == '' or password=='':
             flash('enter valid username or password')
             return render_template('main/login.html')
         user=list(r.db('udio').table('users').filter((r.row['username']==username) & (r.row['password']==password) ).run(g.rdb_conn))
         count=r.db('udio').table('users').filter((r.row['username']==username) & (r.row['password']==password)).count().run(g.rdb_conn)
         if count >0:
             access=1
         else:
             access=0
         if access==0:
             return "authentication error"
         else:
             session['user']=user
             return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    session.pop('user',None)
    flash("Logged out")
    return redirect(url_for('login'))

@app.route('/dashboard',methods=['POST','GET'])
def dashboard():
    if request.method=='GET':
        if 'user' not in session:
            flash('Please Login')
            return redirect(url_for('login'))
        username=session['user'][0]['username']
        password=session['user'][0]['password']
        name=''
        print("Username:")
        print(username)
        user=list(r.db('udio').table('users').filter(r.row['username']==username ).run(g.rdb_conn))
        name=user[0]['firstname']+user[0]['lastname']
        image_path=user[0]['image_path']
        print "Image Path"
        print image_path
        return render_template('admin/select_ride.html',name=name,img=image_path)
    if request.method=='POST':
        to_place=request.form['to_place']
        from_place=request.form['from_place']
        date=request.form['date']
        return redirect(url_for('find_rider',to_place=to_place,from_place=from_place,__date__=date))

@app.route('/find_rider/<to_place>/<from_place>/<__date__>',methods=['GET','POST'])
def find_rider(from_place,to_place,__date__):
    if request.method=='GET':
        riders=list(r.db('udio').table('rides').filter((r.row['from_place']==from_place) & ( r.row['to_place']==to_place) & (r.row['date']==__date__) & (r.row['done']==0)).order_by(r.desc('date')).run(g.rdb_conn))
        return render_template('admin/ride_list.html',riders=riders,name=session['user'][0]['firstname']+session['user'][0]['lastname'],img=session['user'][0]['image_path'])
    if request.method=='POST':
        return redirect(url_for('/ride_request'),code=307)
        #find rider id
        #find sender id
        #create a table called messages
        #add user and rider id
        #add a request message



@app.route('/session')
def session_view():
    sess=session['user']
    return json.dumps(sess)


@app.route('/review',methods=['GET','POST'])
def review():
    return render_template("admin/delivery.html",name=session['user'][0]['firstname']+session['user'][0]['lastname'],img=session['user'][0]['image_path'])

@app.route('/tripplan',methods=['GET','POST'])
def tripplan():
    if request.method=='GET':
        if 'user' in session:
            name=session['user'][0]['firstname']+session['user'][0]['lastname']

            return render_template('admin/tripplan.html',name=name,img=session['user'][0]['image_path'],)
        else:
            return redirect(url_for('login'))
    if request.method=='POST':
        to_place=request.form['to_place']
        from_place=request.form['from_place']
        date=request.form['date']
        vehicle=request.form['vehicle']
        time=request.form['time']
        conn=create_connection()
        extra_info=request.form['extra_info']
        mobile=session['user'][0]['mobile']
        geo=get_location(from_place)
        geo_from_lat=geo[0]
        geo_from_lon=geo[1]
        ride=list(r.db('udio').table('rides').insert([ {
                        'to_place':to_place,
                        'licence':session['user'][0]['licence'],
                        'from_place':from_place,
                        'date':date,
                        'time':time,
                        'vehicle':vehicle,
                        'extra_info':extra_info,
                        'availability':0,
                        'done':0,
                        'created_date':r.now(),
                        'rider_id':session['user'][0]['id'],
                        'email':session['user'][0]['email'],
                        'name':session['user'][0]['firstname']+session['user'][0]['lastname'],
                        'review':0,
                        'image_path':session['user'][0]['image_path'],
                        'current':1,
                        'mobile':mobile,
                        'cordinates':[{'lat':geo_from_lat,'lon':geo_from_lon }],
                        'sender_id':0
                        }]).run(g.rdb_conn,time_format="raw"))
        return render_template('admin/ride_created.html',riders=ride[0],name=session['user'][0]['firstname']+session['user'][0]['lastname'],img=session['user'][0]['image_path'])




@app.route('/ride_request',methods=['POST'])
def ride_request():
    #sender_id=session['user'][0]['id']
    data=request.json

    print data
    ride_id=data['id'][0:36]
    rider_id=data['id'][36:]
   # rider_id=data['rider_id']
    sender=session['user'][0]['id']
    r.db('udio').table('packages').insert({
        'sender':sender,
        'ride_id':ride_id,
        'rider_id':rider_id,
        'accept':0,
        'date':r.now()
        }).run(g.rdb_conn)
    print ('data registered')

    return "Ride request"


@app.route('/add_location',methods=['POST'])
def add_location():
    ride_id=request.form['ride_id']
    lat=request.form['lat']
    lon=request.form['lon']
    ride=r.db('udio').table('rides').filter({'id':ride_id}).insert([{'lat':lat, 'lon':lon}]).run(g.rdb_conn)
    return  "locations added"


@app.route('/consignments',methods=['GET','POST'])
def consignments():
    if request.method=='GET':
        rides=list(r.db('udio').table('rides').filter((r.row['rider_id']==session['user'][0]['id']) & (r.row['current']==1)).run(g.rdb_conn))
        packages=list(r.db('udio').table('packages').filter({'sender'==session['user'][0]['id']}).run(g.rdb_conn))
        return render_template('admin/consignments.html',name=session['user'][0]['firstname']+session['user'][0]['lastname'] ,rides=rides,img=session['user'][0]['image_path'],packages=packages)
    if request.method=='POST':
        ride_id=request.form['ride_id']

        print (ride_id)
        try:
            rides=r.db('udio').table('rides').filter((r.row['rider_id']==session['user'][0]['id']) & (r.row['current']==1) &(r.row['id']==ride_id)).delete(return_changes=True).run(g.rdb_conn)

        except:
            return render_template('admin/cancel_ride.html',msg="Error!.No such ride found")

        return render_template('admin/cancel_ride.html',msg="Ride cancelled")

@app.route('/map/<id>',methods=['GET','POST'])
def map_view(id):
    if request.method=='GET': 
        print id
        from_place=r.db('udio').table('rides').get(id).pluck('from_place').run(g.rdb_conn)
        to_place=r.db('udio').table('rides').get(id).pluck('to_place').run(g.rdb_conn)
        cordinates=r.db('udio').table('rides').get(id).pluck('cordinates').run(g.rdb_conn)
        print cordinates['cordinates']
        print from_place
        print to_place
        geo_from=get_location(from_place['from_place'])
        geo_to=get_location(to_place['to_place'])
        geo_rider_lat=cordinates['cordinates'][-1]['lat']
        geo_rider_lon=cordinates['cordinates'][-1]['lon']
        print geo_rider_lat
        print geo_rider_lon
        print geo_from
        print geo_to
        #get_geolocation(place)
        geo_from_lat=geo_from[0]
        geo_from_lon=geo_from[1]
        geo_to_lat=geo_to[0]
        geo_to_lon=geo_to[1]
        return render_template('main/map.html',geo_from_lat=geo_from_lat,geo_from_lon=geo_from_lon,geo_to_lat=geo_to_lat,geo_to_lon=geo_to_lon,geo_rider_lat=geo_rider_lat,geo_rider_lon=geo_rider_lon)

    if request.method=='POST':
        from_place=r.db('udio').table('rides').get(id).pluck('from_place').run(g.rdb_conn)
        to_place=r.db('udio').table('rides').get(id).pluck('to_place').run(g.rdb_conn)
        cordinates=r.db('udio').table('rides').get(id).pluck('cordinates').run(g.rdb_conn)
        geo_from=get_location(from_place['from_place'])
        geo_to=get_location(to_place['to_place'])
        geo_rider_lat=cordinates['cordinates'][-1]['lat']
        geo_rider_lon=cordinates['cordinates'][-1]['lon']
        print geo_rider_lat
        print geo_rider_lon
        print geo_from
        print geo_to
        #get_geolocation(place)
        geo_from_lat=geo_from[0]
        geo_from_lon=geo_from[1]
        geo_to_lat=geo_to[0]
        geo_to_lon=geo_to[1]
        return render_template('main/map.html',geo_from_lat=geo_from_lat,geo_from_lon=geo_from_lon,geo_to_lat=geo_to_lat,geo_to_lon=geo_to_lon,geo_rider_lat=geo_rider_lat,geo_rider_lon=geo_rider_lon)





@app.route('/request')
def request_sent():
    return render_template('admin/request.html',img=session['user'][0]['image_path'])

@app.route('/requests_area',methods=['GET','POST'])
def request_area():
    if request.method=='GET':
    #req=list(r.db('udio').table('packages').filter({'rider_id':session['user'][0]['id']}).run(g.rdb_conn,time_format="raw")) #.eq_join('ride_id',r.db('udio').table('rides')).zip().run(g.rdb_conn,time_format="raw"))
   # req=list(r.db('udio').table('packages').filter({'rider_id':session['user'][0]['id']}).eq_join('ride_id',r.db('udio').table('rides')).zip().run(g.rdb_conn,time_format="raw"))
        req=list(r.db('udio').table('packages').filter({'rider_id':session['user'][0]['id']}).eq_join('ride_id',r.db('udio').table('rides')).zip().eq_join('sender',r.db('udio').table('users')).zip().run(g.rdb_conn,time_format="raw"))
        print (req)
       # return json.dumps(req)
        return render_template('admin/request_area.html', rides=req,img=session['user'][0]['image_path'])
    if request.method=='POST':
        ride_id=request.form['ride_id']
        sender_id=request.form['sender_id']
        ride=list(r.db('udio').table('rides').filter({'id':ride_id}).update({'done':1}).run(g.rdb_conn,time_format="raw"))
        package=list(r.db('udio').table('packages').filter((r.row['ride_id']== ride_id) & (r.row['sender']==sender_id)).update({'accept':1}).run(g.rdb_conn,time_format="raw"))
        return render_template('admin/accepted.html',img=session['user'][0]['image_path'])
        #r.db('udio').table('packageskju
        return "AAA"

