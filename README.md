# safety-app-portal

Web portal for [*safety-app*](https://github.com/rice-apps/safety-app)

## Development
Set up your Python virtual environment, and install all required packages.

### Environment Tools

* Use a python virtual environment: 
	* `sudo pip install virtualenv`
* Use _autoenv_ to load directory-based environment: 
	* `sudo pip install autoenv` 
	* `echo "source 'which activate.sh'" >> ~/.bashrc`

### Starting Up

#### Initial Setup:
_In the project repo._
* Create your virtual environment:
	* `virtualenv venv`
* Activate environment:
	* `source venv/bin/activate`
* Install dependencies:
	* `pip install -r requirements.txt`

#### Normal Flow:
With the provided `.env` file, once you `cd`, your virtual environment should start with local development settings loaded.
* Navigate to directory 
	* `cd safety-app-portal`

Run `setup.py` to set-up a local version of the database.
Run `app.py` to launch the Flask app.

## Heroku Deployment

Hosted on Heroku. Instructions soon.
