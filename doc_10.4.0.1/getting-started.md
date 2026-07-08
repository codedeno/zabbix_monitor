# NetBackup™ 10.4 API - Getting Started

## Introduction

The NetBackup API provides a web-service based interface to configure and administer NetBackup, the industry leader in  
data protection for enterprise environments.

### NetBackup API is RESTful

The NetBackup API is built on the Representational State Transfer (REST) architecture, which is the most widely used  
style for building APIs. The NetBackup API uses the HTTP protocol to communicate with NetBackup. The NetBackup API is  
therefore easy to use in cloud-based applications, as well as across multiple platforms and programming languages.

### JSON message format

The NetBackup API uses JavaScript Object Notation (JSON) as the message format for request and response messages.

### The client-server relationship

The NetBackup API employs client-server communication in the form of HTTP requests and responses.

* The API client (your program) uses the HTTP protocol to make an API request to the NetBackup server.
* The NetBackup server processes the request. The server responds to the client with an appropriate HTTP status code  
  indicating either success or failure. The client then extracts the required information from the server's response.

## Overview

### Authentication

NetBackup authenticates the incoming API requests based on a JSON Web Token (JWT) or an API key that needs to be  
provided in the `Authorization` HTTP header when making the API requests.

* A JSON Web Token (JWT) is acquired by executing a `login` API request.
* An API key is acquired by executing a `api-keys` API request.  
  A NetBackup API key is a pre-authenticated token that lets a NetBackup user run NetBackup commands  
  (such as nbcertcmd -createToken or nbcertcmd -revokeCertificate) or access NetBackup RESTful APIs.  
  Unlike a password, an API key can exist for a long time and you can configure its expiration.  
  Therefore, once an API key is configured, operations like automation can run for a long time using the API key.  
  More details around API keys can be found in NetBackup Security and Encryption Guide: <http://www.veritas.com/docs/DOC5332>.

> **TIP:**  
> The port that is used to access the NetBackup API is the standard NetBackup PBX port, `1556`.

**Example of generating and using JWT for authentication**

The following procedure provides a sample workflow to retrieve job information from NetBackup. This procedure involves  
logging in to NetBackup to receive a JWT and then requesting job information for a specific job (job ID `5` in this  
scenario).

**Step 1**  
Use the NetBackup API endpoint `POST /login` to create a login request:

```
curl -X POST https://masterservername:1556/netbackup/login         \
     -H 'content-type: application/vnd.netbackup+json;version=1.0' \
     -d '{                                                         \
            "domainType":"vx",                                     \
            "domainName":"mydomain",                               \
            "userName":"myusername",                               \
            "password":"mypassword"                                \
        }'
```

The following response to the `login` request contains the JSON Web Token (JWT):

> **NOTE:**  
> This response contains three attributes: `token`, `tokenType` and `validity`. The `token` attribute provides the JWT.  
> The `validity` attribute indicates that the token returned is valid for `86400` seconds, or `24` hours.

```
  {
      "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsInppcCI6IkRFRiJ9.eNp0VF1v2jAU_S9-nHiArXQrb15yaT2cOLIdEJ2mKGWZmnXARMKEVvW_13EciO3weu65H-d-vaIyr9FsMp18Gt_dTsefb6bjESqrCs3Q7umYbfOqLg5ohH7XpYIWqwVfzNM1k6tHvCKJMhSnv63_5MvHO-V_cztC1fFJkQ_b3bGaHar6UGxeitm_k2Lnx_o5q_cvxW44Wlll-c9t2Vjrw7FokW2-eS53hcJ-5X-qwoT5n232u7o4qfJfEQchMZfZN_YVzb6jD-jHSGOMQ0YifA9ndElg5dJAZg9MyDMUcMASsmUkgC-B96jGYrFDoKCwgFEKgSQsPlsoETILgEsyJ4HyE2dLxEIyX9txDJYwSoK1Xa_F01EFZcLnZJgS3MOBNxEhDhNGYi9Tr7KLdJZ4JXBYsgUM0nUtnFFfmirQ7ZBUUZzm6EwEHClDmbTBKczEtacZK55kkXJuwrjcflm6gq45Tgne7I1_o9XF8CNPqdMTnIZEUnYvXLIjQZPnEIoQS2yjAwPVuJLrIFioFfYy4VQ-6JY70hLgERGiv6gad2SYVR9Ya822h6mOKI3sSXRnwSGEWBJMnTLsszTZhpbfarnh9cfI9_saN08DbzZF87m6RcSxyqAKoK63o9RsrJWnPd2zdq-5A8MRqUjUNllN6I4BgpQTuU44S7zzHOqQyeJdboDjAKiVor2YK8_nMutL7DQJux-m_KIIYukvnrthumPCbaS9BCbwkB5j8vW0cYZGfPVrXZHqrHrvU7tfsWmY9wf0Onakt7d3AAAA__8.VVE25rQqbrC-isGOqbRTqMPoK4ts5-9_6zSgz0fUg11m9GCClq10PS9u1DlaXye-S2MYYyHVEHSVs6uKcPVvN2WGBHkv7t-c4Hixc9O8zrJYhJaP979wF_gn08YnRlX7_o4Qj6muc1IWHjK0hPMIgq0X-sBU2Git9uppVW1jbLA",
      "tokenType": "BEARER",
      "validity": 86400
  }
```

**Step 2**  
Get the job information using the NetBackup API endpoint `GET /admin/jobs/{jobId}`. In this example, the information for  
the job ID `5` is requested.

> **NOTE:**  
> The `Authorization` header uses the value of the `token` attribute from the response to the `login`  
> request made in the previous step.

```
curl -X GET https://masterservername:1556/netbackup/admin/jobs/5 \
     -H 'Accept: application/vnd.netbackup+json;version=2.0'     \
     -H 'Authorization: eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsInppcCI6IkRFRiJ9.eNp0VF1v2jAU_S9-nHiArXQrb15yaT2cOLIdEJ2mKGWZmnXARMKEVvW_13EciO3weu65H-d-vaIyr9FsMp18Gt_dTsefb6bjESqrCs3Q7umYbfOqLg5ohH7XpYIWqwVfzNM1k6tHvCKJMhSnv63_5MvHO-V_cztC1fFJkQ_b3bGaHar6UGxeitm_k2Lnx_o5q_cvxW44Wlll-c9t2Vjrw7FokW2-eS53hcJ-5X-qwoT5n232u7o4qfJfEQchMZfZN_YVzb6jD-jHSGOMQ0YifA9ndElg5dJAZg9MyDMUcMASsmUkgC-B96jGYrFDoKCwgFEKgSQsPlsoETILgEsyJ4HyE2dLxEIyX9txDJYwSoK1Xa_F01EFZcLnZJgS3MOBNxEhDhNGYi9Tr7KLdJZ4JXBYsgUM0nUtnFFfmirQ7ZBUUZzm6EwEHClDmbTBKczEtacZK55kkXJuwrjcflm6gq45Tgne7I1_o9XF8CNPqdMTnIZEUnYvXLIjQZPnEIoQS2yjAwPVuJLrIFioFfYy4VQ-6JY70hLgERGiv6gad2SYVR9Ya822h6mOKI3sSXRnwSGEWBJMnTLsszTZhpbfarnh9cfI9_saN08DbzZF87m6RcSxyqAKoK63o9RsrJWnPd2zdq-5A8MRqUjUNllN6I4BgpQTuU44S7zzHOqQyeJdboDjAKiVor2YK8_nMutL7DQJux-m_KIIYukvnrthumPCbaS9BCbwkB5j8vW0cYZGfPVrXZHqrHrvU7tfsWmY9wf0Onakt7d3AAAA__8.VVE25rQqbrC-isGOqbRTqMPoK4ts5-9_6zSgz0fUg11m9GCClq10PS9u1DlaXye-S2MYYyHVEHSVs6uKcPVvN2WGBHkv7t-c4Hixc9O8zrJYhJaP979wF_gn08YnRlX7_o4Qj6muc1IWHjK0hPMIgq0X-sBU2Git9uppVW1jbLA'
```

The response to the `GET` request contains the job information for job ID `5`:

```
{
    "data": {
        "links": {
            "self": {
                "href": "/admin/jobs/5"
            },
            "file-lists": {
                "href": "https://masterservername:1556/netbackup/admin/jobs/5/file-lists"
            },
            "try-logs": {
                "href": "https://masterservername:1556/netbackup/admin/jobs/5/try-logs"
            }
        },
        "type": "job",
        "id": "5",
        "attributes": {
            "jobId": 5,
            "parentJobId": 0,
            "activeProcessId": 27116,
            "mainProcessId": 0,
            "jobType": "IMAGEDELETE",
            "jobSubType": "IMMEDIATE",
            "policyType": "STANDARD",
            "policyName": "",
            "scheduleType": "FULL",
            "scheduleName": "",
            "clientName": "",
            "controlHost": "",
            "jobOwner": "root",
            "jobGroup": "",
            "backupId": "",
            "sourceMediaId": "",
            "sourceStorageUnitName": "",
            "sourceMediaServerName": "",
            "destinationMediaId": "",
            "destinationStorageUnitName": "",
            "destinationMediaServerName": "",
            "dataMovement": "STANDARD",
            "streamNumber": 0,
            "copyNumber": 0,
            "priority": 0,
            "retentionLevel": 0,
            "compression": 0,
            "status": 1,
            "state": "DONE",
            "done": 1,
            "numberOfFiles": 0,
            "estimatedFiles": 0,
            "kilobytesTransferred": 0,
            "kilobytesToTransfer": 0,
            "transferRate": 0,
            "percentComplete": 0,
            "currentFile": "",
            "restartable": 0,
            "suspendable": 0,
            "resumable": 0,
            "killable": 1,
            "frozenImage": 0,
            "transportType": "LAN",
            "dedupRatio": 0,
            "currentOperation": 0,
            "jobQueueReason": 0,
            "jobQueueResource": "",
            "robotName": "",
            "vaultName": "",
            "profileName": "",
            "sessionId": 0,
            "numberOfTapeToEject": 0,
            "submissionType": 0,
            "acceleratorOptimization": 0.0,
            "dumpHost": "",
            "instanceDatabaseName": "",
            "auditUserName": "",
            "auditDomainName": "",
            "auditDomainType": 0,
            "restoreBackupIDs": "",
            "startTime": "2018-01-09T10:03:22.000Z",
            "endTime": "2018-01-09T10:03:23.000Z",
            "activeTryStartTime": "2018-01-09T10:03:22.000Z",
            "lastUpdateTime": "2018-01-09T10:03:23.256Z",
            "kilobytesDataTransferred": 0,
            "try": 1
        }
    }
}
```

**Example of generating and using an API key for authentication**

The following procedure provides a sample workflow to retrieve job information from NetBackup.  
This procedure involves logging onto NetBackup to receive a JWT and then creating an API key  
that uses the JWT. Then use this API key for fetching information of a specific job  
(job ID `5` in this scenario).

**Step 1**  
Use the NetBackup API endpoint `POST /login` to create a login request:

```
curl -X POST https://masterservername:1556/netbackup/login         \
     -H 'content-type: application/vnd.netbackup+json;version=1.0' \
     -d '{                                                         \
            "domainType":"vx",                                     \
            "domainName":"mydomain",                               \
            "userName":"myusername",                               \
            "password":"mypassword"                                \
        }'
```

The following response to the `login` request contains the JSON Web Token (JWT):

> **NOTE:**  
> This response contains three attributes: `token`, `tokenType` and `validity`. The `token` attribute provides the JWT.  
> The `validity` attribute indicates that the token returned is valid for `86400` seconds, or `24` hours.

```
  {
      "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsInppcCI6IkRFRiJ9.eNp0VF1v2jAU_S9-nHiArXQrb15yaT2cOLIdEJ2mKGWZmnXARMKEVvW_13EciO3weu65H-d-vaIyr9FsMp18Gt_dTsefb6bjESqrCs3Q7umYbfOqLg5ohH7XpYIWqwVfzNM1k6tHvCKJMhSnv63_5MvHO-V_cztC1fFJkQ_b3bGaHar6UGxeitm_k2Lnx_o5q_cvxW44Wlll-c9t2Vjrw7FokW2-eS53hcJ-5X-qwoT5n232u7o4qfJfEQchMZfZN_YVzb6jD-jHSGOMQ0YifA9ndElg5dJAZg9MyDMUcMASsmUkgC-B96jGYrFDoKCwgFEKgSQsPlsoETILgEsyJ4HyE2dLxEIyX9txDJYwSoK1Xa_F01EFZcLnZJgS3MOBNxEhDhNGYi9Tr7KLdJZ4JXBYsgUM0nUtnFFfmirQ7ZBUUZzm6EwEHClDmbTBKczEtacZK55kkXJuwrjcflm6gq45Tgne7I1_o9XF8CNPqdMTnIZEUnYvXLIjQZPnEIoQS2yjAwPVuJLrIFioFfYy4VQ-6JY70hLgERGiv6gad2SYVR9Ya822h6mOKI3sSXRnwSGEWBJMnTLsszTZhpbfarnh9cfI9_saN08DbzZF87m6RcSxyqAKoK63o9RsrJWnPd2zdq-5A8MRqUjUNllN6I4BgpQTuU44S7zzHOqQyeJdboDjAKiVor2YK8_nMutL7DQJux-m_KIIYukvnrthumPCbaS9BCbwkB5j8vW0cYZGfPVrXZHqrHrvU7tfsWmY9wf0Onakt7d3AAAA__8.VVE25rQqbrC-isGOqbRTqMPoK4ts5-9_6zSgz0fUg11m9GCClq10PS9u1DlaXye-S2MYYyHVEHSVs6uKcPVvN2WGBHkv7t-c4Hixc9O8zrJYhJaP979wF_gn08YnRlX7_o4Qj6muc1IWHjK0hPMIgq0X-sBU2Git9uppVW1jbLA",
      "tokenType": "BEARER",
      "validity": 86400
  }
```

**Step 2**  
Create the API key for this user using the JWT created above.

> **NOTE:**  
> The `Authorization` header uses the value of the `token` attribute from the response to the `login`  
> request made in the previous step.

```
curl -X POST https://masterservername:1556/netbackup/security/api-keys           \
     -H 'Content-Type: application/vnd.netbackup+json;version=3.0'                    \
     -H 'Authorization: eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsInppcCI6IkRFRiJ9.eNp0VF1v2jAU_S9-nHiArXQrb15yaT2cOLIdEJ2mKGWZmnXARMKEVvW_13EciO3weu65H-d-vaIyr9FsMp18Gt_dTsefb6bjESqrCs3Q7umYbfOqLg5ohH7XpYIWqwVfzNM1k6tHvCKJMhSnv63_5MvHO-V_cztC1fFJkQ_b3bGaHar6UGxeitm_k2Lnx_o5q_cvxW44Wlll-c9t2Vjrw7FokW2-eS53hcJ-5X-qwoT5n232u7o4qfJfEQchMZfZN_YVzb6jD-jHSGOMQ0YifA9ndElg5dJAZg9MyDMUcMASsmUkgC-B96jGYrFDoKCwgFEKgSQsPlsoETILgEsyJ4HyE2dLxEIyX9txDJYwSoK1Xa_F01EFZcLnZJgS3MOBNxEhDhNGYi9Tr7KLdJZ4JXBYsgUM0nUtnFFfmirQ7ZBUUZzm6EwEHClDmbTBKczEtacZK55kkXJuwrjcflm6gq45Tgne7I1_o9XF8CNPqdMTnIZEUnYvXLIjQZPnEIoQS2yjAwPVuJLrIFioFfYy4VQ-6JY70hLgERGiv6gad2SYVR9Ya822h6mOKI3sSXRnwSGEWBJMnTLsszTZhpbfarnh9cfI9_saN08DbzZF87m6RcSxyqAKoK63o9RsrJWnPd2zdq-5A8MRqUjUNllN6I4BgpQTuU44S7zzHOqQyeJdboDjAKiVor2YK8_nMutL7DQJux-m_KIIYukvnrthumPCbaS9BCbwkB5j8vW0cYZGfPVrXZHqrHrvU7tfsWmY9wf0Onakt7d3AAAA__8.VVE25rQqbrC-isGOqbRTqMPoK4ts5-9_6zSgz0fUg11m9GCClq10PS9u1DlaXye-S2MYYyHVEHSVs6uKcPVvN2WGBHkv7t-c4Hixc9O8zrJYhJaP979wF_gn08YnRlX7_o4Qj6muc1IWHjK0hPMIgq0X-sBU2Git9uppVW1jbLA' \
     -d '{"data":{"type": "apiKeyCreationRequest","attributes":{"expireAfterDays":"P1D","description":"API key for user myusername with 1 year validity"}}}'
```

The response contains two attributes `apiKey` and `expiryDateTime`.  
The `apiKey` attribute provides the API key for user "myusername".  
The `expiryDateTime` attribute indicates the time until which this API key is valid.

```
{
    "data": {
        "links": {
            "self": {
                "href": "/netbackup/security/api-keys/A1uMjmj93mo="
            }
        },
        "type": "apiKeyCreationResponse",
        "id": "A1uMjmj93mo=",
        "attributes": {
            "apiKey": "A1uMjmj93mrpsW9qWroT-paNdMSDPdABCEDi7PRPD-Mc0mkFn6-KvHdXT1v8Wxx7",
            "expiryDateTime": "2019-04-25T08:28:30.294Z"
        }
    }
}
```

**Step 3**  
Get the job information using the NetBackup API endpoint `GET /admin/jobs/{jobId}`.  
In this example, the information for the job ID `5` is requested.

> **NOTE:**  
> The `Authorization` header uses the value of the `apiKey` attribute from the response to the `login`  
> request made in the previous step.

```
curl -X GET https://masterservername:1556/netbackup/admin/jobs/5 \
     -H 'Accept: application/vnd.netbackup+json;version=2.0'     \
     -H 'Authorization: A1uMjmj93mrpsW9qWroT-paNdMSDPdABCEDi7PRPD-Mc0mkFn6-KvHdXT1v8Wxx7'
```

The response to the `GET` request contains the job information for job ID `5`:

```
{
    "data": {
...
        "type": "job",
        "id": "5",
        "attributes": {
            "jobId": 5,
            "parentJobId": 0,
            "activeProcessId": 27116,
            "mainProcessId": 0,
            "jobType": "IMAGEDELETE",
            "jobSubType": "IMMEDIATE",
            "policyType": "STANDARD",
            "policyName": "",
            "scheduleType": "FULL",
...
}
```

### Multifactor Authentication (MFA)

NetBackup issues JSON Web Token (JWT), post successful authentication of user credentials and validation of  
one-time password (OTP). Further invocation of NetBackup RESTful API(s) must include JSON Web Token (JWT) in  
`Authorization` HTTP header. To learn more about multifactor authentication, refer to the NetBackup  
[Web UI Administrators Guide](http://www.veritas.com/docs/DOC5332)

> **NOTE:**  
> NetBackup supports multifactor authentication starting from version **10.3**.

**Example of acquiring JWT of a user, registered with multifactor authentication**

**Step 1**

Use the NetBackup API endpoint `POST /login` to get multifactor authentication (MFA) token:

```
curl -X POST https://masterservername:1556/netbackup/login         \
     -H 'content-type: application/vnd.netbackup+json;version=10.0' \
     -d '{                                                         \
            "domainType":"unixpwd | NT | vx | ldap",                \
            "domainName":"mydomain",                               \
            "userName":"myusername",                               \
            "password":"mypassword"                                \
        }'
```

A successful response is indicated by HTTP response code `200` and content a JSON object. Response JSON object will have  
the following form.

```
  {
      "token": "AIwUEF-fbJEtnGtUhUBuadgTgMrRRTnjbKjFFhTyhZWwtMDgubmJ1c2VjLnZ4aW5kaWEudmVyaXRhAVAbbdmthbmRlOnVuaXhwd2Q6MTAwMjpmYWxzZQ==.UZR6ECpvSzEE4IkpMcUf_aXdWCiauJQfm2zZZgaQX3w3oHyVf8YvHgVtH8VsUiQ7XID4cpszzgLgtjh5ntmnmGFKfFGRh4T1FY7reUk5MTUZZTBHCCh80ozVtuzJ5NkUZ31tpqvQyIzQW4nOWfcHajxjgdAuroFq6DxXCtEbQuuN_UTxlgk3cUNuCnP9K9o-pmQALCz0alOo00sU_xA==",
      "tokenType": "MFA",
      "validity": 180
  }
```

> **NOTE:**  
> The `tokenType` indicates the type of token. The possible values are `BEARER`, `MFA`.  
> The `BEARER` type of token is a `JWT`. But in case of multifactor authentication, the token type is `MFA`. Usage of MFA  
> token type is limited to validation of one-time password. The validity period of the MFA state token is `180` seconds  
> that is identified by the `validity` object in the JSON response.  
> Next step enumerates method to use MFA state token to acquire JSON Web Token (JWT).

**Step 2**

In previous step we have proved what we know ( username and password ), in this step we must prove what we have (Authenticator application generated one-time password).  
To accomplish this, you should use MFA state token that you have received earlier (in step 1) and invoke HTTP POST method on `/netbackup/login` RESTful API.

Input to `/netbackup/login` RESTful API shall be as following:

```
curl -X POST https://masterservername:1556/netbackup/login         \
     -H 'content-type: application/vnd.netbackup+json;version=10.0' \
     -d '{                                                         \
            "domainType":"vx",                                     \
            "domainName":"vrts.mfa.totp",                               \
            "userName":"AIwUEF-fbJEtnGtUhUBuadgTgMrRRTnjbKjFFhTyhZWwtMDgubmJ1c2VjLnZ4aW5kaWEudmVyaXRhAVAbbdmthbmRlOnVuaXhwd2Q6MTAwMjpmYWxzZQ==.UZR6ECpvSzEE4IkpMcUf_aXdWCiauJQfm2zZZgaQX3w3oHyVf8YvHgVtH8VsUiQ7XID4cpszzgLgtjh5ntmnmGFKfFGRh4T1FY7reUk5MTUZZTBHCCh80ozVtuzJ5NkUZ31tpqvQyIzQW4nOWfcHajxjgdAuroFq6DxXCtEbQuuN_UTxlgk3cUNuCnP9K9o-pmQALCz0alOo00sU_xA==",                               \
            "password":"123456"                             \
        }'
```

> **NOTE:**  
> In the snippet above value of `domainType` and `domainName` must be `vx` and `vrts.mfa.totp` respectively. Value of `userName`  
> must be MFA state token as received from `step 1`. `Password` field must be set to one-time password which is generated  
> on your registered smart device. All fields in the input JSON are mandatory and must be adhered to as specified in above snippet.

```
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsInppcCI6IkRFRiJ9.eNp0VF1v2jAU_S9-nHiArXQrb15yaT2cOLIdEJ2mKGWZmnXARMKEVvW_13EciO3weu65H-d-vaIyr9FsMp18Gt_dTsefb6bjESqrCs3Q7umYbfOqLg5ohH7XpYIWqwVfzNM1k6tHvCKJMhSnv63_5MvHO-V_cztC1fFJkQ_b3bGaHar6UGxeitm_k2Lnx_o5q_cvxW44Wlll-c9t2Vjrw7FokW2-eS53hcJ-5X-qwoT5n232u7o4qfJfEQchMZfZN_YVzb6jD-jHSGOMQ0YifA9ndElg5dJAZg9MyDMUcMASsmUkgC-B96jGYrFDoKCwgFEKgSQsPlsoETILgEsyJ4HyE2dLxEIyX9txDJYwSoK1Xa_F01EFZcLnZJgS3MOBNxEhDhNGYi9Tr7KLdJZ4JXBYsgUM0nUtnFFfmirQ7ZBUUZzm6EwEHClDmbTBKczEtacZK55kkXJuwrjcflm6gq45Tgne7I1_o9XF8CNPqdMTnIZEUnYvXLIjQZPnEIoQS2yjAwPVuJLrIFioFfYy4VQ-6JY70hLgERGiv6gad2SYVR9Ya822h6mOKI3sSXRnwSGEWBJMnTLsszTZhpbfarnh9cfI9_saN08DbzZF87m6RcSxyqAKoK63o9RsrJWnPd2zdq-5A8MRqUjUNllN6I4BgpQTuU44S7zzHOqQyeJdboDjAKiVor2YK8_nMutL7DQJux-m_KIIYukvnrthumPCbaS9BCbwkB5j8vW0cYZGfPVrXZHqrHrvU7tfsWmY9wf0Onakt7d3AAAA__8.VVE25rQqbrC-isGOqbRTqMPoK4ts5-9_6zSgz0fUg11m9GCClq10PS9u1DlaXye-S2MYYyHVEHSVs6uKcPVvN2WGBHkv7t-c4Hixc9O8zrJYhJaP979wF_gn08YnRlX7_o4Qj6muc1IWHjK0hPMIgq0X-sBU2Git9uppVW1jbLA",
  "tokenType": "BEARER",
  "validity": 14400
}
```

**Example of acquiring JWT using multifactor authentication with password and one-time password(OTP)**

In previous example it is seen that when multifactor authentication (MFA) is enabled, then user can obtain the Json  
Web Token (JWT) using password and one-time password. NetBackup provides another way to get Json Web Token (JWT) when  
multifactor authentication is enabled. The user can append one-time password (OTP) to the password.

> **NOTE:**  
> If multifactor authentication (MFA) is enabled, and if REST client makes login API request using NetBackup API  
> version earlier than **10.0**, then you should provide one-time password (OTP) appended to password to get Json Web Token (JWT).

```
curl -X POST https://masterservername:1556/netbackup/login         \
     -H 'content-type: application/vnd.netbackup+json;version=10.0' \
     -d '{                                                         \
            "domainType":"vx",                                     \
            "domainName":"mydomain",                               \
            "userName":"myusername",                               \
            "password":"mypassword123456"                           \
        }'
```

> **NOTE:**  
> This response contains three attributes: `token`, `tokenType` and `validity`. The `token` attribute provides the JWT.  
> The `validity` attribute indicates that the token returned is valid for `14400` seconds.

```
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsInppcCI6IkRFRiJ9.eNp0VF1v2jAU_S9-nHiArXQrb15yaT2cOLIdEJ2mKGWZmnXARMKEVvW_13EciO3weu65H-d-vaIyr9FsMp18Gt_dTsefb6bjESqrCs3Q7umYbfOqLg5ohH7XpYIWqwVfzNM1k6tHvCKJMhSnv63_5MvHO-V_cztC1fFJkQ_b3bGaHar6UGxeitm_k2Lnx_o5q_cvxW44Wlll-c9t2Vjrw7FokW2-eS53hcJ-5X-qwoT5n232u7o4qfJfEQchMZfZN_YVzb6jD-jHSGOMQ0YifA9ndElg5dJAZg9MyDMUcMASsmUkgC-B96jGYrFDoKCwgFEKgSQsPlsoETILgEsyJ4HyE2dLxEIyX9txDJYwSoK1Xa_F01EFZcLnZJgS3MOBNxEhDhNGYi9Tr7KLdJZ4JXBYsgUM0nUtnFFfmirQ7ZBUUZzm6EwEHClDmbTBKczEtacZK55kkXJuwrjcflm6gq45Tgne7I1_o9XF8CNPqdMTnIZEUnYvXLIjQZPnEIoQS2yjAwPVuJLrIFioFfYy4VQ-6JY70hLgERGiv6gad2SYVR9Ya822h6mOKI3sSXRnwSGEWBJMnTLsszTZhpbfarnh9cfI9_saN08DbzZF87m6RcSxyqAKoK63o9RsrJWnPd2zdq-5A8MRqUjUNllN6I4BgpQTuU44S7zzHOqQyeJdboDjAKiVor2YK8_nMutL7DQJux-m_KIIYukvnrthumPCbaS9BCbwkB5j8vW0cYZGfPVrXZHqrHrvU7tfsWmY9wf0Onakt7d3AAAA__8.VVE25rQqbrC-isGOqbRTqMPoK4ts5-9_6zSgz0fUg11m9GCClq10PS9u1DlaXye-S2MYYyHVEHSVs6uKcPVvN2WGBHkv7t-c4Hixc9O8zrJYhJaP979wF_gn08YnRlX7_o4Qj6muc1IWHjK0hPMIgq0X-sBU2Git9uppVW1jbLA",
  "tokenType": "BEARER",
  "validity": 14400
}
```

### Adaptive Multifactor Authentication (Adaptive MFA)

NetBackup 10.3 introduced multifactor authentication using time-based one-time password (OTP).  
In NetBackup 10.4, the existing multifactor authentication infrastructure is enhanced to be `adaptive` where certain  
critical NetBackup operations can be monitored for malicious attacks. The risk involved in critical operations such as  
modifying global security settings is determined using the Risk Engine. It then triggers the adaptive MFA functionality that prompts you to reauthenticate with the one-time password during these critical operations.

> **NOTE:**  
> NetBackup supports Adaptive multifactor authentication starting from version **10.4** for following endpoints.
>
> * `POST /netbackup/security/properties`
> * `POST /netbackup/security/api-keys`

**Example of Adaptive multifactor authentication**

**Step 1**

Use the NetBackup API endpoint `POST /security/properties` to update security configuraton:

```
curl -X POST https://masterservername:1556/netbackup/security/properties/         \
     -H 'content-type: application/vnd.netbackup+json;version=11.0' \
     -d '{
            "allowInsecureBackLevelHost": 1
         }'
```

The HTTP response code `202` and HTTP response header `X-NetBackup-MFA-Request` indicate that the request is accepted by  
the server and requires multifactor authentication to be successful. Use the `X-NetBackup-MFA-Request` header value to  
invoke the endpoint `POST netbackup/security/adaptive-mfa/{requestId}/validate` and enter the valid one-time password.

**Step 2**

In previous step we have invoked `POST /security/properties` to update the security configuration. In response, we got  
the HTTP response code `202` that indicates we need perform multifactor authentication. To perform the multifactor authentication,  
use `POST netbackup/security/adaptive-mfa/{requestId}/validate`. The `requestId` can be found in the HTTP response header  
`X-NetBackup-MFA-Request`.

Input to `/netbackup/security/adaptive-mfa/{requestId}/validate` RESTful API should be as follows:

```
curl -X POST https://masterservername:1556/netbackup/security/adaptive-mfa/K6dWqpOVdgvQtphc4b_IJTBbrKdXneKU9r6DojmdXEEcZ7rjXmDQej8SdNOH1eIplEN9UTGErQY2XDHjp8uWMA==/validate        \
     -H 'content-type: application/vnd.netbackup+json;version=11.0' \
     -d '{
           "data": {
             "type": "mfaOTPValidateRequest",
             "attributes": {
                   "otpCode": "842815"
             }
           }
        }'
```

> **NOTE:**  
> The endpoint `POST /netbackup/security/adaptive-mfa/{requestId}/validate` returns the original API response.  
> Therefore, `POST /netbackup/security/adaptive-mfa/{requestId}/validate` returns `POST /netbackup/security/properties` response on success.

### SSL certificate validation

The NetBackup web service always sends its certificate during SSL handshakes. This certificate can be validated by the  
API client. To validate the certificate, you will need to get the Certificate Authority (CA) certificate from the master  
server and then use the CA certificate in the API requests.

> **TIP:**  
> It is a good practice to validate the SSL certificate. This action ensures that you are communicating with the correct  
> web service.

**Step 1**  
Get the CA certificate from the master server using the `GET /security/cacert` API:

> **NOTE:**  
> You cannot make a secure request with certificate validation until you have the CA certificate. To obtain the initial CA  
> certificate you must skip the certificate validation, with the "--insecure" curl option.

```
curl -X GET https://masterservername:1556/netbackup/security/cacert \
     -H 'content-type: application/vnd.netbackup+json;version=2.0'   \
     --insecure
```

The response to the `cacert` request contains two certificates:

```
    {
        "webRootCert": "-----BEGIN CERTIFICATE-----\nMIICljCCAf+gAwIBAgIIcte7aAAAAAAwDQYJKoZIhvcNAQENBQAwTTEOMAwGA1UE\nAxMFbmJhdGQxLjAsBgNVBAsUJXJvb3RAbW9ybGV5dm01LnJtbnVzLnNlbi5zeW1h\nbnRlYy5jb20xCzAJBgNVBAoTAnZ4MB4XDTE4MDEwODE0MjcyNloXDTM4MDEwMzE1\nNDIyNlowTTEOMAwGA1UEAxMFbmJhdGQxLjAsBgNVBAsUJXJvb3RAbW9ybGV5dm01\nLnJtbnVzLnNlbi5zeW1hbnRlYy5jb20xCzAJBgNVBAoTAnZ4MIGfMA0GCSqGSIb3\nDQEBAQUAA4GNADCBiQKBgQDpRc/yo0utxcKrftPeOzn1o1MR5b42uGWrwg9kU4VM\nZN++0kvrtRWt4wz8zdtNU4wtg/MHWt0ffj6FRYYAZBbM8fu56GFux3wCPJSHWl6B\nZ0nD1vZxFUwTXkRAAObuHrYphjBNf1oUU+4GS44KD4/UW/bucKdZsUI1+HcfCQZw\nNwIDAQABo38wfTAPBgNVHRMBAf8EBTADAQH/MAsGAyoDBQQEcm9vdDAPBgMqAwYE\nCDAwMDAwMDE3MC0GAyoDCAQmezg2ZDY5MDU0LWY0OGEtMTFlNy1hNDAyLTYwYWQy\nMTZjYTdlZX0wHQYDVR0OBBYEFE/mpo7PbWs7p/zkAHWi/BDwpdn+MA0GCSqGSIb3\nDQEBDQUAA4GBAAmZJ98XLqG0H+qwyuZ97YdzE2dWKpRduuARYJp437Sc6tpL6nFn\nuzbtGV30tDdhROYPf1AoNRmZHvz40Hra1B8j4VFggPZOAmmk+UJPjzeHn6qhlRxl\nHjCdEqUZ//+1Aqgj6f/6bqPO5boCVP1qw8N60fkBaV3zLwAOY6CKiHS0\n-----END CERTIFICATE-----\n",
        "cacert": [
            "-----BEGIN CERTIFICATE-----\nMIICljCCAf+gAwIBAgIIcte7aAAAAAAwDQYJKoZIhvcNAQENBQAwTTEOMAwGA1UE\nAxMFbmJhdGQxLjAsBgNVBAsUJXJvb3RAbW9ybGV5dm01LnJtbnVzLnNlbi5zeW1h\nbnRlYy5jb20xCzAJBgNVBAoTAnZ4MB4XDTE4MDEwODE0MjcyNloXDTM4MDEwMzE1\nNDIyNlowTTEOMAwGA1UEAxMFbmJhdGQxLjAsBgNVBAsUJXJvb3RAbW9ybGV5dm01\nLnJtbnVzLnNlbi5zeW1hbnRlYy5jb20xCzAJBgNVBAoTAnZ4MIGfMA0GCSqGSIb3\nDQEBAQUAA4GNADCBiQKBgQDpRc/yo0utxcKrftPeOzn1o1MR5b42uGWrwg9kU4VM\nZN++0kvrtRWt4wz8zdtNU4wtg/MHWt0ffj6FRYYAZBbM8fu56GFux3wCPJSHWl6B\nZ0nD1vZxFUwTXkRAAObuHrYphjBNf1oUU+4GS44KD4/UW/bucKdZsUI1+HcfCQZw\nNwIDAQABo38wfTAPBgNVHRMBAf8EBTADAQH/MAsGAyoDBQQEcm9vdDAPBgMqAwYE\nCDAwMDAwMDE3MC0GAyoDCAQmezg2ZDY5MDU0LWY0OGEtMTFlNy1hNDAyLTYwYWQy\nMTZjYTdlZX0wHQYDVR0OBBYEFE/mpo7PbWs7p/zkAHWi/BDwpdn+MA0GCSqGSIb3\nDQEBDQUAA4GBAAmZJ98XLqG0H+qwyuZ97YdzE2dWKpRduuARYJp437Sc6tpL6nFn\nuzbtGV30tDdhROYPf1AoNRmZHvz40Hra1B8j4VFggPZOAmmk+UJPjzeHn6qhlRxl\nHjCdEqUZ//+1Aqgj6f/6bqPO5boCVP1qw8N60fkBaV3zLwAOY6CKiHS0\n-----END CERTIFICATE-----\n"
        ]
    }
```

**Step 2**  
Save the `webRootCert` certificate. To do this save the `webRootCert` string to a file. Make sure to convert the `\n`  
escape sequences to new lines (carriage returns).

For example, your file would look something like this:

```
-----BEGIN CERTIFICATE-----
MIICljCCAf+gAwIBAgIIcte7aAAAAAAwDQYJKoZIhvcNAQENBQAwTTEOMAwGA1UE
AxMFbmJhdGQxLjAsBgNVBAsUJXJvb3RAbW9ybGV5dm01LnJtbnVzLnNlbi5zeW1h
bnRlYy5jb20xCzAJBgNVBAoTAnZ4MB4XDTE4MDEwODE0MjcyNloXDTM4MDEwMzE1
NDIyNlowTTEOMAwGA1UEAxMFbmJhdGQxLjAsBgNVBAsUJXJvb3RAbW9ybGV5dm01
LnJtbnVzLnNlbi5zeW1hbnRlYy5jb20xCzAJBgNVBAoTAnZ4MIGfMA0GCSqGSIb3
DQEBAQUAA4GNADCBiQKBgQDpRc/yo0utxcKrftPeOzn1o1MR5b42uGWrwg9kU4VM
ZN++0kvrtRWt4wz8zdtNU4wtg/MHWt0ffj6FRYYAZBbM8fu56GFux3wCPJSHWl6B
Z0nD1vZxFUwTXkRAAObuHrYphjBNf1oUU+4GS44KD4/UW/bucKdZsUI1+HcfCQZw
NwIDAQABo38wfTAPBgNVHRMBAf8EBTADAQH/MAsGAyoDBQQEcm9vdDAPBgMqAwYE
CDAwMDAwMDE3MC0GAyoDCAQmezg2ZDY5MDU0LWY0OGEtMTFlNy1hNDAyLTYwYWQy
MTZjYTdlZX0wHQYDVR0OBBYEFE/mpo7PbWs7p/zkAHWi/BDwpdn+MA0GCSqGSIb3
DQEBDQUAA4GBAAmZJ98XLqG0H+qwyuZ97YdzE2dWKpRduuARYJp437Sc6tpL6nFn
uzbtGV30tDdhROYPf1AoNRmZHvz40Hra1B8j4VFggPZOAmmk+UJPjzeHn6qhlRxl
HjCdEqUZ//+1Aqgj6f/6bqPO5boCVP1qw8N60fkBaV3zLwAOY6CKiHS0
-----END CERTIFICATE-----
```

**Step 3**  
You can now use the CA certificate in your API requests. For example, to securely use the `cacert` API remove the  
`--insecure` option and use the `--cacert <filename>` option. In the following example, the CA certificate was saved in  
the file `cacert.pem`.

```
curl -X GET https://masterservername:1556/netbackup/security/cacert \
     -H 'content-type: application/vnd.netbackup+json;version=2.0'   \
     --cacert cacert.pem
```

### Authorization

#### Key Concepts of NetBackup Role Based Access Control

Access control is applied to functional areas of NetBackup (namespaces) at either an API level or object level. Principals are assigned roles that map to operations and roles configured for specific namespaces or objects within the namespace hierarchy.

##### Objects

An object is any NetBackup resource to which you can apply access control, such as a workload asset, a policy, a protection plan, a job, etc.

##### Namespace

NetBackup objects are identified by namespaces that represent functional areas of NetBackup.

> ***For example***:  
> `|ASSETS|MSSQL|INSTANCES|` - Represents the collection of Microsoft SQL Server INSTANCES of the MSSQL workload in the ASSETS top-level namespace.  
> `|ASSETS|MSSQL|INSTANCES|Finance1|` - Represents a specific Microsoft SQL Server instance object.  
> `|PROTECTION|POLICIES|` - Represents the collection of NetBackup policies.

Namespaces have segments in a descending hierarchical structure and are delimited by a pipe or vertical bar character "|".  
You can grant or control accessf at any segment of the namespace hierarchy. Namespace segments can inherit access control from parent namespace segments.  
APIs can have access control on the API level or on the object level. See â€œLevel of Enforcementâ€�.

##### Operations

An operation is an action that you can take on an object. That action may be privileged. Operations are represented by namespaces, for example, `|OPERATIONS|VIEW|`, `|OPERATIONS|UPDATE|`, `|OPERATIONS|ASSETS|RECOVER|`.  
Operations are an element of an object's ACL (Access Control List).

##### Roles

A role represents a job function within NetBackup as determined by an administrator. Principals are assigned roles. The list of roles assigned a principal make up the authorization context of a JWT (JSON Web Token).  
A role is an element of an object's ACL.

##### ACL (Access Control Lists)

An ACL defines who (what roles) and the level of access (operations) configured on an object namespace or inherited from a parent namespace.\  
An ACE is made up of:

* A role
* One or more operations granted to that role on the NetBackup resource.
* A propagation option (below)

An object's ACL is list of ACEs (Access Control Entries).

##### Inheritance

Inheritance applies to an access-controlled resource (Namespace).  
Depending on where a resource is defined in the hierarchy, it may have access control configured directly on the object itself.  
It may also assume configured access control from a parent NetBackup resource.

> ***For example***:  
> A Microsoft SQL Server database is logically "contained" in a SQL server instance.  
> ACEs may be configured directly on a given database.  
> ACEs may also be configured on the containing instance. Any databases defined on that instance may inherit the access configured on the instance.

##### Propagation

Propagation applies to an ACE. Propagation determines if an ACE applies to itself, its children, or to both itself and its children.

> **NOTE**: In most cases propagation applies to both the ACE itself and its children.

#### Level of Enforcement

Depending on the API, enforcement of access control can be applied on the API level or on the object level.   
An administrator can control who has access to specific NetBackup APIs, based on role assignment. An administrator can control the level of access based on the operations that are configured on a resource namespace.  
The granularity of that control depends on the access that you configure in a resource namespace hierarchy.  
Access that is configured in higher-level segments of a namespace grants access to a broader range of objects.

> ***For example***:  
> A security administrator role may be granted operations on the `|SECURITY|CERTIFICATES|` namespace, which gives access to all the host certificates that are managed by the API end point `/netbackup/security/certificates` (API-Level).

Conversely, for a workload assets API, /assetservice/vmware/assets, you can configure finer-grained control (Object-Level) at lower-level namespaces that represent the physical resource objects of the collection.

> ***For example***:  
> A user can be assigned a specific role which grants View access only to a specific VMWare virtual machine.  
> `|ASSETS|VMWARE|VCENTERS|development-vcenter-1|VMS|virtual-machine-123|`  
> Assuming `|virtual-machine-123|` does not inherit configured access from the parent, the user has access to the single vm.

Not all NetBackup APIs are capable of fine-grained object-level access control. Some are only enforced at higher level namespace segments. Those APIs are identified in API documentation with:  
`Enforcement Type: API-Level`

Those APIs which are capable of object-level RBAC configuration are identified in API documentation with:  
`Enforcement Type: Object-Level`

##### API-Level Enforcement

Data requests enforced at the API level allow the authorized principals to perform one or more operations on ALL objects of the resource collection that are managed by the API end point. The specific operations the administrator wants to authorize must be present in the ACL of the namespace that represents the resource collection for the API. Principals are granted access to the API when they have a role with an ACL that includes the namespaces and operations that are enforced on the API.

##### Object-Level Enforcement

Data requests enforced at an object level only allow the authorized principals to perform one or more operations at a more granular (object) level. In this case, the ACLs are typically applied at an object-level namespace that represents a specific NetBackup resource. A principal then only has access to a subset of the resource collection. The specific operations the administrator wants to authorize for the object must be present in the ACL of the namespace that represents that object. Principals are granted access to the object when they have a role with an ACL that includes the namespaces and operations that are enforced on the object level.

> **NOTE:**  
> Object-level enforcement can apply at various points in a namespace hierarchy.  
> Access configured at `|ASSETS|MSSQL|INSTANCES|` may propagate down to child objects.  
> Separate access can also be configured at `|ASSETS|MSSQL|INSTANCES|Finance-1|DATABASES|` which grants additional access to the `|DATABASES|` folder within the instance.  
> Access configured at the `|DATABASES|` segment may or may not inherit access from parent namespaces.

APIs that enforce object-level access control may implement a `meta` request parameter that, when present in the request, returns a `meta` section in the response document that includes the access control namespace.

In NetBackup Swagger documentation, the enforcement type, the namespace that represents the API resources, and any required operations for a given resource path are documented in the **Description** section of the resource as below:â€¨â€¨

```
Enforcement-Type: (API-Level or Object-Level)
Namespace: (the delimited access control namespace representing the resource(s) )
Requires Operation: (the required operation name)
```

### Versioning

To maintain compatibility with the back-level API clients, it is sometimes necessary to version the NetBackup API. The  
NetBackup API is developed so that new versions are minimized. However, at times changes are needed to the API that  
require a new API version. The mechanism to version the NetBackup API is described below.

Version numbers follow a simple `MAJOR.MINOR` pattern, such as `1.2`. These version numbers are not the same as the  
NetBackup release number. The current API version number is documented with every NetBackup release. The version number  
may not increase sequentially from one NetBackup release to the next release. The version number may increase by  
multiple major versions between two consecutive NetBackup releases.

Content negotiation is used to specify which API version the API client is requesting. A new vendor-specific media type  
`application/vnd.netbackup+json` is used, along with a media type parameter named `version`. For example:  
`application/vnd.netbackup+json;version=2.0`. This media type should be used in the `Accept` or `Content-Type` HTTP  
header of your request. If you send both `Accept` and `Content-Type` HTTP headers, their values must match.

In some cases, an API does not consume any input or produce any output. Such a case normally means that neither `Accept`  
nor `Content-Type` HTTP headers are required. However, because these headers are used to specify the API version, the  
`Accept` header must be specified.

> **TIP:**  
> The value of the `Content-Type` or `Accept` HTTP header in a NetBackup API request must use this format:  
> `application/vnd.netbackup+media;version=<major>.<minor>`

It is important for you to consider the kind of changes that will require a new version of the NetBackup API. Developing  
your API client with these rules in mind will ensure that your API client remains compatible with the future versions of  
the NetBackup API.

The following is a list of possible API changes and if they result in a new API version:

| API change results in a new version? | Yes / No |
| --- | --- |
| Add a new endpoint | No |
| Remove an endpoint | Yes |
| Add an output field or attribute | No |
| Remove output field or attribute | Yes |
| Add required input field or attribute | Yes |
| Add non-required input field or attribute | No |

> **NOTE:**
>
> * If the API client expects a particular endpoint or field in the NetBackup response, then removing the endpoint or  
>   field results in a new version.
> * If NetBackup expects a new required field in the request from the API client, then adding it results in a new  
>   version.
> * As you develop your API client, as a best practice you should ignore any new fields that are returned to you. Do not  
>   treat unrecognized fields as an error. This way your API clients can continue to work with future releases of NetBackup  
>   without any change.

### Pagination

Some NetBackup APIs use pagination to limit the number of resources returned in a response. These APIs use the  
`page[offset]` and `page[limit]` query parameters to set the starting point (offset) and the page size (limit). The  
results are returned in a page-by-page format.

> **TIP:**  
> The default page size is `10` resources. The type of resource depends on the individual API. For example: For the API  
> that gets a list of jobs, the page contains job-related information for up to `10` NetBackup jobs.

### Filtering

Some NetBackup APIs use the 'filter' query parameter to limit or reduce the number of resources that the response  
returns.

Use the OASIS syntax to specify the value of the `filter` using OData filtering language:  
<http://docs.oasis-open.org/odata/odata/v4.01/csprd01/part2-url-conventions/odata-v4.01-csprd01-part2-url-conventions.html#_Filter_System_Query>.

> **NOTE:**  
> The supported OData operators and functions depend on each individual NetBackup API, as described in the NetBackup API  
> reference.

### Date and time formatting

All NetBackup APIs accept and return date and time values using the ISO 8601 format in UTC with the `Z` zone designator.

More information on the details of the ISO spec can be found in the Wikipedia article, "ISO 8601":  
<https://en.wikipedia.org/wiki/ISO_8601>.

### Integer formatting

All integer property values are expected to be in 32-bit format unless it is explicitly stated otherwise in the  
documentation. This means that a property of type integer without a format specified like this

```
type: integer
```

should be interpreted as having the `int32` format by default.

```
type: integer
format: int32
```

### About request header X-Client-ID

Veritas recommends that you set the `X-Client-ID` HTTP request header which mentions  
the identity of the consumer component. For example, you can set this HTTP request header  
value to `customer_id-component_name_calling_the_NB_APIs`. Please note that this value won't be  
used for any other purposes than telemetry analysis of NetBackup APIs usage. This header value enables  
Veritas NetBackup to understand API usage pattern and might help Veritas make improvements in the most frequently used APIs.

### About request header X-Request-ID

You can set the request header `X-Request-ID` while making API calls. This header's value normally is a  
UUID, which is tied to the given request, but it can be any random string. This value can be used by NetBackup APIs  
to track the request across multiple NetBackup sub-components (other NetBackup processes) if the API implementation  
requires communication with other NetBackup components. If you do not mention this value,  
the NetBackup API server generates a secure random string and returns this value in `X-Request-ID` response header.  
Veritas recommends that API consumers log this request identifier in order to help track a single request end-to-end,  
which helps in troubleshooting issues with APIs.

### About encoding requests

All request URLs of NetBackup APIs must be [percent encoded](https://en.wikipedia.org/wiki/Percent-encoding) according to the [RFC3986](https://tools.ietf.org/html/rfc3986).  
The following aspects need to be taken care of when percent encoding.

* Percent encode all URL path parameters
* Percent encode all query paramters names and values

Here is an example with query parameters:  
A request to GET all assets using a query filter to return only virtual machines where the cluster name begins with `Name-Ã  !@#$%^&*`.  
Additionally, this request is specifying a page offset of 3 and page limit of 9.

```
Intended Request
GET https://master.nb.com/netbackup/assets?filter=startswith(extendedAttributes/cluster,'Name-Ã  !@#$%^&*')&page[limit]=9&page[offset]=3
```

should be encoded like below. Note the encoding for query parameters name and value.

```
Encoded Request
GET https://master.nb.com/netbackup/assets?filter=startswith(extendedAttributes%2Fcluster,'Name-%C3%A0%20!%40%23%24%25%5E%26*')&page%5Blimit%5D=9&page%5Boffset%5D=3
```

A sample cURL request for the above looks like this

```
curl --request GET \
  --url "https://master.nb.com/netbackup/assets?filter=startswith(extendedAttributes%2Fcluster%2C'Name-%C3%A0%2040%23%24%25%5E%26*')&page%5Blimit%5D=9&page%5Boffset%5D=3" \
  --header "accept: application/vnd.netbackup+json;version=3.0" \
  --header "authorization: <authorization-token>"
```

### Asynchronous API's

When an operation may not complete in a reasonable amount of time it may be implemented using the asynchronous pattern.  
The following procedure provides a sample workflow for working with asynchronous APIs.

***Step 1***  
Use the NetBackup API endpoint to initiate the async operation.

```
GET /netbackup/library/async-articles-resource HTTP/1.1
Accept: application/vnd.netbackup+json; version=1.0
```

The initial response to the request.

```
HTTP/1.1 202 Accepted
Content-Type: application/vnd.netbackup+json; version=1.0
Location:  /netbackup/library/async-articles-resource-results/10
Retry-after: 2022-01-14T14:46:01.311Z
```

The location header contains the location to check for the results of the async operation.  
The retry-after header indicates when a GET request can be executed on the status monitor URL.

***Step 2***  
Use the NetBackup API status-monitor end point to check for the results.

```
GET /netbackup/library/async-articles-resource-results/10
HTTP/1.1 
Accept: application/vnd.netbackup+json; version=1.0
```

In this case, the async operation is still executing.

```
HTTP/1.1 102 Processing
Content-Type: application/vnd.netbackup+json; version=1.0
Retry-after: 2022-01-14T14:47:01.311Z
{
  "meta": {
    "asyncResourceStatus": {
      "httpResponse": 102
    }
  }
}
```

A subsequent `GET` request is issued to the NetBackup API status-monitor end point which does satisfy the `Retry-after` header value.

```
GET /netbackup/library/async-articles-resource-results/10 
HTTP/1.1

Accept: application/vnd.netbackup+json; version=1.0
```

The async operation has successfully completed.

```
HTTP/1.1 200 Ok
Content-Type: application/vnd.netbackup+json; version=1.0

{
  "data": [
    {
      "id": "1",
      "type": "article",
      "attributes": {
        ...
      }
    }, {
      "id": "2",
      "type": "article",
      "attributes": {
        ...
      }
    }
  ],
  "meta": {
    "asyncResourceStatus": {
      "httpResponse": 200
    }
  }
}
```

The http response code in the meta represents the status of the async operation.  
The request's http response code represents the status of the status monitor URL request.

***Step 3***  
Use the NetBackup API status-monitor end point to cancel the asynchronous operation.

```
DELETE /netbackup/library/async-articles-resource-results/10
HTTP/1.1
```

The response to cancel the operation.

```
HTTP/1.1 204 No Content
```

### API Documentation on Master Server

The NetBackup API documentation is available directly on the master server using the Swagger UI for presentation.  
This enables API testing using the `Try It Out` button. Please note that using this functionality makes real API calls  
to your Master Server.

> **NOTE:**  
> While all the standard security and authorization checks are enforced, it is possible to make  
> destructive calls using this tool. It is recommended that this be used in a development environment.

The documentation can be found at the following URL: `https://<master_server>:1556/api-docs/index.html`

## API Code Samples

To hit the ground running with the NetBackup API, you can refer to the API code samples in different programming  
languages. The API code samples are located on GitHub: <https://github.com/VeritasOS/netbackup-api-code-samples>. This is  
a community-supported, open source project available under the MIT license.

> **Disclaimer:**
>
> * The API code samples are not officially supported by Veritas and should not be used in a production environment.
> * The purpose of these code samples is only to serve as a reference, to help you write your own applications using the  
>   NetBackup API.

## What's New in NetBackup 10.4?

### New APIs

* **Robots:**
  + Delete robots.
  + Update a robot.
  + Get robot details by robot name.
  + Retrieve list of unique device hosts for configured robots.
* **Robot Inventory:**
  + Get robot contents.
  + Fetch the list of barcode rules.
  + Create a new barcode rule on the media manager server.
  + Update the specified barcode rule.
  + Delete the specified barcode rule.
  + Fetch the list of media server's media ID generation rules.
  + Set the list of media server's media ID generation rules.
  + Fetch the list of media server's media ID prefixes.
  + Set the list of the media server's media ID prefixes.
  + Manage robot volume configuration.
  + Get media type mappings for a specified robot type.
* **Tape media volumes:**
  + Retrieve list of tape media volumes.
  + Create tape media volumes.
  + Retrieve details for a tape media volume.
  + Perform quick erase or long erase on a volume.
  + Perform label operation on a volume.
  + Retrieve list of external media types.
  + Rescan and update barcodes for one or more tape volumes.
  + Move volumes between robots.
  + Update one or more tape volumes.
  + Delete one or more tape volumes.
  + Eject one or more tape media volumes from a robot.
* **Tape media volume groups:**
  + Retrieve list of tape volume groups.
  + Retrieve details of a tape volume group.
  + Update a tape volume group.
  + Delete a tape volume group.
* **Volume pools:**
  + Create a new tape volume pool.
  + Retrieve details of a volume pool by id.
  + Update a volume pool.
  + Delete one or more volume pools.
* **Tape Media Owners:** Retrieve a list of media owner names.
* **Media Settings:**
  + Retrieve associated EMM server settings.
  + Update associated EMM server setting.
* **Storage devices:** Retrieve tape robots and standalone drives used for storage unit configuration.
* **Malware:**
  + Delete failed/canceled scan result with specified id.
  + Validate configuration for malware scan.
* **Anomaly:** Update the feedback parameters of a policy and client.
* **File Hash Search:** Search files by file hash.
* **Multifactor Authentication:** The existing multifactor authentication infrastructure is enhanced to be adaptive.

### Versioned APIs

This is a list of APIs that have been versioned in 10.4 due to breaking changes. The previous version of these APIs  
is still supported by specifying the correct version. See the Versioning section above for more details.

* Get tape-volume-pools API: `GET /storage/tape-volume-pools` no longer supports filtering on `policyType`.
* Establish trust with a primary server API:`POST /config/servers/trusted-master-servers`  
  `Request Payload for credential based trust will require one additional 'remotePrimaryAuthMode' field from version 11.0 onwards`

API v10.0 example:

```
"trustedMasterServerName": "String",
"authenticationType": "CREDENTIAL",
"userName": "String",
"password": "String",
"fingerprint": "String"
```

API v11.0 example:

```
"trustedMasterServerName": "String",
"authenticationType": "CREDENTIAL",
"userName": "String",
"password": "String",
"fingerprint": "String",
"remotePrimaryAuthMode":"String"
```

* Add scan host API: `POST /malware/scan-hosts`  
  new mandatory parameter `mediaServerName` has been added to the payload, which is used for validating the scan host before adding it

API v10.0 example:

```
{
  "data": {
    "type": "createScanHost",
    "attributes": {
      "hostName": "scanhost.example.com",
      "maxNoOfParallelScans": 0,
      "state": "ACTIVE",
      "scanHostCredentialName": "sample_creds"
    },
    "relationships": {
      "malwareTool": {
        "data": {
          "type": "malwareTool",
          "id": "1"
        }
      },
      "scanHostPool": {
        "data": {
          "type": "scanHostPool",
          "id": "2"
        }
      }
    }
  }
}
```

API v11.0 example:

```
{
  "data": {
    "type": "createScanHost",
    "attributes": {
      "hostName": "scanhost.example.com",
      "maxNoOfParallelScans": 0,
      "state": "ACTIVE",
      "scanHostCredentialName": "sample_creds",
      "mediaServerName": "mediaserver.example.com"
    },
    "relationships": {
      "malwareTool": {
        "data": {
          "type": "malwareTool",
          "id": "1"
        }
      },
      "scanHostPool": {
        "data": {
          "type": "scanHostPool",
          "id": "2"
        }
      }
    }
  }
}
```