from flask import Flask, render_template, request, redirect, url_for
import datetime
import os

app = Flask(__name__)

PREDICTIONS_FILE = 'predictions.txt'
TIME_ZONE_OFFSET = 3  # East African Time (EAT) is UTC+3

def read_predictions():
    if not os.path.exists(PREDICTIONS_FILE):
        return []
    with open(PREDICTIONS_FILE, 'r') as file:
        predictions = file.readlines()
    predictions = [eval(pred.strip()) for pred in predictions]
    return predictions

def write_predictions(predictions):
    with open(PREDICTIONS_FILE, 'w') as file:
        for pred in predictions:
            file.write(str(pred) + '\n')

def clean_old_predictions(predictions):
    today = datetime.datetime.utcnow() + datetime.timedelta(hours=TIME_ZONE_OFFSET)
    cutoff_date = today - datetime.timedelta(days=7)
    return [pred for pred in predictions if datetime.datetime.strptime(pred['date'], '%Y-%m-%d') >= cutoff_date]

@app.route('/', methods=['GET', 'POST'])
def index():
    predictions = read_predictions()
    predictions = clean_old_predictions(predictions)
    write_predictions(predictions)
    
    if request.method == 'POST':
        date = request.form['date']
        prediction_type = request.form['prediction_type']
        prediction_text = request.form['prediction_text']
        
        predictions.append({'date': date, 'type': prediction_type, 'prediction': prediction_text})
        write_predictions(predictions)
        
        return redirect(url_for('index'))
    
    return render_template('index.html', predictions=predictions, today=datetime.datetime.utcnow().strftime('%Y-%m-%d'))

@app.route('/select_date', methods=['GET'])
def select_date():
    date = request.args.get('date')
    predictions = read_predictions()
    filtered_predictions = [pred for pred in predictions if pred['date'] == date]
    return render_template('index.html', predictions=filtered_predictions, today=date)

@app.route('/pick', methods=['GET'])
def pick():
    prediction_type = request.args.get('type')
    predictions = read_predictions()
    filtered_predictions = [pred for pred in predictions if pred['type'] == prediction_type]
    return render_template('index.html', predictions=filtered_predictions, today=datetime.datetime.utcnow().strftime('%Y-%m-%d'))

if __name__ == '__main__':
    app.run(debug=True)