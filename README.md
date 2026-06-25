# Skill dump 
Do you learn something new every day, but forget what you have learned with time? That application is the solution.

## Features:
- Log in, Sign up.
- Create, modify and delete (private) **skill entries**. Choose skill type for each skill.
- Search skills by keyword or by skill type (in private skills).
- Browse your skills and see your **skill stats** on the home page.
- Add a **profile picture**. It will be visible for all users.
- Browse threads even without login (**easy redirection** after login, back to the thread you were browsing). Note that there is no easy redirection available on the sign up or when the user was not logged in before.
- Create your own **threads** and send messages to others' threads.
- Check other user's profiles and see their profile picture and last thread sent messages.

## Technical notes on the app:
- The developer tried their best to consider security risks, for example SQL or XSS injections. CSRF token against CSRF attacks is implemented. The 'next_page' logic contains a certain security risk, as it relies on user input for redirection and should be validated against a whitelist of allowed pages.
- private_ideas.py serves as a module for dealing with all private skills related matters.
- App supports large amounts of data in threads without lagging. A report is included in big_data_amount_report.md.

## How to test:
- Clone this repository to the machine using `git clone https://github.com/plumbusp/Skill_dump_app.git`
- Activate virtual environment: `python3 -m venv venv`,then `source venv/bin/activate`
- Install Python and Flask. If Flask is not installed: `pip install flask`
- Set up the environmental variable SECRET_KEY. Use this command (PowerShell):
```
$env:SECRET_KEY = (python -c "import secrets; print(secrets.token_hex(8))")
```
(or bash)
```
export SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(8))")
```
- Run the application using the `flask run` command and go to http://127.0.0.1:5000
