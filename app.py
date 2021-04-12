from flask import *
import psycopg2
import psycopg2.extras

app = Flask(__name__)
logged = False
conn = psycopg2.connect(user="group_2", password="RzW1ga8nZDUIn",
                                host="127.0.0.1", database="group_2")
# conn = psycopg2.connect(user="postgres", password="addu",
#                                 host="localhost", database="airline_project")
cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
app.secret_key = 'abc'

password = 'admin'

attrs_acc = ['event_id', 'investigation_type', 'registration_number',
                'accident_number', 'event_date', 'location',
                'country', 'latitude', 'longitude', 'airport_code',
                'airport_name', 'injury_severity', 'aircraft_damage',
                'amateur_built', 'far_description', 'schedule',
                'purpose_of_flight', 'air_carrier', 'total_fatal_injuries',
                'total_serious_injuries', 'total_minor_injuries',
                'total_uninjured', 'weather_condition', 'broad_phase_of_flight',
                'report_publication_date']
attrs_air = ['registration_number', 'aircraft_category',
                'make', 'model', 'number_of_engines', 'engine_type']
@app.route('/')
def index():
    return render_template('index.html', logged = logged)

@app.route('/stats')
def stats():
    return render_template('stats.html', logged = logged)

@app.route('/year')
def year():
    attr = ['accident_year', 'num_of_times', 'perc']
    q = '''with x(sum_t) as
            (select sum(num_of_times)
            from year_data)
            select accident_year, num_of_times, ROUND(num_of_times/(select sum_t from x)*100, 2) as perc
            from year_data
            order by num_of_times desc limit 20;'''    
    cursor.execute(q)
    res = cursor.fetchall()
    return render_template('stat_result.html', logged = logged, res = res, attr = attr, val='year')

@app.route('/model')
def model():
    attr = ['model', 'num_of_times', 'perc']
    q = '''with x(sum_t) as
            (select sum(num_of_times)
            from model_data)
            select model, num_of_times, ROUND(num_of_times/(select sum_t from x)*100, 2) as perc
            from model_data
            order by num_of_times desc limit 20;'''    
    cursor.execute(q)
    res = cursor.fetchall()
    return render_template('stat_result.html', logged = logged, res = res, attr = attr, val='Model')

@app.route('/country')
def country():
    attr = ['country', 'num_of_times', 'perc']
    q = '''with x(sum_t) as
            (select sum(num_of_times)
            from coun_data)
            select country, num_of_times, ROUND(num_of_times/(select sum_t from x)*100, 2) as perc
            from coun_data
            order by num_of_times desc limit 20;'''    
    cursor.execute(q)
    res = cursor.fetchall()
    return render_template('stat_result.html', logged = logged, res = res, attr = attr, val='Country')

@app.route('/location')
def location():
    attr = ['location', 'num_of_times', 'perc']
    q = '''with x(sum_t) as
            (select sum(num_of_times)
            from loc_data)
            select location, num_of_times, ROUND(num_of_times/(select sum_t from x)*100, 2) as perc
            from loc_data
            order by num_of_times desc limit 20;'''    
    cursor.execute(q)
    res = cursor.fetchall()
    return render_template('stat_result.html', logged = logged, res = res, attr = attr, val='Location')

@app.route('/operator')
def operator():
    attr = ['aircraft_operator', 'crew_casualties', 'passenger_casualties']
    q = '''SELECT aircraft_operator, sum(crew_fatal) as crew_casualties, sum(pax_fatality) as passenger_casualties
FROM summary_view
GROUP BY aircraft_operator
ORDER BY sum(crew_fatal+pax_fatality) DESC LIMIT 20;'''    
    cursor.execute(q)
    res = cursor.fetchall()
    return render_template('stat_result.html', logged = logged, res = res, attr = attr, val='Operator')


@app.route('/air_ins', methods=["GET", "POST"])
def air_ins():
    global logged
    inputdata = request.form
    query = 'insert into aircraft1('
    for a in attrs_air:
        query += a +","
    query = query[:len(query)-1] + ') values ('
    for a in attrs_air:
        if 'number_of_engines' == a:
            query += inputdata[a]+","
        else:
            query += "'" + inputdata[a]+"',"
    query = query[:len(query)-1] + ');'
    msg = ''
    print(query)
    #try:
    res = cursor.execute(query)
    conn.commit()
    msg = '1 row successfully inserted'
    # except:
    #    msg = 'Some Error Occurred'
    return render_template('res.html', msg = msg, logged=logged)

@app.route('/acc_ins', methods=["GET", "POST"])
def acc_ins():
    global logged
    inputdata = request.form
    query = 'insert into airline_accident('
    for a in attrs_acc:
        query += a +","
    query = query[:len(query)-1] + ') values ('
    for a in attrs_acc:
        if 'total' in a or a=='latitude' or a=='longitude' or a=='event_id':
            query += inputdata[a]+","
        else:
            query += "'" + inputdata[a]+"',"
    query = query[:len(query)-1] + ');'
    msg = ''
    print(query)
    try:
        res = cursor.execute(query)
        conn.commit()
        msg = '1 row successfully inserted'
    except:
        msg = 'Some Error Occurred'
    return render_template('res.html', msg = msg, logged=logged)

@app.route('/acc_del', methods=["GET","POST"])
def acc_del():
    global logged
    inputdata = request.form
    query = 'delete from airline_accident where event_id='+inputdata['id']+';'
    print(query)
    try:
        cursor.execute(query)
        print('correctly executed')
        conn.commit()
        print('commit proper')
        msg = str(cursor.rowcount) + ' row deleted successfully'
    except:
        msg = 'Some Error occurred'
    return render_template('res.html', msg = msg, logged=logged)

@app.route('/search_db', methods=["GET", "POST"])
def search_db():
    id = request.form['id_inp']
    location = request.form['loc_inp']
    country = request.form['coun_inp']
    date = request.form['day_inp']
    carrier = request.form['carrier_inp']
    model = request.form['model_inp']
    regn = request.form['regn_inp']
    airport = request.form['airport_inp']
    query = 'select * from airline_accident natural join aircraft1 where '
    first = False
    q2 = False
    query2 = 'select * from faa_incident where '
    if id:
        try:
            r = int(id)
        except:
            return render_template('index.html')
        query += 'event_id = ' + id
        first = True
    if location:
        if first:
            query += ' and '
        query += 'location = \'' + location +'\''
        first = True
        query2 += 'event_city = \'' + location + '\''
        q2 = True
    
    if country:
        if first:
            query += ' and '
        query += 'country = \'' + country + '\''
        first = True
    
    if date:
        if first:
            query += ' and '
        query += 'event_date = \'' + date + '\''
        first = True
        if q2:
            query2 += ' and '
        query2 += 'local_event_date = \'' + date + '\''
        q2 = True
    
    if carrier:
        if first:
            query += ' and '
        query += 'air_carrier = \'' + carrier + '\''
        first = True
    
    if model:
        if first:
            query += ' and '
        query += 'model = \'' + model + '\''
        first = True
        if q2:
            query2 += ' and '
        query2 += 'model = \'' + model + '\''
        q2 = True

    if regn:
        if first:
            query += ' and '
        query += 'registration_number = \'' + regn + '\''
        first = True
        if q2:
            query2 += ' and '
        query2 += 'aircraft_registration_nbr = \'' + regn + '\''
        q2 = True
    
    if airport:
        if first:
            query += ' and '
        query += 'airport_name = \'' + airport + '\''
        first = True
        if q2:
            query2 += ' and '
        query2 += 'event_airport = \'' + airport + '\''
        q2 = True

    query += ';'
    query2 += ';'
    print(query)
    print(query2)
    attrs1 = ['event_id', 'investigation_type', 'registration_number',
                'accident_number', 'event_date', 'location',
                'country', 'latitude', 'longitude', 'airport_code',
                'airport_name', 'injury_severity', 'aircraft_damage',
                'amateur_built', 'far_description', 'schedule',
                'purpose_of_flight', 'air_carrier', 'total_fatal_injuries',
                'total_serious_injuries', 'total_minor_injuries',
                'total_uninjured', 'weather_condition', 'broad_phase_of_flight',
                'report_publication_date', 'aircraft_category',
                'make', 'model', 'number_of_engines', 'engine_type']
    attrs2 = ['aids_report_number', 'local_event_date',
                'event_city', 'event_state', 'event_airport',
                'event_type', 'aircraft_damage', 'flight_phase',
                'make', 'model', 'aircraft_series', 'operator',
                'primary_flight_type', 'flight_conduct_code', 
                'flight_plan_filed_code', 'aircraft_registration_nbr',
                'total_fatalities', 'total_injuries', 'nbr_of_engines',
                'pic_certificate_type', 'pic_flight_time_total_make_model']
    try:
        cursor.execute(query)
        res1 = cursor.fetchall()
        res2 = []
        if q2:
            cursor.execute(query2)
            res2 = cursor.fetchall()
    except:
        print("Some Error occurred")
    return render_template('search_result.html', res1 = res1, res2 = res2,
                                attrs1 = attrs1, attrs2 = attrs2,
                                showOne = len(res1) > 0, showTwo = len(res2) > 0,
                                logged = logged)
    
@app.route('/login', methods=["GET","POST"])
def login():
    global logged
    if request.form['password'] == password:
        logged = True
    else:
        logged = False
        print('Wrong password')
    return render_template('index.html',logged = logged)

@app.route('/logout')
def logout():
    global logged
    logged = False
    return render_template('index.html', logged = False)

@app.route('/admin')
def admin():
    global logged, attrs_acc, attrs_air
    if logged:
        return render_template('admin.html', logged = logged, attrs_acc = attrs_acc, attrs_air = attrs_air)
    return render_template('index.html', logged = logged)

if __name__ == '__main__':
    app.run()