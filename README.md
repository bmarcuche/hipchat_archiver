hipchat_archiver.py
=================

This script allows archiving of HipChat 1-1 chats.

Usage 
------

```python hipchat_archiver.py [options]```

Options
------
```
  --version                              show program's version number and exit
  -h, --help                             show this help message and exit
  -n NAME, --name=NAME                   export specific user
  -k APIKEY, --apikey=APIKEY
                                         hipchat api key
  -c, --csv                              export to csv
  -j, --json                             export to json
  -p EXPORT_PATH, --path=EXPORT_PATH     hipchat log export path
  -z, --archive                          compress logs directory
```

Running
------
*(needed)*

1) grant access to api

a) sign in: https://<yourcompany>.hipchat.com/account/api
   
b) create new token with the following scopes:  View Group, View Messages

*(optional)*

2) export hipchat token
   
a) export MY_HIPCHAT_TOKEN=<APIKEY>

(note) if you skipped step 2, provide the API token using the -k switch

Examples
------

 #### generate csv and json output for all 1-1 chats
 ```python hipchat_exporter.py -k <APIKEY> --csv --archive```

 ##### generate csv and json output for all 1-1 chats
  ```python hipchat_exporter.py -k <APIKEY> --json --csv --archive```

 ##### generate csv and json output for 1-1 chats with specific user
  ```python hipchat_exporter.py -k <APIKEY> --json --csv --archive -n "Bruno Marcuche"```


Known Issues
--------

This script has been tested on CentOS 6.8, 6.9, Linux Mint 17.3 and Windows 10 WLS.
I no longer have access to hipchat servers to troubleshoot or enhance this.
