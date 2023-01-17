# To install markdownx-4.0.0b1,
* pre-install: wheel
* pip install git+https://github.com/neutronX/django-markdownx.git

# To install through requrements.txt:
* git+https://github.com/neutronX/django-markdownx@5260f03
* <b>or</b>
* git+https://github.com/neutronX/django-markdownx@master

# To collect static files
* everytime you add static files into /static folder, run the command below:
* ```python3 manage.py collectstatic```
* to update and serve the latest files using gunicorn.