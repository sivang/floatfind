The soft-float enabled debian repository
========================================
In order to correctly support our current hardware architecture (mips little endian) we had to create
a debian repository that is software floating point enabled. That is, contains software packages specifically
built for the mipsel architecture with software floating point support.

The floatfind/trunk directory contains utility scripts that help maintain and extend the repository.

The repository is hosted on a removable large mobile hard drive that is usually connected through
a USB interface to the machine referred to as the 'build cluster'. This machine is basically an LX
host, that has its root filesystem on the mobile hard drive. The root filesystem is of the Debian
GNU/Linux distributions and serves as a build machine for packages we need to rebuild to support
software floating point.  The OS installation there already has all the toolchain needed to compile
software with soft-float support, and is setup to use parallel building across two PCs that have 
a cross-toolchain for MIPSel installed on them in order to speed up large builds.


Using The Repository
====================
To use the repository in in a client, add the following line to the client's /etc/apt/sources.list file:

deb http://tigershark.NET9.RnD/myrepo lenny contrib main non-free

After that, update your package cache by doing:

$ apt-get update

Watch the update process syncing up against the repository.

Then, you are ready to install packages from the repository:

$ apt-get install [pkg-name]

If the package you were trying to install was not found, you need to rebuild it for software floating 
point support. Read on the next section.

Extending The Repository
========================
Extending the repository means by this order:

 1. Building the missing package in question, this sometimes entails fetching build dependencies and
    building them as needed. Note that the build cluster already contains most of the base build dependencies.

 2. Building runtime dependencies , which in turn might require building dependencies of dependencis until satisfied.

 3. Adding the newly built runtime dependencies and the newly built package to the repository, using the addfloat.py script.

 4. Go back to 'Using The Repository' and install the package in question, this time all its dependencies should be pulled
    in automatically and you should be able to use to software on the client.


Building Only Hard-float Packages
=================================
Note, that before going and building the package and its dependencies you can check if it uses hardware floating point
operations in the first place, and thus rebuild only that portion of the packages instead of blindly rebuilding all of them.
To do that, you can use the utility script 'checkfloat.py'. Consult its source to understand its usage as it contains 
inline documentation along side the code.

How To Build Packages On The Buildcluster
=========================================
Building of package on the buildcluster is done using an ssh session to the host. to start an ssh session to the host do
$ ssh 192.168.9.159 -lroot
You will be asked for the password, enter '1234' and press [ENTER]

Once logged on follow this steps to maintain a tidy directory structure for the builds:

1. cd /builds/BUILDS
2. mkdir [pkg-name] (this directory will hold the build of this package)
3. cd [pkg-name]
4. apt-get source [pkg-name] (this will fetch the debian source that we will use to build the software)

Then cd to the source directory, usually looks something like:

5. cd packagename-x.y.z (where x.y.z is a version number)

Now edit the file ./debian/rules , see if its header contains anything similar to:

nclude /usr/share/cdbs/1/rules/debhelper.mk
include /usr/share/cdbs/1/rules/simple-patchsys.mk
include /usr/share/cdbs/1/class/gnome.mk
include /usr/share/cdbs/1/rules/utils.mk

(The gnome.mk entry is not mandatory and it's okay if it is omitted)

This means the package is using CDBS, a debian build system. Debian build systems were created
to ease the creation of packages that require lots of boiler-plate code to build. The build system
already has this code plus some additions. These make it easier to build a package and by providing a set
of make scripts and snippets you need to include from your 'rules' file to utilize the automation provided
by the build system. 

So, if the package is using CDBS, then the CDBS on the buildcluster was already modified to automatically support
parallel builds, so you need to do nothing to enable it.

If ./debian/rules seems like a regular make file without the special CDBS then make sure you find the main '$(MAKE)' statement,
usually under the 'build' or 'binary' targets and modify it such that make will spawn multiple builds that will utilize the other
nodes available for building. Change the make line to look like this:

$(MAKE) -j 10

This will tell make to spawn 10 parellel build processes which will utilize the other nodes in the cluster setup and will speed up
builds of large software.

After this is down you are ready to build the package, make sure you're in the packagename-x.y.z directory, and then execute:

$ debuild -us -uc -nc -b

This will start the build process, apply any neccessary patches from the debian source (usually stored at ./debian/patches) , run 
configure and make accordingly and will leave you, once finished with a binary package of the software in question. After
building is finished you are ready to actually install and use the package and also add it to our soft-float debian repository.

To install the freshly built package(s) from the dir where you ran the build process:

$ dpkg -i ../*.deb

To add the newly built package(s) to the repository use the addfloat.py script:

$ cd ..

(now you're in the upper dir, e.g. /builds/BUILDS/pkg-name)

$ addfloat.py -all

This will glob for all the *.deb packages, and add them one by one to the repository, removing packages that has the same version number
to make sure only the soft-float version is in the repository.

Removing a File From The Repository
===================================
As you are logged in to the buildcluster, issue:

$ removedeb.py [pkgname] to remove a package from the soft-float repository

Recreation Of The Setup
=======================
The physical storage of the repository is a large mobile hard drive connected to an LX machine serving as the buildcluster.
IP Address of this machine: 192.168.9.159
The path to the repository: /builds/myrepo (this is the top level directory for the repository)
The buildcluster machine is exporting this path via NFS, this allows the http serving machine (tigershark) to mount it
over nfs and thus provide a directory entry that is symlinked from the tigershark machine:

sivan@tigershark:/var/www$ ls -la | grep myrepo
lrwxrwxrwx  1 root root   25 2008-04-21 10:22 myrepo -> /home/sivan/builds/myrepo

Notice that this sym link is from the /var/www folder on the tigershark vm, which is the document root of the
apache web server.


the /home/sivan/builds directory is mounted via NFS:

sivan@tigershark:~$ mount | grep builds
192.168.9.159:/builds on /home/sivan/builds type nfs (rw,addr=192.168.9.159)

The tigershark virtual machine, which responds to the IP address: 192.168.9.139 is serving the HTTP requests to the repository.

The tigershark has a web server (Apache) installed to serve those http requests, to install it on a new machine:
$ sudo apt-get install apache


