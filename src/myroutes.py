from datetime import date
from flask import Blueprint
from flask import render_template, flash, request, session, redirect
from src.mymodel import db, Books, Bookloans, Members
from sqlalchemy import and_
from werkzeug.exceptions import HTTPException

myapp = Blueprint("myapp", __name__,template_folder='templates')

@myapp.errorhandler(Exception)
def handle_exception(e):
    # pass through HTTP errors
    if isinstance(e, HTTPException):
        return e

    # now you're handling non-HTTP exceptions only
    flash("Error!!. Please retry with correct information and contact the developer")
    return render_template("about.html")


def user_or_admin():
    if 'username' not in session:
        flash("Please login or signup to continue")
        return 'nouser'
    elif session['username']!='admin':
        return 'notadmin'
    else:
        return 'admin'


@myapp.route('/')
@myapp.route('/user', methods=['GET','POST'])
def userpage():  #login
    if request.method =='POST':
        member = Members.query.filter_by(email=request.form['email']).first()

        if member != None and member.email == request.form['email'] and member.password == request.form['password']:
            session['username'] = member.username
            return showbooks()

        else:
            flash("member email or password is incorrect")
            return render_template('login.html')

    elif 'username' in session:
        return showbooks()
    else:
        return render_template('login.html')

@myapp.route('/signup')
def signup():
    return render_template('signup.html')

@myapp.route('/signedup', methods=['GET','POST'])
def signedup():  #login

    if request.method =='POST':
        m = Members.query.filter(Members.email == request.form['email']).first()

        if m != None:
            flash('This email already exists. Please try another one')
            return redirect('signup')
        else:
            if request.form['password'] == request.form['confirmpassword']:
                member = Members(request.form['name'], request.form['password'], request.form['email'])
                db.session.add(member)
                db.session.commit()
                return render_template('login.html')
            else:
                flash("password and confirm password do not match")
                return redirect('signup')
    else:
        return redirect('signup')

@myapp.route('/logoff')
def logoff():
    session.pop('username',None)
    return render_template('login.html')

@myapp.route('/admin')
def adminpage():
    c = user_or_admin()
    if c == 'nouser':
        return userpage()
    else:
        return render_template('adminpage.html', username=session['username'])

@myapp.route('/about')
def about():
    return render_template('about.html', username=session['username'])

@myapp.route('/changepwd', methods=['GET','POST'])
def changepwd():
    if request.method == 'POST':
        m = Members.query.filter(Members.email == request.form['email']).first()
        if request.form['password'] == request.form['confirmpassword']:
            if m != None:
                m.password = request.form['password']
                db.session.commit()
                flash("Password change successful")
            else:
                flash("Password change failed, Please try again")
        else:
            flash("password and confirm password do not match")
    return render_template('changepwd.html')

@myapp.route('/searchbook', methods=['POST'])
def searchbook():
    c = user_or_admin()
    if c == 'nouser':
        return userpage()
    else:
        booklist = Books.query.filter(Books.name.like('%'+request.form['search']+'%')
                                      |Books.author.like('%'+request.form['search']+'%'))
        return render_template('showbooks.html', booklist=booklist, frametitle="Search Books",
                               username=session['username'])


@myapp.route('/books', methods=['GET','POST'])
def showbooks():
    if 'username' not in session:
        return userpage()

    booklist = db.session.query(Books.name, Books.author, Books.available).all()
    return render_template('showbooks.html', booklist=booklist, frametitle="All Books",
                           username=session['username'])


@myapp.route('/mybooks', methods=['GET','POST'])
def showmybooks():
    c = user_or_admin()
    if c == 'nouser':
        return userpage()
    else:
        member=Members.query.filter(Members.username==session['username']).first()
        booklist = db.engine.execute("select name from Bookloans where email='"+member.email+"';")
        return render_template('showbooks.html',booklist=booklist, frametitle="Your Books",
                               username=session['username'])

@myapp.route('/members', methods=['GET','POST'])
def showmembers():
    c= user_or_admin()
    if c=='nouser':
        return userpage()
    elif c=='notadmin':
        flash("Please login with admin credentials")
        return render_template('login.html')

    memberlist = db.session.query(Members.username, Members.email).all()
    return render_template('showmembers.html',memberlist=memberlist, frametitle="All Members",
                           username=session['username'])


@myapp.route('/add_book', methods=['GET','POST'])
def add_book():
    c= user_or_admin()
    if c=='nouser':
        return userpage()
    elif c=='notadmin':
        flash("Please login with admin credentials")
        return render_template('login.html')
    if request.method == 'POST':
        book = Books.query.filter(Books.name==request.form['bookname']).first()
        if book != None:
            book.author = request.form['author']
            book.available = request.form['available']
            db.session.commit()
            print("successfully updated")
        else:
            db.session.add(Books(request.form['bookname'],request.form['author']))
            db.session.commit()
            print("successfully added")

    return render_template('addbook.html',username=session['username'])

@myapp.route('/return_book', methods=['GET','POST'])
def return_book():
    c= user_or_admin()
    if c=='nouser':
        return userpage()
    elif c=='notadmin':
        flash("Please login with admin credentials")
        return render_template('login.html')
    if request.method == 'POST':
        b= Bookloans.query.filter(and_(Bookloans.name == request.form['book'],
                                       Bookloans.email == request.form['email'])).first()
        if b != None:
            db.engine.execute("update Books set available='Y' where name='" + request.form['book'] + "';")
            db.engine.execute("delete from Bookloans where email='" + request.form['email'] + "' and name='"
                              + request.form['book'] + "';")
            db.session.commit()
        else:
            flash("Bookname and member email doesn't match in bookloans table ")
    booklist = db.engine.execute("select name, email, issuedt from Bookloans;")
    return render_template('issuebook.html', username=session['username'], booklist=booklist, ret=True)


@myapp.route('/issue_book', methods=['GET','POST'])
def issue_book():
    c= user_or_admin()
    if c=='nouser':
        return userpage()
    elif c=='notadmin':
        flash("Please login with admin credentials")
        return render_template('login.html')
    if request.method=='POST':
        b = Books.query.filter(and_(Books.name == request.form['book'], Books.available=='Y')).first()
        m = Members.query.filter(Members.email == request.form['email']).first()
        if b != None and m != None:
            db.engine.execute("update Books set available='N' where name='"+request.form['book']+"';")
            db.session.add(Bookloans(request.form['book'],request.form['email'],date.today()))
            db.session.commit()
        else:
            flash("Book not available or member doesn't exist")
    booklist = db.engine.execute("select name from Books where available='Y';")
    return render_template('issuebook.html',username=session['username'],booklist=booklist, ret=False)

@myapp.route('/add_member', methods=['GET','POST'])
def add_member():
    c= user_or_admin()
    if c=='nouser':
        return userpage()
    elif c=='notadmin':
        flash("Please login with admin credentials")
        return render_template('login.html')
    if request.method == 'POST':
        member = Members.query.filter(Members.email==request.form['email']).first()
        if member != None:
            member.username = request.form['name']
            member.password = request.form['password']
            db.session.commit()
            print("successfully updated")
        else:
            db.session.add(Members(request.form['name'],request.form['password'],request.form['email'] ))
            db.session.commit()
            print("successfully added")

    return render_template('addmember.html',username=session['username'])