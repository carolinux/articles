#How to install Python 2.7 on CentOS with Anaconda

###Introduction

The CentOS family of Linux distributions is widely used by enterprises to house applications. It is a popular distribution because it's free to use without the need for a license and because the feature-freeze practices applied during the release cycle guarantee long-term stability. 

The price for stability is that the operating system ships with certain libraries that are quite out of date for the use by applications, as is the case for Python which is found in CentOS distributions at versions 2.6 or even lower. If a developer needs a higher version of Python, they need to compile and install it themselves.

However, it's important to leave the already installed Python intact, because the operating system requires it for internal use, for instance for its package manager (yum). The most common thing that can go wrong is that the developer, by trying to install the new Python version, manages to corrupt the system (just Google for "installing Python 2.7 on CentOS broke my yum").

 For that reason, instead of building Python by hand, it makes sense to use an existing tool that can manage Python installations without tampering with the system Python which is installed at */usr/bin/python* and instead installs the new version side-by-side with the old one. A relatively new but already widely-used tool for managing Python installations is Anaconda by [Continuum.io](http://www.continuum.io) which makes building Python quite easy.

###Prerequisites
A machine running CentOS 6.4.

##Install Python

First we need to choose a directory where the new Python binaries will be installed. Let's say that this is */usr/local/miniconda*.
We can install Python 2.7 using the following commands: 

<!--code lang=bash linenums=true-->
    wget https://repo.continuum.io/miniconda/Miniconda-3.0.0-Linux-x86_64.sh # download the install script
    sh Miniconda-3.0.0-Linux-x86_64.sh -b -p /usr/local/miniconda # may or may not need sudo depending on the file access settings of the target directory

### Add Python 2.7 to the PATH
If it is desirable for us to launch the newly installed Python when typing 'python' in the shell, then we need to add this line to the *~/.bashrc* file of all the users that have a need for this behavior (for instance, the user our webserver runs as).

<!--code lang=bash linenums=true-->
    export PATH=/usr/local/miniconda/bin:$PATH # prepend the new binaries to the path

After editing the *bashrc* file, run the following to make the changes take effect immediately.

<!--code lang=bash linenums=true-->
    source ~/.bashrc

 Users that don't have this in their profiles will call system Python instead. Yum will always call system Python because the path */usr/bin/python* is hardcoded in its source code. So unless we a try to create a symlink to this path or replace the binary, the package manager will keep working fine.

### Create aliases
If we don't want to override the 'python' command, we can also create aliases in *bashrc* for 'python2.7' and 'python2.6'. This will require us to explicitly say which version we want to use every time.

<!--code lang=bash linenums=true-->
    alias python2.7="/usr/local/miniconda/bin/python"
    alias python2.6="/usr/bin/python"


### Install Pip

If our server houses a django application, chances are we also need to install pip for managing our packages. The goal is to have pip install the new packages for Python2.7 installed in /usr/local/miniconda and not for the system Python. It is possible to do this with one line (assuming we added python 2.7 in the path in the previous section).

<!--code lang=bash linenums=true-->
    conda install pip

To verify that it worked do:

<!--code lang=bash linenums=true-->
    which pip
    /usr/local/miniconda/bin/pip


