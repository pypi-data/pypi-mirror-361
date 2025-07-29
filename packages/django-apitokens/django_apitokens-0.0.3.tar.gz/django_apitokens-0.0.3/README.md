# django-apitokens

Generate tokens compatible with Django Restframework (`drf`) from your Django Admin view:
- Create new tokens at will (after being generated, they no longer can be reversed, since only a digest is stored in the database).
- Add expirity dates (supports time and date)
- Remove tokens when you no longer need them.

## My Token view

![Screenshot 2023-03-21 at 14 47 02](https://user-images.githubusercontent.com/7786556/226643622-893b631d-d353-4833-8def-78f61ea77561.png)


## Add token view

![Screenshot 2023-03-21 at 14 47 19](https://user-images.githubusercontent.com/7786556/226643580-ac761fd7-91a9-4c5c-898b-4cc1daf9d812.png)


# Install

- Install the python package: `pip install django-apitokens` 
- Add `apitokens` to your Django installed apps:

```python
# In your settings.py
INSTALLED_APPS = [
    ...
    'apitokens',
]
```

- Ensure you are using `knox` `TokenAuthentication` class:

```python
# In your settings.py
REST_FRAMEWORK = {
    ...,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'knox.auth.TokenAuthentication',
        ...,
    ),
    ...,
}
```

- You are set to use tokens generated through this app as a way to login with the DRF framework.

# Contributing

To contribute code to this app, ensure you're following the [community guidelines](https://github.com/surface-security/guidelines#contributing)
