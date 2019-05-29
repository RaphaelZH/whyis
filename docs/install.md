# Install Whyis

The Whyis installer is layered, which allows for maximum flexibility. Each layer is runnable by itself, resulting in a functional Whyis.

If you do not have Ubuntu 16.04, please use VirtualBox, VMWare, or another virtualization tool to create a VM with Ubuntu 16.04 installed. Whyis requires at least 4 GB of memory and 30GB of disk space.

- **Layer 2: Shell Script** If you already have a virtual machine provisioned, or want to directly install Whyis onto an Ubuntu 16.04 server directly, you can use the Layer 2 shell script. It is a simple script, `install.sh`, that installs Puppet and the needed modules, and then runs the Layer 1 Puppet script.
- **Layer 1: Puppet** [Puppet](https://puppet.com/) is a flexible devops tool that automates the configuration and provisioning of servers, both virtual and physical. The script `manifests/install.pp` can be used directly by current Puppet users that want to incorporate Whyis deployment into their existing Puppet infrastructure.

** Whyis installations are currently supported on Ubuntu 16.04. **


## Layer 2: Install into an Ubuntu 16.04 system

This is useful for deploying production knowledge graphs, or for developers who already have a machine (virtual or otherwise) that is ready to run Whyis. Currently, we only support installing on Ubuntu 16.04.

```
bash < <(curl -skL https://raw.githubusercontent.com/tetherless-world/whyis/release/install.sh)
```

To install using the development branch of Whyis, use the master install script:

```
bash < <(curl -skL https://raw.githubusercontent.com/tetherless-world/whyis/master/install.sh)
```
## How to Create an Ubuntu 16.04 Virtual Machine with Virtualbox

### Download ISO file

Download the ISO file for Ubuntu Server 16.04 from: https://www.ubuntu.com/download/server.

### Create a new Ubuntu Virtual Machine

From VM VirtualBox Manager, Select "New" to create a new VM.

In the following window, name your VM and select Type Linux and Version Ubuntu.

Choose the desired memory and space settings, and complete the VM creation.

### Load the ISO
Before starting the newly created VM, right click the VM and go to its Settings.

Under Storage, select Controller IDE and specify your ISO file. Press Ok to save the settings.

Now, when you start the VM, it should install a new Ubuntu desktop. You can now just follow the instructions for installing Whyis onto a Ubuntu system.

# Administrative Tasks

To peform the following administrative tasks, you need to connect to the VM (if you're not running directly):

```
vagrant ssh
```

Once you are in the server, you need to change to the **whyis** user, go to the whyis app directory, and activate the python virtual environment:

```
sudo su - whyis
cd /apps/whyis
source venv/bin/activate
```

### Configure Whyis
**If you are using an existing whyis knowledge graph, this step is not needed.  Instead, go to the install instructions for the graph you wish to install.**

Whyis is built on the Flask web framework, and most of the Flask authentication options are available to configure in Whyis.
A configuration script will walk you through the configuration process and make a project directory for you. 
Change the default values as needed. The SECRET_KEY and SECURITY_PASSWORD_SALT are randomly generated at runtime, so you shouldn't need to change those.

```
$ python manage.py configure
project_name [My Knowledge Graph]: 
project_short_description [An example knowledge graph configuration.]: 
project_slug [my_knowledge_graph]: 
location [/apps/my_knowledge_graph]: 
author [J. Doe]: 
email [j.doe@example.com]: 
linked_data_prefix [http://localhost]: 
version [0.1]: 
packages []: 
SECRET_KEY [J00F5f80rGSbvpUo9oBFAtksmrd7ef8u]: 
SECURITY_PASSWORD_SALT [JDyCyPu0KEu/fdJr4CbG65VhCtGugwCu]: 
$ 
```

This will create a project skeleton for you at `location` (here, `/apps/my_knowledge_graph`). The files are:

* **config.py** - Main configuration file for Whyis.
* **vocab.ttl** - Vocabulary file for configuring custom Whyis views.
* **templates/** - Directory for storing Whyis view templates.
* **my_knowledge_graph/** - Project source directory. Put any python code in here.
  * **agent.py** - An empty inference agent module.
* **static/** - Files that are served up at `{linked_data_prefix}/cdn/` as static files.
  * **css/** - Project-specific CSS files.
    * **my_knowledge_graph.css** - Default empty project-specific CSS file.
  * **html/** - Project-specific static HTML files, like for Angular.js templates.
  * **js/** - Project-specific javascript files.
    * **my_knowledge_graph.js** - Default empty project-specific javascript file.
* **setup.py** - File for installation using pip.

Change directories into the project dir and install it into your virtualenv. Be sure your virtualenv is activated first:

```
$ cd /apps/my_knowledge_graph
$ pip install -e .
```

Restart apache and celeryd as a privileged user (not whyis) to have the configuration take effect:

```
$ sudo service apache2 restart
$ sudo service celeryd restart
```

### Add a User

Registration is available on the website for users, but it's easy to add a user to the knowledge graph from the command line. 
Perform this task as the `whyis` user from the `/apps/whyis` directory.
Use `--roles=admin` to make the user an administrator.

```
$ python manage.py createuser -e <email> -p <password (can change later)> -f <First Name> -l <Last Name -u <user handle> --roles=admin
```

### Modify a User

You can change the roles a user has from the command line as well, but you'll need their user handle. 
For instance, you can add a user to a role like this:

```
$ python manage.py updateuser -u <user handle> --add_roles=admin
```

You can remove them from a role like this:

```
$ python manage.py updateuser -u <user handle> --remove_roles=admin
```

Changing a password is also simple:

```
$ python manage.py updateuser -u <user handle> -p <new password>
```

### Run in development mode

Whyis can be run on a different port to enable debugging. You will see output from the log in the console and will be able to examine stack traces inside the browser.

```
$ python manage.py runserver -h 0.0.0.0
```

### Loading Knowledge

Knowledge can be added to Whyis using a command as well. This can be used to inject states that trigger larger-scale knowledge ingestion using [SETLr](https://github.com/tetherless-world/setlr/wiki/SETLr-Tutorial), or can simply add manually curated knowledge. 
If the RDF format supports named graphs, and the graphs are nanopublications, the nanopublications will be added as-is.
If there are no explicit nanopublications, or if the RDF format is triples-only, each graph (including the default one), is treated as a separate nanopublication assertion.
The PublicationInfo will contain some minimal provenance about the load, and each assertion will be the graphs contained in the file.

```
$ python manage.py load -i <input file> -f <turtle|trig|json-ld|xml|nquads|nt|rdfa>
```

## [Next: Creating Whyis Views](views)
