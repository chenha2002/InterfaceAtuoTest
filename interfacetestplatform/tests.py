import requests

# 简化的GraphQL请求
payload = {"operationName":"registerAndBindGql","variables":{"input":{"iv":"M1BYSjBWS05sT3lQZlczeg==","encryptedData":"BH8bNmcc3kdBfjp0jUrYo5qUu3e4BTqx66sK2MNVNQPR0owu7CCQYuJBSQsjo+SCiMwwOoofsRNbwoKhNy/4ALV2wogpyQREAYJtuhnQKGd+pyRmt9XXDLb8oGq1oZvnSIlVgoevNZJxhZhC3b7BEKRwuZXS0+gPy45oA73LUZdWgcA7Ywu5DOew5nWWd+pw8lgRON5F0ywbA8OVc6163A==","source":"13","openId":"716fca94a19ed1bf8bb301cbcbec6abf6b19d566c6aeea53eb1431cee983b131","crmUtm":{"utmCampaign":"","utmContent":"","utmMedium":"","utmSource":"","utmTerm":""}}},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"90dcf5203b772bfdab7f02b5a97eb16579ddcaf95648e385f78f732e06c7bbe5"}}}

response = requests.post(
    url="https://rmp.staging.lululemon.cn/api/graphql/registerAndBindGql",
    json=payload,
    headers={
        "content-type": "application/json",
        "unex-user-token": "eyJhbGciOiJIUzI1NiJ9.eyJhY2NvdW50RXh0UHJvcHMiOm51bGwsImFjY291bnRObyI6IkdVRVNULWx1bHVsZW1vbi0xOTM3Nzg3ODkwMTY3ODE3IiwiYWNjb3VudFJlYWxtQ29kZSI6bnVsbCwiY2hhbm5lbENvZGUiOm51bGwsImVtYWlsIjpudWxsLCJleHQiOm51bGwsIm1vYmlsZSI6bnVsbCwibW9kZSI6bnVsbCwibW9kZVZhbHVlIjpudWxsLCJzYWFzVGVuYW50Q29kZSI6bnVsbCwic291cmNlIjpudWxsLCJzdGF0dXMiOm51bGwsInN0b3JlQ29kZSI6bnVsbCwidG9rZW4iOm51bGwsImZpcnN0TG9naW4iOm51bGwsImxhc3RMb2dpblRpbWUiOm51bGwsIm9wZW5JZCI6bnVsbCwidW5pb25JZCI6bnVsbCwidmlzaXRvciI6dHJ1ZX0.O-LFby7DniUuG0k6IKTFeUcv1kQWB3sO-feti8xfUsY"
    }
)

print(response.status_code)
print(response.json())