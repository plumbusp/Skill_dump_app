# Skill dump 
Do you learn somethings new eveyday, but forget what have you learned with time? That application is the solution

## Features:
- Log in, Sing in.
- Create, modify and delete (private) **skill entries**. Choose skill type for each skill.
- Search skills by keyword or by skill type (in private skills).
- Browse your skills and see your **skill stats** on the home page.
- Add a **profile picture**. It wil be visible for all users.
- Browse threads even without login (**easy redirection** after the login, back to the thread you have been browsing. Not that there is no easy redirection awailable on the sign in or when the user was switching tabs between log in and sign in).
- Create your own **threads** and send messages to others' threads.
- Check other user's profiles and see their profile picture and last thread sent messages.

## Technical notes on the app:
- The developer tried their best to consider security risks, for example SQL or XSS injections. CSRF token against CSRF attacks is implemented. 'next_page' logic contains a certain security risk, as a attacker can put a url to the differnt site, however this issue seems to be out of the scope of the course.
- private_ideas.py serves as a module for dealing with all private skills related matters.
- App supports big amount of data in threads, without lagging. Report is made and is in big_data_amount_report.md

## How to test:
- Install python and flask. If flask is not installed: pip install flask
- Set up the envioromental variable SECRET_KEY. Use this command (powershell)
```$env:SECRET_KEY = (python -c "import secrets; print(secrets.token_hex(8))")```
- run the application suing 'flask run' command and go to the  http://127.0.0.1:5000
  

