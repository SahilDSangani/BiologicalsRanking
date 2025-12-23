from flask import Flask, render_template, jsonify
import pandas as pd
import os

app = Flask(__name__)

# Load data into Pandas DataFrame
df = pd.read_csv('data.csv')

@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    """API endpoint to get all data as JSON"""
    return jsonify(df.to_dict('records'))

@app.route('/api/data/sorted/<column>/<direction>')
def get_sorted_data(column, direction):
    """API endpoint to get sorted data"""
    ascending = (direction == 'asc')
    sorted_df = df.sort_values(by=column, ascending=ascending)
    return jsonify(sorted_df.to_dict('records'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
