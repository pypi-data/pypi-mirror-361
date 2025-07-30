# magma-auth
Python package for MAGMA Authentication

## Import module
```python
from magma_auth import auth
```

### Login using username and password
This will save (encrypted) your username and password.
```python
auth.login(
    username="<NIP>",
    password="<PASSWORD>",
    use_token=True, # Will try to look up saved token
    verbose=True
)
```
After logged in for the first time, you can log in without using username and password. You can use `auto()` method to
log in.
```python
auth.auto()
```
### Get your token
```python
token = auth.token
```
### Decode your token
```python
auth.decode(token)
```
### Get expired token
```python
auth.expired_at
```
### Get token from saved file
This method can be used after logged in for the first time.
```python
token = auth.load_token()
```
### Validate and check your token
This will check and validate token from MAGMA server.
```python
auth.validate_token(token)
```