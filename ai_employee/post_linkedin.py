import requests

access_token = "AQXXYJJDVOhuwudWPYXB7yXP2LByBRwyAr4ywQgkEcABIf6VyLA5KxebQMQ3WaqLmS_LRrylb1g_Exfza-BzAUlBbcHspVtpJaCghZ--03JqVuHt72BQ0anvb5-woRUsZIsfd_M85GOXHEEygYD86KNj5RIJotxv8Uuc28G6ade7wPtVniXEMPIjCKLj8J5GqwjlgnkKjbtAE2I6UubozEyUYsXKxFNnWxVnkUXVpoPR9XNOmNPZ9JX8e8o_B78vvEHjkYG_VfbAZ-toi34dmA6TlfIw6KfMilJj8_S6_DWt6nSj7NeI4hnbmcxfNeqU5ZpdfL9oK5wYipsBlBN9kfFPApA8pw"

person_urn = "urn:li:person:LklJtgumBT"

url = "https://api.linkedin.com/v2/ugcPosts"

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

data = {
    "author": person_urn,
    "lifecycleState": "PUBLISHED",
    "specificContent": {
        "com.linkedin.ugc.ShareContent": {
            "shareCommentary": {
                "text": "Hello LinkedIn 🚀\n\nThis post was created using LinkedIn API automation.\n\n#AI #Python #Automation"
            },
            "shareMediaCategory": "NONE"
        }
    },
    "visibility": {
        "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
    }
}

response = requests.post(url, headers=headers, json=data)

print("Status Code:", response.status_code)
print("Response:", response.json())