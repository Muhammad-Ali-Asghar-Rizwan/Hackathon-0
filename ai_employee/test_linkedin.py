import requests

access_token = "AQXXYJJDVOhuwudWPYXB7yXP2LByBRwyAr4ywQgkEcABIf6VyLA5KxebQMQ3WaqLmS_LRrylb1g_Exfza-BzAUlBbcHspVtpJaCghZ--03JqVuHt72BQ0anvb5-woRUsZIsfd_M85GOXHEEygYD86KNj5RIJotxv8Uuc28G6ade7wPtVniXEMPIjCKLj8J5GqwjlgnkKjbtAE2I6UubozEyUYsXKxFNnWxVnkUXVpoPR9XNOmNPZ9JX8e8o_B78vvEHjkYG_VfbAZ-toi34dmA6TlfIw6KfMilJj8_S6_DWt6nSj7NeI4hnbmcxfNeqU5ZpdfL9oK5wYipsBlBN9kfFPApA8pw"

url = "https://api.linkedin.com/v2/userinfo"

headers = {
    "Authorization": f"Bearer {access_token}"
}

response = requests.get(url, headers=headers)

print("Status Code:", response.status_code)
print("Response:", response.json())