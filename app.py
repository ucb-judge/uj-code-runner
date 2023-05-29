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
    print('If you reached here, overwriting the function did not work')
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps({
            'message': 'If you reached here, overwriting the function did not work',
        })
    }

'''
    Handle the request to run a C++ program
    
    Parameters:
        event (dict): The event payload
        context (dict): The context payload
        
    Returns:
        A response object
'''
def cpp_handler(event, context):
    # Validate if the request body is empty
    request = validate_empty_request(event)
    if request != None:
        return request
    
    # Parse the multipart form data from the request body
    form_data = get_form_data(event)
    if 'statusCode' in form_data:
        return form_data
    
    # Save the uploaded sourceCode file to a temporary location
    with tempfile.NamedTemporaryFile(suffix='.cpp', delete=False) as file:
        file.write(form_data['code'][0])
        source_code_filepath = file.name
    # Save the uploaded input file to a temporary location
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as file:
        file.write(form_data['input'][0])
        input_filepath = file.name
    # Create a temporary file to store the output
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as file:
        output_filepath = file.name
    
    # Compile the C++ code using ./cpp/compile_cpp.sh
    compilation_result = subprocess.run(['./cpp/compile_cpp.sh', source_code_filepath], capture_output=True)
    compilation_error = check_compilation_result(compilation_result)
    if compilation_error != None:
        return compilation_error
 
    # Run the compiled binary using ./cpp/run_cpp_program.sh
    compiled_source_code_filepath = re.sub(r'\.cpp$', '', source_code_filepath)
    execution_result = subprocess.run(['./cpp/run_cpp_program.sh', compiled_source_code_filepath, input_filepath, output_filepath], capture_output=True)
    execution_error = check_execution_result(execution_result)
    if execution_error != None:
        return execution_error    
    
    # Successfully executed the program
    return success_response (execution_result, output_filepath)
    


'''
    Validate if the request body is empty
    
    Parameters:
        event (dict): The event payload
        
    Returns:
        None if the request body is not empty
        A response object if the request body is empty
'''
def validate_empty_request(event):
    print('event=', event)
    print('body=', event['body'])
    if event['body'] == None:
        print('body is None')
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'message': 'No files uploaded'
            })
        }
    return None

'''
    Parse the multipart form data from the request body
    
    Parameters:
        event (dict): The event payload
    
    Returns:
        form_data (dict): The parsed form data
'''
def get_form_data(event):
    fp = io.BytesIO(event['body'].encode('utf-8'))
    pdict = cgi.parse_header(event['headers']['Content-Type'])[1]
    if 'boundary' in pdict:
        pdict['boundary'] = pdict['boundary'].encode('utf-8')
    pdict['CONTENT-LENGTH'] = len(event['body'])
    form_data = cgi.parse_multipart(fp, pdict)
    print('form_data=', form_data)
    # Validate if the multipart form data contains the required keys (sourceCode, input, timeLimit, memoryLimit)
    if 'sourceCode' not in form_data or 'input' not in form_data or 'timeLimit' not in form_data or 'memoryLimit' not in form_data:
        # Return an error response of which key is missing
        missing_keys = []
        if 'sourceCode' not in form_data:
            missing_keys.append('sourceCode')
        if 'input' not in form_data:
            missing_keys.append('input')
        if 'timeLimit' not in form_data:
            missing_keys.append('timeLimit')
        if 'memoryLimit' not in form_data:
            missing_keys.append('memoryLimit')
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'message': 'Missing keys in multipart form data',
                'data': 'The following keys are missing in the multipart form data: ' + ', '.join(missing_keys),
            })
        }
    return form_data

'''
    Check if the compilation was successful
    
    Parameters:
        compilation_result (subprocess.CompletedProcess): The result of the compilation
        
    Returns:
        None if the compilation was successful
        A response object if the compilation failed
'''
def check_compilation_result(compilation_result):
    print ('compilation_result=', compilation_result)
    if compilation_result.returncode != 0:
        # Compilation failed, return the error message
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'message': 'Compilation failed',
                'data': '\n'.join(compilation_result.stderr.decode('utf-8').split('\n')[:-1])
            })
        }
    return None

'''
    Check if the execution was successful
    
    Parameters:
        execution_result (subprocess.CompletedProcess): The result of the execution
        
    Returns:
        None if the execution was successful
        A response object if the execution failed
'''
def check_execution_result(execution_result):
    print ('execution_result=', execution_result)
    if execution_result.returncode != 0:
        # Execution failed, return the error message
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'message': 'Execution failed',
                'data': execution_result.stderr.decode('utf-8')
            })
        }
    return None

'''
    Return a success response
    
    Parameters:
        execution_result (subprocess.CompletedProcess): The result of the execution
        output_filepath (str): The path to the output file
    
    Returns:
        A response object
'''
def success_response (execution_result, output_filepath):
    
    memory_usage = execution_result.stdout.decode('utf-8').split('\n')[0]
    execution_time = execution_result.stdout.decode('utf-8').split('\n')[1]
    # Read the output file
    with open(output_filepath, 'r') as file:
        output = file.read()

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps({
            'message': 'Execution successful',
            'data': json.dumps({
                'output': output,
                'memory_usage': memory_usage,
                'execution_time': execution_time
            })
        })
    }
                           