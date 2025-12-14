# Pylint report of the project

Feedback given by pylint:
'''
**\*\***\***\*\*** Module app
app.py:1:0: C0114: Missing module docstring (missing-module-docstring)
app.py:16:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:68:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:74:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:84:4: R1705: Unnecessary "elif" after "return", remove the leading "el" from "elif" (no-else-return)
app.py:105:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:116:4: R1705: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it (no-else-return)
app.py:126:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:133:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:148:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:162:4: R1705: Unnecessary "elif" after "return", remove the leading "el" from "elif" (no-else-return)
app.py:180:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:199:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:206:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:235:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:250:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:252:4: R1705: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it (no-else-return)
app.py:265:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:266:4: R1705: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it (no-else-return)
app.py:280:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:298:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:324:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:337:0: C0116: Missing function or method docstring (missing-function-docstring)
**\*\***\***\*\*** Module calculate_handicap
calculate_handicap.py:1:0: C0114: Missing module docstring (missing-module-docstring)
calculate_handicap.py:4:0: C0116: Missing function or method docstring (missing-function-docstring)
calculate_handicap.py:37:0: C0116: Missing function or method docstring (missing-function-docstring)
**\*\***\***\*\*** Module config
config.py:1:0: C0114: Missing module docstring (missing-module-docstring)
**\*\***\***\*\*** Module db
db.py:1:0: C0114: Missing module docstring (missing-module-docstring)
db.py:5:0: C0116: Missing function or method docstring (missing-function-docstring)
db.py:12:0: C0116: Missing function or method docstring (missing-function-docstring)
db.py:12:0: W0102: Dangerous default value [] as argument (dangerous-default-value)
db.py:20:0: C0116: Missing function or method docstring (missing-function-docstring)
db.py:24:0: C0116: Missing function or method docstring (missing-function-docstring)
db.py:24:0: W0102: Dangerous default value [] as argument (dangerous-default-value)
db.py:31:0: C0116: Missing function or method docstring (missing-function-docstring)
db.py:36:0: C0116: Missing function or method docstring (missing-function-docstring)
db.py:54:0: C0116: Missing function or method docstring (missing-function-docstring)
db.py:56:4: R1705: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it (no-else-return)
db.py:62:0: C0116: Missing function or method docstring (missing-function-docstring)
db.py:64:4: R1705: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it (no-else-return)
db.py:70:0: C0116: Missing function or method docstring (missing-function-docstring)
db.py:75:0: C0116: Missing function or method docstring (missing-function-docstring)
db.py:77:4: R1705: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it (no-else-return)
**\*\***\***\*\*** Module initialize_database
initialize_database.py:1:0: C0114: Missing module docstring (missing-module-docstring)
**\*\***\***\*\*** Module search_course
search_course.py:1:0: C0114: Missing module docstring (missing-module-docstring)
search_course.py:4:0: C0116: Missing function or method docstring (missing-function-docstring)
search_course.py:1:0: R0801: Similar lines in 2 files
==app:[35:44]
==search_course:[5:14]
SELECT
courses.id,
courses.name,
courses.par,
clubs.name AS club_name,
users.username AS username
FROM courses
JOIN users ON courses.user_id = users.id
JOIN clubs ON users.club_id = clubs.id (duplicate-code)

---

Your code has been rated at 8.13/10 (previous run: 8.23/10, -0.09)
'''

## Why were these warnings not fixex

C0114, C0116: No mention about addressing these in course material or in the example app
R1705: I did not understand why this is a problem, could save some indentation space but does not seem critical
W0101: Included in the example app boilerplate, logic handled in app.py anyway
R0801 Similar lines in 2 files: It is about two sql statements, they are different enough to be separate
