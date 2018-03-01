# -*- coding: utf-8 -*-
"""
Archives HipChat 1-1 Chats
Initial Version: Bruno Marcuche 2017

"""
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import os
import urllib2
import json
from time import sleep
import datetime
import csv
import optparse
import glob
import tarfile

def flush_out(filename):
    ''' flush print buffer '''
    sys.stdout.write("\r\x1b[Kexporting to: "+filename.__str__())
    sys.stdout.flush()

class HipChat(object):
    ''' helper class for hipchat api '''

    def __init__(self, token):
        self.token = token
        self.users_dict = {}
        self.path = '/var/tmp/hipchat_logs'

    def get_url(self, max_results, start_index, uid=0):
        ''' build history url '''
        date_from = "1999-10-03T15:33:30+01:00"
        date_to = 'T'.join(str(datetime.datetime.now()).split(" "))
        if uid != 0:
            params = "/%s/history?auth_token=%s" % (uid, self.token)
        else:
            params = "?auth_token=%s" % self.token
        url = "https://api.hipchat.com/v2/user%s" % params
        try:
            uri = "&reverse=true&max-results=%s&start-index=%s&date=%s&end-date&%s" \
            % (max_results, start_index, date_to, date_from)
            nurl = url + uri
        except TypeError as type_error:
            print type_error
        except urllib2.HTTPError:
            nurl = url
        return nurl

    def get_json(self, url):
        ''' query api; returns json '''
        sleep(3)
        try:
            req = urllib2.Request(url)
            req.add_header("Content-Type", "application/json; charset=utf-8")
            req.add_header("Authorization", "Bearer " + self.token)
            content = urllib2.urlopen(req)
            # lost hipchat access before adding rate limiting per headers
            #rate_remaining = int(content.info().getheader('X-Ratelimit-Remaining'))
            #rate_reset_epoch = float(content.info().getheader('X-Ratelimit-Reset'))
            jsondata = json.load(content)
        except urllib2.HTTPError as http_error:
            jsondata = 'bad url: %s\n%s' % (http_error, url)
        return jsondata

    def get_users(self):
        ''' get users; returns json '''
        all_users_url = self.get_url(1000, 0)
        all_users = self.get_json(all_users_url)
        return all_users

    def get_user_ids(self):
        ''' get dict of all user ids in format {user_id:'User Name'} '''
        users = self.get_users()
        self.users_dict = dict((
            x['id'],
            x['name']
            )
                               for x in users['items'])
        return self.users_dict

    def get_user(self, username):
        ''' get user dict by name '''
        self.users_dict = self.get_user_ids()
        return {k: v for k, v in self.users_dict.items() if v == username}

    def get_save_file(self, c_user, ext):
        ''' set up file for saving '''
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        return '%s/%s_hipchat_log.%s' % (self.path, c_user, ext)

    def clean_up(self):
        ''' clean up hipchat log directory '''
        try:
            for files in glob.glob('%s/*.*' % self.path):
                os.remove(files)
        except OSError:
            pass

    def archive(self):
        ''' create archive '''
        archive_path = self.path + os.sep + "hipchat_logs.tar.gz"
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(self.path)
        print 'archive written: %s' % archive_path

if __name__ == '__main__':
    USE_MSG = "usage: %prog -k <APIKEY> [export format]"
    PARSER = optparse.OptionParser(usage=USE_MSG, version="%prog 1.0")
    PARSER.add_option('-n', '--name', dest='name', default=None, action='store', type='str',
                      help='export specific user')
    PARSER.add_option('-k', '--apikey', dest='apikey', default=None, action='store', type='str',
                      help='hipchat api key')
    PARSER.add_option('-c', '--csv', dest='csv', default=False, action='store_true',
                      help='export to csv')
    PARSER.add_option('-j', '--json', dest='json', default=False, action='store_true',
                      help='export to json')
    PARSER.add_option('-p', '--path', dest='export_path', default=None, action='store', type='str',
                      help='hipchat log export path')
    PARSER.add_option('-z', '--archive', dest='archive', default=False, action='store_true',
                      help='compress logs directory')
    OPTIONS, ARGS = PARSER.parse_args()
    try:
        MY_TOKEN = os.environ["MY_HIPCHAT_TOKEN"]
    except KeyError:
        MY_TOKEN = OPTIONS.apikey
    if MY_TOKEN is None:
        MSG = """

        API token was not passed via cmdline and could not
        find an API token exported under MY_HIPCHAT_TOKEN

        To continue, Please:

        use -k <API_KEY> to pass a valid API key

        or

        export MY_HIPCHAT_TOKEN=<API_KEY>

        To create a new API key

           a) Sign In: https://<your-company>.hipchat.com/account/api

           b) Create new token with the following scopes:
              - View Group
              - View Messages
        """
        PARSER.error(MSG)
    ARCHIVE = OPTIONS.archive
    USERNAME = OPTIONS.name
    USE_CSV = OPTIONS.csv
    USE_JSON = OPTIONS.json
    EXPORT_PATH = OPTIONS.export_path
    if USE_CSV is False and USE_JSON is False:
        MSG = """

        Please specify at least one export method

        See --help for details
        """
        PARSER.error(MSG)
    HIP = HipChat(MY_TOKEN)
    if EXPORT_PATH is not None:
        HIP.path = EXPORT_PATH
    HIP.clean_up()
    if USERNAME is not None:
        USER_IDS = HIP.get_user(USERNAME)
    else:
        USER_IDS = HIP.get_user_ids()
    if USER_IDS == {}:
        print 'Could not find specified user: %s' % USERNAME
        print 'Try one of these names'
        print [v for k, v in HIP.get_user_ids().items()]
    for user_id, user_name in USER_IDS.items():
        chat_user = '_'.join(user_name.split(' ')).lower()
        histo_range = [int('%s' % y + "001") for y in [x for x in xrange(0, 30)] if y != 0]
        histo_range.insert(0, 0)
        histo_urls = [HIP.get_url(1000, hrange, user_id) for hrange in histo_range]
        for histo_url in histo_urls:
            json_history = HIP.get_json(histo_url)
            if json_history['items'] == []:
                break
            elif USE_CSV is True:
                extension = 'csv'
                save_file = HIP.get_save_file(chat_user, extension)
                with open(save_file, 'a') as csv_out:
                    csv_w = csv.writer(csv_out)
                    header = ['date', 'from', 'id', 'mentions', 'message', 'message_format', 'type']
                    csv_w.writerow(header)
                    for history in json_history['items']:
                        if history['message'] is not None:
                            fields = [str(x) for x in [history['date'],
                                                       history['from'],
                                                       history['id'],
                                                       history['mentions'],
                                                       history['message'],
                                                       history['message_format']]]
                            csv_w.writerow(fields)
            flush_out(save_file)
            if USE_JSON is True:
                extension = 'json'
                save_file = HIP.get_save_file(chat_user, extension)
                with open(save_file, 'a') as json_out:
                    json.dump(json_history, json_out)
                    flush_out(save_file)
    if ARCHIVE is True:
        HIP.archive()
