##### About
- Social Media Workflow Tool product backend.

##### Setup Virtual Env
1. `pip install virtualenv` in your shell.
2. `virtualenv myenv`
3. `myenv/Scripts/activate` to activate your env

##### For virtualenv to install all files in the requirements.txt file

1. cd to the directory where requirements.txt is located
2. activate your virtualenv
3. run: pip install -r requirements.txt in your shell

##### To Execute and Start Server
1. `uvicorn main:app --reload`

##### Check the API
1. Visit localhost:8000/docs or localhost:8000/redocs to check the Documentation of the API.

##### Refer example files for understanding things.