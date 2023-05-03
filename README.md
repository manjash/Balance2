The objective of the project is the implement a user `Balance` microservice for a marketplace platform to enable additional functionality for the payment and reporting systems.  
The `Balance` microservice supports
- Adding and withdrawing money from the user balance
- Transferring money from one user balance to another
- Reserving money off the user balance (reserved amount can be authorised, captured to a dedicated account and refunded), in connection with the product / service order the reservation is done for. 
- Report generation with product / service orders details on monthly basis 


In addition to the immediate `Balance` microservice functionality, some basic operations with orders, transactions and products / services were added to emulate (to a certain extent) the `Balance` microservice behaviour in the real world payment system.

Main endpoints available in the `Balance` service:

### Adding amount to balance
```
POST /api/v1/balance/moneyIn
```

```console
request_body = {
  "user_id": "string",
  "amount": int
}
```

### Reserving balance
Reserving balance amount for a particular product / service purchase
```
POST /api/v1/balance/reserve
```

```console
request_body = {
  "user_id": "string",
  "service_product_id": "string",
  "order_id": "string",
  "amount": int
}
```

### Reconciliation of the reserved balance amount
```
POST /api/v1/balance/reserve/capture
```


```console
request_body = {
  "user_id": "string",
  "service_product_id": "string",
  "order_id": "string",
  "amount": 0
}
```

### Cancellation / refund of the reserved balance
Cancellation / refund of the reserved amount from the balance
```
POST /api/v1/balance/reserve/capture/refund
```

If the amount is still authorised, the reservation is released and the amount is returned to the balance account.
If the amount has already been captured, the funds are returned to the balance account. 

```console
request_body = {
  "user_id": "string",
  "service_product_id": "string",
  "order_id": "string",
  "amount": 0
}
```

### Get particular user's balance
```
GET /api/v1/balance/getBalance/{user_id}
```


### Generate accountant report for the services purchased

**!NB:** there is no restriction for other payment methods to be used to make a service / product purchase. The report represents all purchases regardless of the payment method, but filtering to purchases made through balance is possible if needed.


```
POST /api/v1/balance/accountantReport
```
Report is generated per particular month.
Enter year and month in yyyymm format (string).

```console
request_body = "yyyymm"
```

The structure of the report:

| Service Title   | Sum           |
|:----------------|:--------------|
| Title           | Sum per title |


# Launch the service

### Prerequisites:
- Docker

### To launch the service:
- download the repository
- in your terminal go to `\balance` folder and type

```console
$ docker-compose build
```

When the build is complete, do

```console
$ docker-compose up -d
```

### Endpoints in action

To see the endpoints in actions, you can use `Postman`, `curl` or any other similar system of your choice.

### Authentication for Postman querying

`GET` request to `http://127.0.0.1/api/v1/login/oauth`, with `username` and `password` as params.

Set up autorefresh by using OAuth2 option in `Authorization`:
```console
Grant Type:             Password Credentials
Access Token URL:       http://127.0.0.1/api/v1/login/oauth
Username:               FIRST_SUPERUSER
Password:               FIRST_SUPERUSER_PASSWORD
Client Authentication:  Send as Basic Auth Header
```


### Full api documentation

Please see http://localhost/docs with autogenerated Swagger UI representation. 