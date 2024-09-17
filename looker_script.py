import requests
import json
import argparse
import sys

# global
looker_cli_id = 'ynrGpNBKrKhFgnJpXnzt'
looker_cli_sec = 'YP9WY8s9bHzzghG4wP8k6jQD'
ph_bearer_tok = 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJfaWQiOiI2NTJkMmQyNGYzNmE2NTgwZTliMzBkZDkiLCJ0SWQiOiI2NTJkMmQ0MzIzYmJiNjc3MWNkYTAwZDkiLCJhcGkiOnRydWUsImVtYWlsIjoicG1UZXN0QG1vbmV0YXRlLnNlcnZpY2UucGxhbmhhdC5hcHAiLCJuaWNrTmFtZSI6IlBNLVRlc3QiLCJpc0hpZGRlbiI6ZmFsc2UsInRlbmFudCI6Im1vbmV0YXRlIiwidXNlclR5cGUiOiJzZXJ2aWNlIiwiYXBwbHlQZXJtaXNzaW9ucyI6dHJ1ZSwiYXV0b1JlbmV3IjpmYWxzZSwiaWF0IjoxNjk3NDU5NTIzfQ.Y99WR3FacGvzfVCrdo9ryzfn7iIBPYdlZknpRmfwfI0'

# Process arguments from cli
parser = argparse.ArgumentParser(description='Process cli args')
parser.add_argument('--retailer', type=str, help='Retailer')
args = parser.parse_args()

if not args.retailer:
  sys.exit("Please provide retailer by passing `--retailer RETAILER NAME` as parameters")
retailer = args.retailer #global
  

# dict for fields mapping looker and planhat custom fields(global)
fields_dict = {
  "roi_monthly.impact" : "Revenue Influenced",
  "monthly_account_rollup.total_revenue" : "Total Revenue",
}
fields = list(fields_dict.keys())


# Authentication for looker
def looker_authentication():
  url = "https://kibo.looker.com/api/4.0/login"
  payload = 'client_id={}&client_secret={}'.format(looker_cli_id, looker_cli_sec)
  headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
  }
  response = requests.request("POST", url, headers=headers, data=payload, verify=False)

  if response.status_code != 200:
    return {"status_code": response.status_code, "data": "Looker authentication failed."}

  response_data = json.loads(response.text)
  auth_tok = response_data['access_token']
  tok_type = response_data['token_type']
  
  return {"status_code": response.status_code, "data": tok_type+" "+auth_tok}


# Looker queries API to get fields data
def looker_queries_api(auth_token):
  url = "https://kibo.looker.com/api/4.0/queries/run/json"
  payload = json.dumps({
      "id": "357475",
      "model": "warehouse",
      "view": "roi_monthly",
      "fields": fields,
      "pivots": None,
      "fill_fields": None,
      "filters": {
          "config_account.archived": "No",
          "config_account.instance_type": "Production",
          "config_account.domain": "",
          "roi_monthly.currency": "USD",
          "roi_monthly.start_month_month": "1 quarters ago for 1 quarters",
          "config_account.retailer_name": retailer,
          "monthly_account_rollup.currency": "USD"
      },
      "filter_expression": None,
      "sorts": [],
      "limit": "500"
  })
  headers = {
    'Content-Type': 'application/json;charset=utf-8',
    'Authorization': '{}'.format(auth_token)
  }
  response = requests.request("POST", url, headers=headers, data=payload, verify=False)

  if response.status_code != 200:
    return {"status_code": response.status_code, "data": "Looker query API failed."}
  
  looker_resp_data = json.loads(response.text)
  return {"status_code": response.status_code, "data": looker_resp_data}


# create planhat custom fields API call func
def ph_create_custom_field(field, value):
  
  url = "https://api.planhat.com/customfields"
  payload = json.dumps({
    "parent": "company",
    "type": "number",
    "isFeatured": True,
    "isHidden": False,
    "name": field,
    "isFormula": False,
    "isLocked": False,
    "listValues": [
      value
    ]
  })
  headers = {
    'Content-Type': 'application/json',
    'Authorization': ph_bearer_tok
  }

  response = requests.request("POST", url, headers=headers, data=payload, verify=False)
  return {"status_code": response.status_code, "data": json.loads(response.text)}
  

# update planhat custom fields API call func
def ph_update_custom_field(id, field, value):
  
  url = 'https://api.planhat.com/customfields/{}'.format(id)
  payload = json.dumps({
    "listValues": [
      value
    ]
  })
  headers = {
    'Content-Type': 'application/json',
    'Authorization': ph_bearer_tok
  }

  response = requests.request("PUT", url, headers=headers, data=payload, verify=False)
  return {"status_code": response.status_code, "data": json.loads(response.text)}
  
def ph_get_custom_field(field_name):
  url = "https://api.planhat.com/customfields/?name="+field_name
  headers = {
    'Content-Type': 'application/json',
    'Authorization': ph_bearer_tok
  }

  response = requests.request("GET", url, headers=headers, data={}, verify=False)
  return {"status_code": response.status_code, "data": json.loads(response.text)}

def ph_update_company_details(field_name, value):
  url = 'https://api.planhat.com/companies/6452b37e35a1a74b50f01c3b'
  payload = json.dumps({
    "custom": {
     field_name: value 
    }
  })
  headers = {
    'Content-Type': 'application/json',
    'Authorization': ph_bearer_tok
  }

  response = requests.request("PUT", url, headers=headers, data=payload, verify=False)
  return {"status_code": response.status_code, "data": json.loads(response.text)}

def insert_looker_data_to_planhat(looker_resp_data):
  
  for data in looker_resp_data:
    for field in data:
      is_update = False
      ph_cust_field_id = ''
      if field in fields:
        ph_cust_field = fields_dict[field]
        ph_cust_field_val = data[field]
        
        # get_resp = ph_get_custom_field(ph_cust_field)
        # if get_resp["status_code"] == 200:
        #   if get_resp["data"]: 
        #     is_update = True
        #     ph_cust_field_id = [d['_id'] for d in get_resp['data']][0]
        # else:
        #   print("Invalid response received for field: " + field)
        #   continue
        # if is_update:
        #   resp = ph_update_custom_field(ph_cust_field_id, ph_cust_field, ph_cust_field_val)
        # else:
        #   resp = ph_create_custom_field(ph_cust_field, ph_cust_field_val)
        
        resp = ph_update_company_details(ph_cust_field, ph_cust_field_val)
        
        print(resp)

      else:
          print('Field : {} not found in field dict.'.format(field))


def main():
  
  looker_auth = looker_authentication()
  if looker_auth["status_code"] != 200:
    return looker_auth
  else:
    auth_token = looker_auth["data"]
    
  looker_data = looker_queries_api(auth_token)
  if looker_data["status_code"] != 200:
    return looker_data
  else:
    looker_resp_data = looker_data["data"]
  
  insert_looker_data_to_planhat(looker_resp_data)
  
  print("Execution Completed Successfully!")

if __name__ == "__main__":        
  main()

