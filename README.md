# hypy

This is a straightforward API module for [Hypothes.is](https://web.hypothes.is/).  
[See the Hypothes.is API documentation](https://h.readthedocs.io/en/latest/api-reference/) for details of parameters available.

## Requirements

- requests

## Example Usage

```
from hypy import AnnotationAPI

h = AnnotationAPI('developerAPIKey')

a = h.profile() #retrieve info of authenticated user

a = h.get(id) #retrieve annotation

results = h.search(arg1=...,arg2=...) #search for
annotations with arg1, arg2, ... as query parameters

results = h.list() #list authenticated user's annotations

a = h.create(json) #create an annotation from a json dict

a = h.update(id,arg1=...,arg2=...) #update an annotation
with arg1, arg2, ... in request body

response = h.delete(id)
```

All responses are json `dict`s, or list of `dict`s.

## Not implemented

- OAuth authentication
- API methods: Groups
- API methods: Users
