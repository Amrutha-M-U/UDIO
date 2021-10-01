from flask import request,jsonify
from flask_restful import Resource ,Api
import rethinkdb as r
from app.model import create_connection , close_connection

class geo(Resource):
    def get(self):
        return {'hello':'world' }
    def post(self):
        ride_id=request.form['ride_id']
        lon=request.form['lon']
        lat=request.form['lat']
        conn=create_connection()
        r.db('udio').table('rides').get(ride_id).update({'cordinates': r.row['cordinates'].append({'lat':lat, 'lon':lon})}).run(conn)
        print lat
        print lon
        close_connection(conn)
        return 'post'

class login_mob(Resource):
    def post(self):
        username=request.form['username']
        password=request.form['password']
        print username
        print password
        conn=create_connection()
        user=list(r.db('udio').table('users').filter((r.row['username']==username) & (r.row['password']==password) ).pluck('id').run(conn))
        close_connection(conn)
        print user
        id={'userid':user}
        return jsonify(id=id)
        conn=create_connection()
        count=r.db('udio').table('users').filter((r.row['username']== username) & (r.row['password']==password) ).count().run(conn)
        if count > 0:
            user=list(r.db('udio').table('users').filter((r.row['username']== username) & (r.row['password']==password) ).run(conn))
            return { 'user': user}
        else:
            return {'error':'user not found'}
        
from app import application as app

api=Api(app)

api.add_resource(login_mob,'/moblogin')
api.add_resource(geo,'/geo')


