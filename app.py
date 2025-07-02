#!/usr/bin/env python3
from flask import Flask, render_template, request, jsonify
import subprocess
import json
import os
import threading
import time

app = Flask(__name__)

# Global variable to store the latest output
latest_output = ""
output_lock = threading.Lock()

def run_command(cmd):
    """Run a command and capture its output"""
    global latest_output
    
    try:
        # Clear previous output
        with output_lock:
            latest_output = f"Running command: {' '.join(cmd)}\n"
        
        # Run the command
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
            cwd=os.getcwd()  # Ensure we're in the right directory
        )
        
        # Read output in real-time
        output_lines = []
        for line in process.stdout:
            output_lines.append(line.strip())
            # Update global output
            with output_lock:
                latest_output = f"Running command: {' '.join(cmd)}\n" + "\n".join(output_lines)
        
        # Wait for process to complete with timeout
        try:
            process.wait(timeout=300)  # 5 minute timeout
        except subprocess.TimeoutExpired:
            process.kill()
            error_msg = "Command timed out after 5 minutes"
            with output_lock:
                latest_output += f"\n{error_msg}"
            return False, error_msg
        
        return process.returncode == 0, "\n".join(output_lines)
        
    except Exception as e:
        error_msg = f"Error running command: {str(e)}"
        with output_lock:
            latest_output = error_msg
        return False, error_msg

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/refresh', methods=['POST'])
def refresh():
    """Handle refresh button click"""
    try:
        success, output = run_command(['python', 'speedtest.py', 'refresh'])
        return jsonify({
            'success': success,
            'output': output
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'output': f'Server error: {str(e)}'
        })

@app.route('/bench', methods=['POST'])
def bench():
    """Handle bench button click"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'output': 'No data received'
            })
        
        number = data.get('number', 3)
        
        if not str(number).isdigit() or int(number) <= 0:
            return jsonify({
                'success': False,
                'output': 'Please provide a valid positive number'
            })
        
        success, output = run_command(['python', 'speedtest.py', 'bench', str(number)])
        return jsonify({
            'success': success,
            'output': output
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'output': f'Server error: {str(e)}'
        })

@app.route('/run', methods=['POST'])
def run():
    """Handle run button click"""
    try:
        success, output = run_command(['python', 'speedtest.py', 'run'])
        return jsonify({
            'success': success,
            'output': output
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'output': f'Server error: {str(e)}'
        })

@app.route('/get_output')
def get_output():
    """Get the latest output"""
    with output_lock:
        return jsonify({'output': latest_output})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 