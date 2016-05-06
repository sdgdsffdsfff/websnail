if [[ $1 == 'nohup' ]]; then
    nohup python manager.py runserver --host=0.0.0.0 --port=8899 &
    #nohup gunicorn -c gunicorn.py manager:app &
else
    python manager.py runserver --host=0.0.0.0 --port=8899
    #gunicorn -c gunicorn.py manager:app
fi
