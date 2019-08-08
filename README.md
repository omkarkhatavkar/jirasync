
![](https://i.ibb.co/d4Y6Frs/2d524aa8-8c79-4562-bfd9-a3f8a85536df-200x200.png)

Jirasync is a CLI tool which collects all GitHub Issues, PR, PR_Reviews and Create them as Jira tasks. It will handle the whole lifecycle of jira task from Assigment => Adding to Current Sprint => Updating correct status. Currently, it is designed for a Single User and MultiUser who wants syncs his GitHub work history in Jira by running some commands.

![](https://raw.githubusercontent.com/omkarkhatavkar/jirasync/master/img/jirasync_1.gif)
 <p align="center">  
 Sync and Track your GitHub work with JIRA  
    <br />  
 <a href="https://github.com/omkarkhatavkar/jirasync
 "><strong>Explore the docs »</strong></a>  
 <br /> <br /> <a href="https://raw.githubusercontent.com/omkarkhatavkar/jirasync/master/img/jirasync_1.gif">View Demo</a>  
  ·  
    <a href="https://github.com/omkarkhatavkar/jirasync/issues">Report Bug</a>  
  ·  
    <a href="https://github.com/omkarkhatavkar/jirasync/issues">Request Feature</a>  
 </p></p>  
  
  
  
<!-- TABLE OF CONTENTS -->  
## Table of Contents  
  
* [About the Project](#about-the-project)  
* [Installation](#installation)  
* [Workflow](#workflow)
* [Usage](#usage)  
* [Contributing](#contributing)  
* [License](#license)  
* [Contact](#contact)  
  
  
  
<!-- ABOUT THE PROJECT -->  
## About The Project    

Jirasync is a CLI tool which collects all GitHub Issues, PR, PR_Reviews and tracks Jira tasks for those. Currently, it is only designed for a single user who syncs his GitHub work history in Jira by running some commands for an interval of a week.

#### Main Features 

-   See the list of work was done on GitHub and Redmine based on week and day interval.    
-   Sync and track your own github work in Jira running one command 
-   You can sync not only single user but also multiteam menmbers by configurating team.yaml
-  All pr_create, pr_reviews, issue_create has been added to sync with JIRA.
 
  <!-- ## Installation -->  
## Installation    

After install, make sure to run `jirasync set-config` successfully to set configuration.
#### From source

    $ git clone https://github.com/omkarkhatavkar/jirasync.git
    $ cd jirasync/
    $ chmod +x setup.sh
    $ source ./setup.sh

  <!-- ## Workflow -->  
## Workflow
#### GitHub Issue WorkFlow

-   If any new issue created by you in GitHub then is created in the JIRA backlog, by default is assigned to the same user in Jira so he can assign to correct user later.
    
-   If the issue is not new and if it is closed then the status is automatically updated.
    

![](https://i.ibb.co/9vTHbqh/9-IMMd-z-BXDY1-Oy-MZILx-NGZl-Ljxv-E3-Vuw-OIMS-Ir-PVmn-AUDx-IRGe8-XVXGT-2w-Yt-A3-U5-b0vj-Dq-Y6vyv-Kg1-Ied-AECU0nd-Dz-FJEFKt-QIg-FMu-Wvo-W2-P-lh14-Tz-FFo-D7-Bzh-N2-HGRH3kv.png)

Case1: Creating new GitHub issues to Jira

  

![](https://i.ibb.co/y5J3C8d/LEr6-Iy-G2-YKgta-OYk-EHSZ6jm-Qi3q-S-cw-HI3-Dk-Fx-Eb-AThln2ye-Ad154yq1b-TCm6l-Nk0l-Ba-Hh-n-Mpr0-Ul-Mj5-XT7-K9-PZR9-Arc-HLW084-FGu3-SM-p-Sp-NAF2-CQPG2-Xq-BD4-C0-R8-FGBCX6if.png)

Case2: Issues status is automatically updated once issue closed in GitHub    

## PR WorkFlow:

-   If any new PR created by you in GitHub then new task created in the JIRA for Current Sprint, by default is assigned to the same user in Jira.
    
-   Once Github PR gets merged then the same Jira Task will be moved to ‘Done’ status.
    

  

![](hGttps://lh6.googleusercontent.com/Qqy_LIJ0N9oQ6zDg673D5VA_uJKsM_jid1GBLPdPTuEFLia3fpvdu1gb4lgG3nV3GzWQM8EMTEozxjHB_NJ1Uhsq9ffOIeYeVaWWsM3RxZCZpbh2xsZYU1w0li70DjDKZ0frm5Cq)

Case3: Auto PR Create/Closed (Done) manage by Jirasync

  

#### PR_Review WorkFlow:

-   If you review PR and approve the PR, then the Jira Task is created for review in the current sprint.
    
-   Once reviewed PR get merged then the Jira task will be moved to ‘Done’ status
    

  

![](https://i.ibb.co/V31G52W/tsm8ouwkvh-W4-Sekx3w-Yu-WYqx-P4-Iypo-EK0-Vli-NHELSV2a3g4n-Bs95ivcd6e5-Vk-D2-Mrw-Sgmcd5-Et-ZKHNw5-H4g-Ah8t0-O-p-Cccgh8-Ao-ZI2h-Md5s-OI3-fgb-MIZPz8mxd-FDVOWqtjd-Du-Ay.png)

####  Note:

-   All Jira tasks are uniquely identified as projectname#pr/pr_review/issue#id.
    
    ## Usage 
    #### Commands
	  ```bash
	(env) [root@okhatavk jirasync]# jirasync --help
	Usage: jirasync [OPTIONS] COMMAND [ARGS]...

	  This CLI tool to sync and track GitHub issues, pr's, pr_reviews with Jira.
	  Currently supported to only for create, update and close status.

	Options:
	  --debug / --no-debug
	  --help                Show this message and exit.

	Commands:
	  check-github-history  see github work history result based on intervals...
	  set-config            Set configuration in jirasync before start using it
	  show-team-history     see github work history for a team based on...
	  start-syncing         sync github issues, pr, pr_reviews as jira tasks
	                        for...
	  start-syncing-team    sync github issues, pr, pr_reviews as jira tasks
	                        for...

	```
	#### Basic usage
	Set Configuration:  This is the first step, where you can setup your jirasync.
	 ```bash
	 # jirasync set-config --help
	Usage: jirasync set-config [OPTIONS]

	  Set configuration in jirasync before start using it

	Options:
	  --git-urls TEXT         Pass the git project names for Jira sync e.g.
	                          airgun, robottelo
	  --jira-url TEXT         Pass the Jira url
	  --github-username TEXT  Pass GitHub username
	  --github-token TEXT     Pass GitHub token
	  --jira-username TEXT    Pass Jira username
	  --jira-email-id TEXT    Pass Jira Email Id
	  --jira-board TEXT       Pass the Jira board name
	  --jira-project TEXT     Pass the Jira project name
	  --help                  Show this message and exit.

	 ```
	  
	 Start-Syncing: Sync github issues, pr, pr_reviews as jira tasks for individual user.
	``` bash
	(env) [root@okhatavk jirasync]# jirasync start-syncing --help 
	Usage: jirasync start-syncing [OPTIONS]

	  sync github issues, pr, pr_reviews as jira tasks for individual user.
	  currently supported day and week interval e.g. jirasync start-syncing
	  --interval week

	Options:
	  --interval TEXT  please pass interval e.g. week, day
	  --help           Show this message and exit. 
	  ```
	Start-Syncing: Sync github issues, pr, pr_reviews as jira tasks for whole team. Before that make sure that team.yaml should exist with correct data (for format use team_sample.yaml)
	```bash 
	(env) [root@okhatavk jirasync]# jirasync start-syncing-team --help 
	Usage: jirasync start-syncing-team [OPTIONS]

	  sync github issues, pr, pr_reviews as jira tasks for whole team. currently
	  supported day and week interval for all users mentioned in team.yaml e.g.
	  jirasync start-syncing-team --interval week

	Options:
	  --interval TEXT  please pass interval e.g. week, day
	  --help           Show this message and exit. ```

  
## Contributing

#### Bug Reports & Feature Requests

Please use the [issue tracker](https://github.com/omkarkhatavkar/jirasync/issues) to report any bugs or file feature requests.

#### Developing

PRs are welcome. To begin developing, do this:

```bash
$ git https://github.com/omkarkhatavkar/jirasync.git
$ cd jirasync
$ chmod +x setup.sh
$ source ./setup.sh
```

<!-- LICENSE -->  
## License  
  
Distributed under the MIT License. See `LICENSE` for more information.  
  
  
  
<!-- CONTACT -->  
## Contact  
  
Project Link: [https://github.com/omkarkhatavkar/jirasync](https://github.com/omkarkhatavkar/jirasync)  
  
	 
	
