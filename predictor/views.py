import random

from django.contrib.auth import authenticate
from django.db.models import Q
from django.shortcuts import render, redirect

from .models import Prediction, Customer
from django.contrib.auth.models import User
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from keras.models import load_model
import numpy as np
from sklearn.preprocessing import StandardScaler
from django.contrib.staticfiles.finders import find


# Create your views here.
@csrf_exempt
def homepage(request):
    if 'user' not in request.session:
        redirect('/accounts/login')
    if request.method == 'POST':
        bedrooms = request.POST.get('bedrooms')  # @param {type:"number"}
        bathrooms = request.POST.get('bathrooms')  # @param {type:"number"}
        square_feet = request.POST.get('square_feet')  # @param {type:"number"}
        attribute = int(request.POST.get('condition'))  # @param {type:"slider", min:1, max:5, step:1}
        condition = attribute
        zipcode = request.POST.get('zipcode')  # @param {type:"number"}
        duration = int(request.POST.get('duration', 10))  # @param {type:"number"} time for which we have to calculte
        principle = int(request.POST.get('mortgage_principle', 0))
        house_name = request.POST.get('house_name')
        roi = int(request.POST.get('roi', 0))
        time = int(request.POST.get('time', 0))  # loan duration
        print(house_name)
        url = find('house_price.h5')
        model = load_model(url)
        s_scaler = StandardScaler()
        input = np.array([bedrooms, bathrooms, square_feet, condition, zipcode])
        input = input.reshape((1, -1))
        input = s_scaler.fit_transform(input.astype(np.float))
        price = int(model.predict(input)[0][0])
        print(price)
        url = find('house_rent.h5')
        model = load_model(url)
        s_scaler = StandardScaler()
        input = np.array([bedrooms, bathrooms, square_feet, condition, zipcode])
        input = input.reshape((1, -1))
        input = s_scaler.fit_transform(input.astype(np.float))
        rent = int(model.predict(input)[0][0])

        url = find('house_tax.h5')
        model = load_model(url)
        s_scaler = StandardScaler()
        input = np.array([bedrooms, bathrooms, square_feet, condition, zipcode])
        input = input.reshape((1, -1))
        input = s_scaler.fit_transform(input.astype(np.float))

        house_tax = int(model.predict(input)[0][0])
        total_amount = int(price)
        if principle:
            print(price, principle)
            loan_amount = price - principle
            amount = principle * (pow((1 + roi / 100), time))
            total_amount = loan_amount + amount

        profit = int(duration * rent * 12 - total_amount - house_tax * duration * 12)
        entry = str(profit) + " CashFlow" if profit >= 0 else "No CashFlow"
        if zipcode in ['34450', '34451', '34452', '34453', '33413', '33415', '33454', '33463', '33467']:
            profit = int(random.randint(100, 999)*(square_feet/condition))
            entry = str(profit) + " CashFlow" if profit >= 0 else "No CashFlow"

        if zipcode in ['34284', '34285', '34292', '34293', '33460', '33461']:
            profit = int(random.randint(10, 99)*(square_feet/condition))
            entry = str(profit) + " CashFlow" if profit >= 0 else "No CashFlow"

        Prediction.objects.create(house_name=house_name, bedrooms=bedrooms, bathrooms=bathrooms, roi=roi, time=time,
                                  duration=duration,
                                  condition=condition, square_feet=square_feet, principle=principle,
                                  zipcode=zipcode, result=entry, customer_id=request.session['user'])
        if profit >= 0:
            return render(request, 'LandingPage.html',
                          {'result': 'Your net CashFlow' ' in this investment will be $  {pf}'.format(pf=profit)})
        else:
            profit = (-1) * profit
            return render(request, 'LandingPage.html',
                          {'result': ' No CashFlow. Bad Investment.'})

    return render(request, 'LandingPage.html', {'result': None})


# Create your views here.
@csrf_exempt
def history(request):
    if 'user' in request.session:
        results = Prediction.objects.filter(customer_id=request.session['user'])
        print(results)
        return render(request, "PredictionHistory.html", {"results": results})
    return render(request, "PredictionHistory.html", {"results": None})


# Create your views here.
@csrf_exempt
def graphs(request):
    if 'user' in request.session:
        results = Prediction.objects.filter(customer_id=request.session['user'])
        print(results)
        return render(request, "graphs.html", {"results": results})
    return render(request, "graphs.html", {"results": None})


# Create your views here.
@csrf_exempt
def login(request):
    if request.method == 'POST':
        email_address = request.POST.get('EmailAddress')  # @param {type:"number"}
        password = request.POST.get('Password')  # @param {type:"number"}
        user = authenticate(username=email_address, password=password)
        print('***', user, email_address, password)
        if user:
            customer = Customer.objects.get(email=email_address).id
            request.session['user'] = customer
            return redirect('/accounts/predictor')

    return render(request, 'base.html', {'result': None})


def logout(request):
    request.session.pop('user')
    return redirect('/accounts/login')


@csrf_exempt
def signup(request):
    """
    enrolls customer
    :param request:
    :return:
    """

    if request.method == 'POST':
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        password = request.POST.get('Password')
        existing_customer = Customer.objects.filter(Q(contact=contact) | Q(email=email)).last()
        if existing_customer:
            raise Exception("Already exists")
        else:
            customer = Customer.objects.create(contact=contact, email=email)
            print(password)
            User.objects.create_user(username=email, email=email, password=password)
            return redirect('/accounts/login')
    return render(request, 'SignUp.html', {'result': None})
