from flask import Flask, render_template, request, jsonify
from compiler import compile_and_run
import sys
from io import StringIO

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compile', methods=['POST'])
def compile_code():
    code = request.json.get('code', '')
    
    # Capture stdout to get print statements
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()

    try:
        result = compile_and_run(code)
        sys.stdout = old_stdout
        output = redirected_output.getvalue()
        
        if output:
            return jsonify({'output': output.strip()})
        elif result is not None:
            return jsonify({'output': str(result)})
        return jsonify({'output': 'Code executed successfully'})
    
    except Exception as e:
        sys.stdout = old_stdout
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True) 