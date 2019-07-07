# NoteKfet 2020
## Installation sur un serveur

On supposera pour la suite que vous utiliser debian/ubuntu sur un serveur tout nu ou bien configuré.

1. Paquets nécessaires

    $ sudo apt install nginx python3 python3-pip python3-dev uwsgi
    $ sudo apt install uwsgi-plugin-python3 python3-virtualenv git

2. Clonage du dépot

    on se met au bon endroit :

        $ cd /var/www/
        $ mkdir note_kfet
        $ cd note_kfet
        $ git clone git@gitlab.crans.org:bde/nk20.git .
3. Environment Virtuel
   
   À la racine du projet:

        $ virtualenv env
        $ source /env/bin/activate
        (env)$ pip install -r requirements.txt
        (env)$ deactivate

4. uwsgi  et Nginx

    On utilise uwsgi et Nginx pour gérer le coté serveu :

        $ sudo ln -s /var/www/note_kfet/nginx_note.conf /etc/nginx/sites-enabled/
        
   **Modifier la config nginx  pour l'adapter à votre server!**
   
   Si l'on a un emperor (plusieurs instance uwsgi):
    
        $ sudo ln -s /var/www/note_kfet/uwsgi_note.ini /etc/uwsgi/sites/

    Sinon: 
        
        $ sudo ln -s /var/www/note_kfet/uwsgi_note.ini /etc/uwsgi/apps-enabled/
5. Base de données

    Pour le moment c'est du sqllite, pas de config particulière.
    
## Développer en local

Il est tout a fait possible de travailler en local, vive `./manage.py runserver` !

## Cahier des Charges 

Il est disponible [ici][https://wiki.crans.org/NoteKfet/NoteKfet2018/CdC]. 

## Documentation

La documentation est générée par django et son module admindocs. **Commenter votre code !*
