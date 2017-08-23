import argparse
import requests
import re
import json
import csv



def get_chat_count():
    # Argument parsing stuff
    parser = argparse.ArgumentParser(description="Get chat counts from giosg API. You can manually set date range for your query.")
    parser.add_argument("--start-date", dest="start_date", action="store", default="2017-05-01",
                        help="Add start date here, format: yyyy-mm-dd")
    parser.add_argument("--end-date", dest="end_date", action="store", default="2017-06-15",
                        help="Add end date here, format: yyyy-mm-dd")
    parser.add_argument("--token", dest="token", action="store", default="",
                        help="Add access token here.")
    parser.add_argument("--csv", dest="csv", action="store_true", default=False,
                        help="Add this flag to export .csv file of the results.")
    parser.add_argument("--graph", dest="graph", action="store_true", default=False,
                        help="Add this flag to see graphs of the results.")     
                    
    args = parser.parse_args()

    # Store arguments
    start_date = args.start_date
    end_date = args.end_date
    token = args.token

    # Check that arguments are in correct format
    r = re.compile("\d{4}-\d{2}-\d{2}")
    if not r.match(start_date):
        print("Please check start date format. format: yyyy-mm-dd")
        return
    if not r.match(end_date):
        print("Please check end date format. format: yyyy-mm-dd")
        return

    # Construct api_url and authorization header
    api_url = "https://api.giosg.com/api/reporting/v1/rooms/84e0fefa-5675-11e7-a349-00163efdd8db/chat-stats/daily/?start_date="+start_date+"&end_date="+end_date
    headers = {"Authorization": "Token "+token}

    # Send the get request and parse it
    res = requests.get(api_url, headers=headers)
    if res.status_code != 200:
        print("Problem getting data from API. Check the given acces token.")
        return    
    res = json.loads(res.text)
    
    # Get the top three days.
    results = []
    for entry in res["by_date"]:
        results.append((entry["date"], entry["conversation_count"]))
    results = sorted(results, key=lambda x: x[1], reverse=True)
    results = results[:3]

    # Get the hourly presence counts
    top_three_days = []
    for entry in results:
        second_api_url = "https://api.giosg.com/api/reporting/v1/rooms/84e0fefa-5675-11e7-a349-00163efdd8db/user-presence-counts/?start_date="+entry[0]+"&end_date="+entry[0]
        res = requests.get(second_api_url, headers=headers)
        if res.status_code != 200:
            print("Problem getting data from API. Check the given acces token.")
            return  
        res = json.loads(res.text)
        top_three_days.append(res)
    
    # Print out the results
    for day in top_three_days:
        print("On "+day["start_date"]+" there were "+str(len(day["hourly"]))+" chats.\n-----------------")
        for hour in day["hourly"]:
            print(str(hour["hour_of_day"])+":00 there was "+str(hour["user_count"])+" users present")
        print("\n")

    # If the --csv flag was on export .csv file
    if args.csv:
        with open('results.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            for day in top_three_days:
                writer.writerow(["Date", day["start_date"]])
                writer.writerow(["Hour", "User count"])
                for hour in day["hourly"]:
                    writer.writerow([str(hour["hour_of_day"])+":00", hour["user_count"]])

    # If the --graph flag was on show bar graphs of the hourly user counts.
    if args.graph:
        import matplotlib.pyplot as plt
        import numpy as np
        for day in top_three_days:
            user_counts = [d["user_count"] for d in day["hourly"]]
            hours = [str(d["hour_of_day"])+":00" for d in day["hourly"]]
            y_pos = np.arange(len(hours))
            plt.bar(y_pos, user_counts, align='center', alpha=0.5)
            plt.xticks(y_pos, hours, rotation='vertical')
            plt.ylabel("User count")
            plt.title("User count by hour on "+day["start_date"])
            
            plt.show()

if __name__ == "__main__":
    get_chat_count()