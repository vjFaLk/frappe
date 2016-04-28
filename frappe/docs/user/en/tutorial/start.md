# Starting the Bench

Now we can login and check if everything works.

To start the development server, run `bench start`

	$ bench start
	14:19:56 system           | watch.1 started (pid=21842)
	14:19:56 system           | redis_socketio.1 started (pid=21837)
	14:19:56 system           | worker_default.1 started (pid=21841)
	14:19:56 system           | worker_long.1 started (pid=21849)
	14:19:56 system           | web.1 started (pid=21844)


You can now open your browser and go to `http://localhost:8000`. You should see this login page if all goes well:

<img class="screenshot" alt="Login Screen" src="{{docs_base_url}}/assets/img/login.png">

Now login with : 

Login ID: **Administrator**

Password : **Use the password that was created during installation**

When you login, you should see the "Desk" home page

<img class="screenshot" alt="Desk" src="{{docs_base_url}}/assets/img/desk.png">

As you can see, the Frappe basic system comes with several pre-loaded applications like To Do, File Manager etc. These apps can integrated in your app workflow as we progress.

{next}
