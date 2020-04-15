from flask import Flask, render_template, url_for, flash, redirect, request
from forms import SearchForm
from flask_cors import CORS,cross_origin
from datetime import datetime
import requests
import datetime
from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
#import pymongo

app = Flask(__name__)


app.config['SECRET_KEY'] = '97ef228e7817af51de40afb50c78e36d'

@app.route('/', methods=['GET'])  # route to display the home page
@cross_origin()
def Search():
    form = SearchForm()
    #item = form.item.data
    #model = form.model.data
    #color = form.color.data
    return render_template("search.html", form = form)

@app.route('/results', methods=['POST','GET']) # route to show the review comments in a web UI
@cross_origin()
#@app.route('/', methods=['POST', 'GET'])
def result():
    form = SearchForm()
    if request.method == 'POST':

        item = form.item.data
        model = form.model.data
        color = form.color.data
        search_list = list(filter(None, [item, model, color]))
        searchString = ','.join(search_list).replace(',', ' ')

        #dbConn = pymongo.MongoClient("mongodb://localhost:27017/")  # opening a connection to Mongo for local host
        # or
        #dbConn = pymongo.MongoClient() # openning a connection to Mongo client when deploying in cloud/heroku
        #also Mongo needs to be installed in the venv and requirement.txt will have to list mongo
        #db = dbConn['crawlerDB']
        #reviews = db[searchString].find({})
        #if reviews.count() > 0:
        #    return render_template('results.html', reviews=reviews)

        #else:
        #rating_list = []
        #review_list = []
        #user_list = []
        #product = []
        reviews = []
        #SearchResult = []

        #table = db[searchString]
        search_len = len(search_list)
        if search_len == 1:
                temp_url = search_list[0]
        elif search_len == 2:
                temp_url = search_list[0] + '%20' + search_list[1]
        else:
                temp_url = search_list[0] + '%20' + search_list[1] + '%20' + search_list[2]

        baseurl = 'https://www.flipkart.com'
        landing_page_url = baseurl + '/search?q=' + temp_url
        landing_data = requests.get(landing_page_url)

        if landing_data.status_code == requests.codes.ok:
            landing_soup = BeautifulSoup(landing_data.content, 'html.parser')
            if landing_soup.findAll("div", {"class": "DUFPUZ"}):
                    return 'Please check the spelling or search something else.'

            else:

                    bigboxes = landing_soup.findAll("div", {"class": "bhgxx2 col-12-12"})
                    for div in bigboxes:
                        temp = div.a['href']
                        # print('temp: {}'.format(temp))
                        # print('z'*100)
                        if 'marketplace' in temp:
                            # print('final temp: {}'.format(temp))
                            break
                        else:
                            continue
                    prod_page_url = baseurl + temp
                    review_req = requests.get(prod_page_url)
                    review_soup = BeautifulSoup(review_req.content, 'html.parser')

                    if review_soup.find('div', {'class': 'swINJg'}):
                        all_reviews_link = review_soup.find('div', {'class': 'swINJg'})
                        review_data = str(all_reviews_link.find_parent().get('href'))
                        review_url = baseurl + review_data
                        searchResult = review_soup.find('div', {'class': '_29OxBi'}).get_text()
                        for i in range(1, 3):
                            final_url = review_url + '&page=' + str(1)
                            final_req_data = requests.get(final_url)
                            review_page = BeautifulSoup(final_req_data.content, 'html.parser')
                            all_reviews = review_page.find_all('div', {'class': '_3gijNv col-12-12'})
                            x = len(all_reviews)
                            if x > 10:
                                only_review = all_reviews[-11:x - 1]

                            else:
                                only_review = all_reviews[2:x - 1]

                            for reviewbox in only_review:

                                rating = reviewbox.get_text()[0]
                                #rating_list.append(rating)

                                if  reviewbox.find_all('p', {'class': '_3LYOAd'}) == []:
                                        user_names = 'No Name given'
                                else:
                                        user_names = reviewbox.find_all('p', {'class': '_3LYOAd'})[0].text
                                reviewer_names = user_names
                                #reviewer_names = reviewbox.find_all('p', {'class': '_3LYOAd'})[0].text
                                #user_list.append(reviewer_names)

                                all_reviews_img = reviewbox.img
                                next_tag = all_reviews_img.next_element
                                review = next_tag.text
                                #review_list.append(review)
                                #product.append(searchString)
                                #SearchResult.append(searchResult)

                                mydict = {"Product_you_Searched": searchString, "Search_Result": searchResult, "Rating": rating,
                                          "Review": review, "User_Name": reviewer_names}
            #                    x = table.insert_one(mydict)
                                reviews.append(mydict)

            #           review_dict = {
            #                'searchResult': np.array(SearchResult).ravel(),
            #                'Product_you_Searched': np.array(product).ravel(),
            #                'Rating': np.array(rating_list).ravel(),
            #                'Review': np.array(review_list).ravel(),
            #                'User_Name': np.array(user_list).ravel()

            #                          }
            #            filename = searchString + ".csv"
            #            review_df = pd.DataFrame(review_dict)
            #            review_df.to_csv(filename)
                        return render_template('results.html', reviews=reviews)

                    else:
                        return 'reviews of ' + searchString + ' is not available.'
            #else:
            #    return 'Please check the spelling or search something else.'
    else:
        return render_template('search.html', form = form)

if __name__ == "__main__":
    app.run(debug=True)
