import cgi
import io
import subprocess
import time
import tempfile
import re
import json

def handler(event, context):
    print('event=', event)
    print('body=', event['body'])
    
    if event['body'] is None:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'response': 'No file uploaded'
            })
        }
        
    fp = io.BytesIO(event['body'].encode('utf-8'))
    pdict = cgi.parse_header(event['headers']['Content-Type'])[1]
    if 'boundary' in pdict:
        pdict['boundary'] = pdict['boundary'].encode('utf-8')
    pdict['CONTENT-LENGTH'] = len(event['body'])
    form_data = cgi.parse_multipart(fp, pdict)
    print('form_data=', form_data)
    
    # Check if the multipart form data contains a file with the key 'code'
    if 'code' not in form_data:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'response': 'No file uploaded'
            })
        }

    # Extract the filename from the 'Content-Disposition' header in the 'body' string
    pattern = r'filename="([^"]*)"'
    matches = re.findall(pattern, event['body'])
    
    filename = matches[0]
    print ('filename=', filename)

    # Check if the uploaded file is a valid C++ file
    if not filename.endswith('.cpp'):
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'response': 'Invalid file type. Only .cpp files are allowed.'
            })
        }
        

    # Save the uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(suffix='.cpp', delete=False) as file:
        file.write(form_data['code'][0])
        tmp_filepath = file.name

    # Compile the C++ code
    print('g++', tmp_filepath, '-o', '/tmp/program')
    compilation_result = subprocess.run(['g++', tmp_filepath, '-o', '/tmp/program'], capture_output=True)
    print ('compilation_result=', compilation_result)

    if compilation_result.returncode != 0:
        # Compilation failed, return the error message
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'response': 'Compilation failed',
                'error': compilation_result.stderr.decode('utf-8')
            })
        }

    # Retrieve the timeout value from the event payload
    if 'timeout' not in form_data:
        timeout_seconds = 1
    else:
        timeout_seconds = int(form_data['timeout'][0])
    
    print ('timeout_seconds=', timeout_seconds)
    # Begin execution of the compiled binary
    start_time = time.time()
    try:
        # Execute the compiled binary and capture the output
        execution_result = subprocess.run(['/tmp/program'], capture_output=True, timeout=timeout_seconds)
        print ('execution_result=', execution_result)
        # Return the output as the response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'response': 'Execution successful',
                'output': execution_result.stdout.decode('utf-8'),
                'execution_time': time.time() - start_time,
                'filename': filename
            })
        }
    except subprocess.TimeoutExpired:
        print ('TimeoutExpired')
        # Handle timeout error
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'response': 'Execution timed out'
            })
        }
    except Exception as e:
        print ('Exception')
        # Handle other errors
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'response': str(e)
            })
        }
