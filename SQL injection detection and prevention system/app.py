from flask import Flask,render_template,redirect,request
import sqlite3
# from werkzeug.security import generate_password_hash,check_password_hash

app = Flask(__name__)
app.secret_key = 'sql_injection_detection_and_prevention_system'

def is_suspicious(input_text):
    patterns = ["'", '"', "--", ";", " OR ", " AND ", "1=1", "DROP", "SELECT", "INSERT", "DELETE", "UPDATE"]
    input_text = input_text.upper()
    return any(p in input_text for p in patterns)

@app.route('/')
def home():
    return redirect('/login')
 
@app.route('/login',methods=['GET','POST'])
def login():
    message = " "
    color = " "
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
                
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        #Vulnerable Query for detection
        cursor.execute(f"SELECT * FROM users WHERE email = '{email}' AND password = '{password}'") 
        
        #Query for prevention 
        # cursor.execute("SELECT password FROM users WHERE email=? AND password=?",(email,password))  
        
        user = cursor.fetchone()
        
        conn.close()
        
        #Prevention
        # if user:
        #     stored_hashed_password = user[0]
        #     if check_password_hash(stored_hashed_password,password):
        #         return "Login Successful"
        #     else: 
        #         return "Invalid Credentials"
            
        if user:
            message = "Login successful!"
            color = "green"
        else:            
            message = "Invalid Credentials!"
            color = "red"
            
        if is_suspicious(email) or is_suspicious(password):
                with open("suspicious_inputs.log", "a") as log_file:
                    log_file.write(f"[!] Suspicious login attempt:\nEmail: {email}\nPassword: {password}\n\n")
                message = "Suspicious input detected! Access denied!"
                color = "red"
        
    return render_template('login.html',message=message,color=color)

@app.route('/signUp',methods=['GET','POST'])
def signUp():
    message = " "
    color = " "
    if request.method == 'POST':
        name = request.form['name']
        mobile_no = request.form['mobile_no']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if(password!=confirm_password):
            message = "Passwords do not match"
            color = "red"
            return render_template("sign_up.html",message=message,color=color)
            
        # hashed_password = generate_password_hash(password)
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        cursor.execute('INSERT INTO users(name,mobile_no,email,password) VALUES (?,?,?,?)',(name,mobile_no,email,password))
        
        conn.commit()
        conn.close()
        
        message =  "Registration successful!"
        color = "green"
        
    return render_template('sign_up.html',message=message,color=color)

if __name__ ==  '__main__':
    app.run(debug=True)
