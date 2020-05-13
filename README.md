# Asfour

Asfour is simple messaging app built on the Twilio API, and grown out of a more mature (and more complicated) communications platform, [zwazo](https://github.com/acounsel/zwazo). 

## Getting Started

It's best to use python virtualenv to build locally


```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Prerequisites

Asfour is built in Python3.7 using django (2.2) and deployed on Heroku

```
Boto3
django
django-crispy-forms
django-extensions
django-heroku
django-storages
gunicorn
sendgrid
twilio
```

### Installation and Deployment

Run the following commands to clone the app and deploy to Heroku

Say what the step will be

```
git clone https://github.com/saraabi/asfour.git
cd asfour
heroku create
git push heroku master
heroku open
```

## Built With

* [Django](https://www.djangoproject.com/) - Web framework
* [Heroku](https://www.heroku.com/) - Hosting

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/saraabi/asfour/tags). 

## Authors

* **Samer Araabi** - *Initial work* - [Accountability Counsel](https://www.accountabilitycounsel.org/)
* **Marisa Lenci** - *Support* - [Accountability Counsel](https://www.accountabilitycounsel.org/)

See also the list of [contributors](https://github.com/saraabi/asfour/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Thanks to the Arab Resource and Organizing Center for inspriring the build.
