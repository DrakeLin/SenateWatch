import csv, io, os
from flask import Flask, render_template, request
from html import escape

# filepath = '/Users/hangyullynakim/Desktop/SCHACKS_2020/RepBallot/2020.csv'

# # Initiates flask things
app = Flask(__name__)

# Takes a filpath to a .csv to read file
def read_csv(filepath, column_names):
    with open(filepath, newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            record = {name: value for name, value in zip(column_names, row)}
            yield record

# Makes html syntax string from csv file
def html_table(records):
    column_names = []

    # First detect all posible keys (field names) that are present in records
    for record in records:
        for name in record.keys():
            if name not in column_names:
                column_names.append(name)

    # Create the HTML line by line
    lines = []
    lines.append('<table>\n')
    lines.append('  <tr>\n')
    for name in column_names:
        lines.append('    <th>{}</th>\n'.format(escape(name)))
    lines.append('  </tr>\n')
    for record in records:
        lines.append('  <tr>\n')
        for name in column_names:
            value = record.get(name, '')
            lines.append('    <td>{}</td>\n'.format(escape(value)))
        lines.append('  </tr>\n')
    lines.append('</table>')

    # Join the lines to a single string and return it
    return ''.join(lines)

# Displays initial HTML to prompt user input   
@app.route('/')
def initial():
    return render_template("website.html")

# Display HTML with appropriate table
@app.route('/response', methods=['POST'])
def response():
    # Get year from html form, makes appropriate .csv filename
    year = request.form["year"]
    filename = (str(year) + ".csv")

    # Replace header with filepath to dir containing .csv file
    header = "/Users/hangyullynakim/Desktop/SCHACKS_2020/RepBallot/"
    filepath = header + filename

    # Reads csv
    records = list(read_csv(filepath, 'Name	Party State	Question Measure Date Vote'.split()))
    records = [r for r in records]

    # Makes file
    output = html_table(records)
    file = open("result.html","w")
    file.write(output)
    file.close()
    os.replace('/Users/hangyullynakim/Desktop/SCHACKS_2020/RepBallot/result.html', '/Users/hangyullynakim/Desktop/SCHACKS_2020/RepBallot/templates/result.html')

    return render_template("result.html")
   
# Python equivalent of a main function
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)