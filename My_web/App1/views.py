# from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth.models import auth
from django.contrib import messages
from .models.lob_opt import LOB
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from tablib import Dataset
from django.utils.safestring import mark_safe
# from django.db import connection
from .models.bucket import Bucket
from django.contrib.auth.models import User
from .models.userRole import UserRole
from .models.mev import Mev
from .models.MEV_var import MevVar
from .models.micro_pairs import MicroPair
from .models.other_input import OtherInput
import requests
import datetime
from django.utils import timezone
import pandas as pd
import json
import copy
import sys
from .models.hfc_status_validation import Hfc_Status_Validation
sys.path.append(r'C:\Users\Administrator\Documents\pythoncode\ECL_Testing')
import Perform_Regression_v1, Perform_Regression_v2
import Get_Portfolio_Data
# from Perform_Regression_v1 import Connect_To_Database
import Generate_ECL_v1, Generate_ECL_v2


Lob = None
imported_data, imported_data2, imported_data3, imported_data4, report_date, role = 'None','None','None','None','None','None'
month_dict = {'01':'January','02':'February','03':'March','04':'April','05':'May','06':'June','07':'July','08': 'August','09':'September','10':'October','11':'November','12':'December'}

# Create your views here.
@login_required
def selected(request):
    if request.method == 'POST':
        value_id = request.session.get('Role')
        print(value_id,'option Id')
        print(request.user.get_username())
        print(request.user.id)
        User_id = request.user.id
        val = request.POST.get('option')
        role = UserRole.objects.filter(UserId =User_id).values('RoleId')
        role_id =str(role[0].get('RoleId'))
        print(type(value_id))
        print(type(role_id))
        global Lob
        Lob = val
        # return HttpResponse('<h1>Get {}</h1>'.format(val))
        return render(request, 'home.html', {'opt': val})
    else:
        print('checked error')


@login_required
def show_options(request):
    print('Show option execute')
    results = LOB.objects.all()
    User_id = request.user.id
    print((User_id))
    role = UserRole.objects.filter(UserId=User_id).values('RoleId')
    print(role)
    if not role:
        return HttpResponse('<h2>Admin have no role</h2>')
    role = role[0].get('RoleId')
    print(role)
    lob = LOB.objects.filter(id = role).values('options')
    if not lob:
        lob = None
    lob = lob[0].get('options')
    print(lob)
    request.session['Role'] = lob
    option={}
    option['username'] = request.user.get_username()
    option['role'] = lob
    print(option)
    return render(request, "index.html", option)


def login(request):
    print('login page called')
    if request.method == 'POST':
        print('Post request execute')
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)

        if user is not None:

            request.session['userName']=user.username
            request.session['userId'] = user.id
            User_id = request.user.id
            role = UserRole.objects.filter(UserId=User_id).values('RoleId')
            auth.login(request, user)
            return redirect('index')
        else:
            messages.info(request, 'Invalid credentials')
            return redirect('login')
    else:
        print('unauthorized user')
        return render(request, 'login.html')


@login_required
def view_report(request):
    return render(request, 'home2.html')


@login_required
def home(request):
    return render(request, 'home.html')


@login_required
def index(request):
    return render(request, 'Index.html')


# Code add from regression
from sqlalchemy import create_engine
ConfigJSONFilePath = "C:/Users/Administrator/Documents/pythoncode/report_rendering_poc/Env_Configuration.json"
TableDetailsJSONFilePath = "C:/Users/Administrator/Documents/pythoncode/ECL_Testing/TableDetails.json"

# Reading the table details from JSON file (this will have the required queries)
# with open(TableDetailsJSONFilePath, 'r') as file:
#     TableDetails_JSON = json.loads(file.read())
#     TableDetails_List = TableDetails_JSON["Data"]
#     TableDetails_df = pd.DataFrame(TableDetails_List)


def Connect_To_Database():
    global engine, Connection

    # Reading Config JSON file
    with open(ConfigJSONFilePath, 'r') as file:
        ConfigDetails = json.loads(file.read())
        # print(ConfigDetails)

    UserName = ConfigDetails["EnvironmentParams"]["UserName"]
    Password = ConfigDetails["EnvironmentParams"]["Password"]
    HostName = ConfigDetails["EnvironmentParams"]["HostName"]
    Port = ConfigDetails["EnvironmentParams"]["Port"]
    Database = ConfigDetails["EnvironmentParams"]["Database"]

    # Establishing the connection
    ConnectionPath = 'postgresql://' + UserName + ':' + Password + '@' + HostName + ':' + str(Port) + '/' + Database
    engine = create_engine(ConnectionPath)
    Connection = engine.connect()

    print("Connected to Database")


def check_leap(req_year):
    year = int(req_year)
    if(year % 4) == 0:
        if (year % 100) == 0:
            if (year % 400) == 0:
                print("{0} is a leap year".format(year))
                return True
            else:
                print("{0} is not a leap year".format(year))
                return False
        else:
            print("{0} is a leap year".format(year))
            return True

    else:
        print("{0} is not a leap year".format(year))
        return False


def date_formate(req_date):
    date_dict ={'01':'01-31','03':'03-31','04':'04-30','05':'05-31','06':'06-30','07':'07-31','08':'08-31','09':'09-30','10':'10-31','11':'11-30','12':'12-31'}
    date_list = req_date.split('-')
    if date_list[0]=='02':
        check = check_leap(date_list[-1])
        if check:
            date_req = '02-29'
        else:
            date_req = '02-28'
        date_req = date_list[-1] + '-' + date_req
        return date_req
    else:
        date_req = date_dict[date_list[0]]
        date_req = date_list[-1]+'-'+date_req
        return date_req


# end here
def cal_view(request):
    if request.method == 'POST' or request.method == 'GET':
        print(request.POST.get('date'))
        date_index = request.POST.get('date')
        if date_index == None:
            date_index = request.session.get('report_date')
            print(date_index,'from session change')
            request.session['report_date'] = date_index
            date_change = date_index
        else:
            date_change = date_formate(date_index)
            request.session['report_date']= date_change
        # LoB = (request.session.get('Role'))
        role = request.session.get('Role')
        # print(LoB)
        print(date_change)
        flag = Hfc_Status_Validation.objects.filter(Report_date=date_change).filter(LoB=role).values('Flag')
        print(flag)
        if flag.exists():
            # print('No flag')
            flag = (flag[0].get('Flag'))

            print(flag)
            if flag == 'E':
                # re_flag['flag']='Y'
                # messages.info(request,
                #               'Regression already performed for reporting date : {}'.format(report_date))
                reporting_date = (request.session.get('report_date'))
                print(request.session.get('userName'))
                LoB = (request.session.get('Role'))
                gen_Report = Generate_ECL_v2.main(date_change, LoB, 'NA', 'E')
                Hfc_Status_Validation.objects.filter(Report_date=date_change).update(Flag='E')
                print(gen_Report)
                jsonReport = json.dumps(gen_Report)
                jsonReport = json.loads(jsonReport)
                for key, value in request.session.items():
                    print('{} => {}'.format(key, value))
                print('*' * 50)
                msg = month_dict.get(date_change.split('-')[-2])+' '+date_change.split('-')[0]
                print(msg)
                return render(request, 'report.html', {'report': jsonReport,'date':msg})

            elif flag == 'Y':
                report_date = date_change
                messages.info(request,
                              'file already exist and Regression is done for reporting date :{} but Generate ECL is '
                              'pending'.format(report_date))

                return render(request,'upload_Y.html')
            elif flag == 'N' or flag == 'n':
                # re_flag['flag'] = 'N'
                messages.info(request,
                              'file already exist for reporting date :{} but regression is pending'.format(date_change))
                return render(request,'upload_N.html')

            return render(request, 'reupload.html', re_flag)
        else:
            return render(request,'test.html')
            # return HttpResponse("<h1>No files are available Please First upload required files")
            # data={'report':report_date}
            # print('No flag available')
            # return render(request,'upload.html',data)

        # month_dict = {'01':'January','02':'February','03':'March','04':'April','05':'May','06':'June','07':'July','08': 'August','09':'September','10':'October','11':'November','12':'December'}
        # month_value = date_change.split('-')[-2]
        # month_detail = month_dict[month_value]+' '+date_change.split('-')[0]
        # return HttpResponse('View report paged')


def cal(request):
    # print(request.POST.get('date'))
    # date_index = request.POST.get('date')
    # date_change = date_formate(date_index)
    # print(date_change)
    # cursor = connection.cursor()
    # cursor.execute("SELECT * FROM App1_Bucket where id=2")
    # row = cursor.fetchall()
    # print('*'*20)
    # print(row)
    # print('*' * 20)
    # connect with redshift and insert demmy data into db
    Connect_To_Database()
    # print(Connection)
    # cursor = Connection.cursor()
    # print(cursor)
    # data_df = {'empid':[10, 11, 12], 'empname': ['xyz', 'abc', 'dfg'], 'depname': ['adm', 'hr', 'it']}
    # mydata = pd.DataFrame(data_df)
    # mydata.to_sql('ecl_test',con=engine, if_exists='append',index=False)
    data = engine.execute("SELECT * FROM ecl_test")
    row = data.fetchall()
    # print(row)
    # end here
    print('*' * 20)
    print(row)
    print('*' * 20)
    Connection.close()
    if request.method == 'POST':
        print(request.POST.get('date'))
        date_index = request.POST.get('date')
        date_change = date_formate(date_index)
        request.session['report_date'] = date_change
        # request.session['index_date']= date_change
        print(date_change)
        month_dict = {'01':'January','02':'February','03':'March','04':'April','05':'May','06':'June','07':'July','08': 'August','09':'September','10':'October','11':'November','12':'December'}
        month_value = date_change.split('-')[-2]
        month_detail = month_dict[month_value]+' '+date_change.split('-')[0]
        # data 1
        # resp2 = Bucket.objects.all()
        # buck = {'data':resp2}
        # return render(request, 'data2.html',buck)
        # data 2
        # table_json,table2_json =Perform_Regression_v1.main('SME',"2020-10-31")
        # print('*'*50)
        # print(table_json)
        # print('*'*50)
        # print(table2_json)
        # print(request.POST.get('date'))
        # print(request.POST)
        data_resp = Get_Portfolio_Data.main(date_change,request.session.get('Role'))
        print(type(data_resp))
        # if isinstance(data_resp, list):
        #     print('list type response')
        #     data_resp = json.dumps(data_resp)
        # else:
        #     print('undefinde')
        data_resp = json.dumps(data_resp)
        print(data_resp,'data from function')
        # data_resp = open(r'C:\Users\Administrator\Desktop\LOB_Data.json').read()
        # print(data_resp)
        jsonData = json.loads(data_resp)
        # resp = requests.get('https://api.covid19api.com/countries').json()
        # print(jsonData)
        return render(request,'index.html',{'result':jsonData,'month': month_detail})
        # role =(request.session.get('Role'))
        # return HttpResponse("<h1>Get date {} to funtion and LOB option {}</h1>".format(request.POST.get('date'),role))


def regre(request):
    if request.method == 'GET':
        report_date1=(request.session.get('report_date'))
        reg_flag = Hfc_Status_Validation.objects.filter(Report_date=report_date1).values('Flag')
        print(reg_flag,'*'*50)
        flag = reg_flag[0].get('Flag')
        # table_json, table2_json = Perform_Regression_v1.main('SME',"2020-10-31")
        # table_json, table2_json = Perform_Regression_v2.main('SME', "2020-10-31", flag) use this for automate pass Flag
        table_json, table2_json = Perform_Regression_v2.main('SME', "2020-10-31", 'Y')
        # print(table_json)
        print(type(table_json))
        # data_resp = open(r'C:\Users\DELL\Desktop\res.json').read()
        # print(data_resp)
        # code due to v2
        table_json = json.dumps(table_json)
        table2_json = json.dumps(table2_json)
        jsonData = json.loads(table_json)
        jsonData2 = json.loads(table2_json)
        print(jsonData,'@'*20)
        print(jsonData2, '@'*20)
        option_list=[]
        for i in jsonData2[0]:
            # print(i)
            option_list.append(i)
        option_list = option_list[1:]
        print(option_list)
        # for i in jsonData[0]:
        #     print(i)
        # resp = requests.get('https://api.covid19api.com/countries').json()
        print(jsonData)
        print(request.session.get('report_date'),'from sessiiii')
        print(Hfc_Status_Validation.objects.filter(Report_date=request.session.get('report_date')))
        Hfc_Status_Validation.objects.filter(Report_date=request.session.get('report_date')).update(Flag='Y')
        return render(request,'regression_report.html',{'result':jsonData,'option':option_list,'result2':jsonData2})
        # role =(request.session.get('Role'))
        # return HttpResponse("<h1>Get date {} to funtion and LOB option {}</h1>".format(request.POST.get('date'),role))


def flag_check(request):
    global report_date, role
    role = request.session.get('Role')
    if request.method == 'POST':
        report_date = request.POST.get('date')

        # date_index = request.POST.get('date')
        report_date = date_formate(report_date)
        print(report_date)
        request.session['report_date'] = report_date
        print(request.session.get('report_date'),'date from session')
        print(report_date,role,'passssssss')
        flag = Hfc_Status_Validation.objects.filter(Report_date=report_date).filter(LoB=role).values('Flag')
        # flag = 'y'
        # print(flag)
        re_flag = {}
        data = {'report': report_date}
        # if flag:
        if flag.exists():
            print('No flag')
            flag = (flag[0].get('Flag'))

            print(flag)
            if flag == 'y' or flag == 'Y':
                re_flag['flag']='Y'
                mon_msg = month_dict.get(report_date.split('-')[-2])+' '+report_date.split('-')[0]
                messages.info(request,
                              'Regression is performed for reporting date : {} but ECL is yet to be generated'.format(mon_msg))
                return render(request,'upload_Y.html')
            elif flag == 'E':
                re_flag['flag']='E'
                messages.info(request,
                              'ECL result is already generated for reporting date : {}'.format(report_date))
                return render(request,'upload_E.html')

            elif flag == 'N' or flag == 'n':
                re_flag['flag'] = 'N'
                messages.info(request,
                              'file already exist for reporting date :{} but regression is pending'.format(report_date))
                return render(request,'upload_N.html')

            return render(request, 'reupload.html', re_flag)
        else:
            # data={'report':report_date}
            print('No flag available')
            return render(request,'upload.html',data)



def reupload(request):
    report_date = request.session.get('report_date')
    # request.session['reupload_flag'] = 'True'
    data = {'report': report_date, 'reupload_flag': 1}
    return render(request, 'upload.html',data)


def convertion_df(file):
    fileread = pd.read_excel(file)
    data_frame = pd.DataFrame(fileread)
    return data_frame


def get_list(df):
    lst = []
    for col in df.columns:
        lst.append(col)
    return lst


def upload(request):
    global imported_data, imported_data2, imported_data3, imported_data4, report_date, role
    report_date=request.session.get('report_date')
    if request.method == 'POST':
        print(request.POST,'from post request')
        # report_date =(request.POST.get('date'))
        report_date = (request.session.get('report_date'))
        role = request.session.get('Role')
        # request.session['report_date'] = report_date
        for key, value in request.session.items():
            print('{} => {}'.format(key, value))
        # print(request.session.get('report_date'),'from session')
        # person_resource = PersonResource()
        dataset = Dataset()
        dataset2 = Dataset()
        dataset3 = Dataset()
        dataset4 = Dataset()
        # print(len(request.FILES['myfile1']))
        # request.FILES.get('filepath', False)
        new_persons = request.FILES.get('myfile', False)
        # print(new_persons)

        new_MEVsce = request.FILES.get('myfile1', False)
        new_MicroPair = request.FILES.get('myfile3',False)
        new_OtherInput = request.FILES.get('myfile4', False)
        if new_persons is not False:
            new_persons = request.FILES['myfile']
        else:
            print('no first file ')
            new_persons = None

        if new_MEVsce is not False:
            new_MEVsce = request.FILES['myfile1']
        else:
            print('no second file ')
            new_MEVsce = None

        if new_MicroPair is not False:
            new_MicroPair = request.FILES['myfile3']
        else:
            print('no third file ')
            new_MicroPair = None

        if new_OtherInput is not False:
            new_OtherInput = request.FILES['myfile4']
        else:
            print('no Fourth file ')
            new_OtherInput = None
        print(new_persons,'/'*20)
        import copy

        dummy1 = copy.deepcopy(new_persons)
        dummy2 = copy.deepcopy(new_MEVsce)
        dummy3 = copy.deepcopy(new_MicroPair)
        dummy4 = copy.deepcopy(new_OtherInput)
        # print(dummy4,'dimmy file')
        print(type(dummy1))
        if dummy1 != None:
            df1 = pd.read_excel(dummy1)
            print(len(df1.columns), '=' * 20)
            lst1 = get_list(df1)
            imported_data = dataset.load(new_persons.read(), format='xlsx')
            flag1 = 1
        else:
            flag1 = 0
            print('File1 is not supplied')
            pass

        if dummy2 != None:
            df2 = pd.read_excel(dummy2)
            print(len(df2.columns), '=' * 20)
            lst2 = get_list(df2)
            imported_data2 = dataset2.load(new_MEVsce.read(), format='xlsx')
            flag2 = 1
        else:
            flag2 = 0
            print('File2 is not supplied')
            pass

        if dummy3 != None:
            df3 = pd.read_excel(dummy3)
            print(len(df3.columns), '=' * 20)
            lst3 = get_list(df3)
            imported_data3 = dataset3.load(new_MicroPair.read(), format='xlsx')
            flag3 = 1
        else:
            flag3 = 0
            print('File3 is not supplied')
            pass

        if dummy4 != None:
            df4 = pd.read_excel(dummy4)
            print(len(df4.columns), '=' * 20)
            lst4 = get_list(df4)
            imported_data4 = dataset4.load(new_OtherInput.read(), format='xlsx')
            flag4 = 1
        else:
            flag4 = 0
            print('File4 is not supplied')
            pass
        # df2 = pd.read_excel(dummy2)
        # df3 = pd.read_excel(dummy3)
        # df4 = pd.read_excel(dummy4)
        # print(len(df1.columns),'='*20)
        # print(df1.isnull().sum().sum())
        # print(len(df2.columns), '=' * 20)
        # print(len(df3.columns), '=' * 20)
        # print(len(df4.columns), '=' * 20)
        # lst1=get_list(df1)
        # lst2 = get_list(df2)
        # lst3 = get_list(df3)
        # lst4 = get_list(df4)
        # fileread=pd.read_excel(dummy4)
        # print(df,'4'*20)
        # dataf = pd.DataFrame(fileread)
        # dataf["reporting date"] = report_date
        # print((dataf.head(1)),'14545454')

        # imported_data = dataset.load(new_persons.read(), format='xlsx')
        # imported_data2 = dataset2.load(new_MEVsce.read(), format='xlsx')
        # imported_data3 = dataset3.load(new_MicroPair.read(), format='xlsx')
        # imported_data4 = dataset4.load(new_OtherInput.read(), format='xlsx')
        print(type(imported_data))
        print(imported_data2)
        check_Mev = Mev.objects.filter(Reporting_date=report_date)
        # if check_Mev:
        #     flag = Hfc_Status_Validation.objects.filter(Report_date=report_date).filter(LoB=role).values('Flag')
        #     flag = (flag[0].get('Flag'))
        #     if flag == 'y' or flag=='Y':
        #         messages.info(request,'Regression already performed on that data which reporting date : {}'.format(report_date))
        #     else:
        #         messages.info(request,'file already exist for reporting date :{} but regression is pending'.format(report_date))
        #
        #     return render(request,'reupload.html')
        # else:
        #     print('No previous data')
            # reupload_file(imported_data, imported_data2, imported_data3, imported_data4, report_date, role)
        check_Mev = Mev.objects.filter(Reporting_date=report_date).delete()
        print('Data delete from DB')
        check_MevSce = MevVar.objects.filter(Reporting_date=report_date).filter(LOB=role).delete()
        check_M_pair = MicroPair.objects.filter(Reporting_date=report_date).delete()
        check_OtherInput = OtherInput.objects.filter(Reporting_date=report_date).delete()
        # print(check)
        try:
            if flag1 ==1:
                if len(lst1) != 6 and df1.isnull.sum().sum > 0:
                    messages.info(request,'<strong>File Upload Error:</strong> Please check the file "MEV Multipliers" \nError Detail: Unidentified column found')
                    return render(request, 'file_error.html')
                for data in imported_data:
                    print(data)
                    x = timezone.now()
                    # x = datetime.datetime.now()
                    # print(Bucket)
                    values = Mev(
                        data[0],
                        data[1],
                        data[2],
                        data[3],
                        data[4],
                        data[5],
                        report_date,
                        role,
                        x,

                    )
                    values.save()
            else:
                pass
        except Exception as e:
            print(e)
            messages.error(request, mark_safe("<strong>File Upload Error:</strong> Please check the file 'MEV Multipliers' and re-upload again.<br/>Error Detail: Blank values found"))
            # messages.info(request, 'File Upload Error: Please check the file "MEV Multipliers"\n\nError Detail: Unidentified column found')
            # messages.info(request,'File Upload Error: Please check the file "MEV Multipliers"\n\nError Detail: Unidentified column found')
            return render(request, 'file_error.html')
        try:
            if flag2 == 1 :
                if len(lst2)!=3 and (df2.isnull().sum().sum()) == 0:
                    messages.error(request, mark_safe(
                        "<strong>File Upload Error:</strong> Please check the file 'Shocks to micro economic variables' and re-upload again.<br/>Error Detail: Wrong File"))
                    # messages.info(request, 'Please check Second file and re-upload it')
                    return render(request, 'file_error.html')
                for data in imported_data2:
                    print(data)
                    x = timezone.now()
                    # x = datetime.datetime.now()
                    # print(Bucket)
                    values = MevVar(
                        data[0],
                        data[1],
                        data[2],
                        report_date,
                        role,
                        x,

                    )
                    values.save()
            else:
                pass
        except:
            messages.error(request, mark_safe(
                "<strong>File Upload Error:</strong> Please check the file 'Shocks to micro economic variables' and re-upload again.<br/>Error Detail: Wrong File"))
            # messages.info(request, 'Please check Second file and re-upload it')
            return render(request, 'file_error.html')

        try:
            if flag3 == 1:
                if len(lst3)!=3 and (df3.isnull().sum().sum()) == 0:
                    messages.error(request, mark_safe(
                        "<strong>File Upload Error:</strong> Please check the file 'Pairs for multivariate regression' and re-upload again.<br/>Error Detail: Wrong File"))
                    # messages.info(request, 'Please check Third file and re-upload it')
                    return render(request, 'file_error.html')

                for data in imported_data3:
                    print(data)
                    x = timezone.now()
                    # x = datetime.datetime.now()
                    # print(Bucket)
                    values = MicroPair(
                        data[0],
                        data[1],
                        data[2],
                        report_date,
                        role,
                        x,

                    )
                    values.save()
            else:
                pass
        except:
            messages.error(request, mark_safe(
                "<strong>File Upload Error:</strong> Please check the file 'Pairs for multivariate regression' and re-upload again.<br/>Error Detail: Wrong File"))
            # messages.info(request, 'Please check Third file and re-upload it')
            return render(request, 'file_error.html')

        try:
            if flag4 == 1:
                # print(lst4,'4'*40)
                if len(lst4)!=2 and (df4.isnull().sum().sum()) == 0:
                    messages.error(request, mark_safe(
                        "<strong>File Upload Error:</strong> Please check the file 'Other inputs' and re-upload again.<br/>Error Detail: Wrong File"))
                    # messages.info(request, 'Please check Fourth file and re-upload it')
                    return render(request, 'file_error.html')
                for data in imported_data4:
                    print(data)
                    x = timezone.now()
                    # x = datetime.datetime.now()
                    # print(Bucket)
                    values = OtherInput(
                        data[0],
                        data[1],
                        report_date,
                        role,
                        x,

                    )
                    values.save()
            else:
                pass
        except:
            messages.error(request, mark_safe(
                "<strong>File Upload Error:</strong> Please check the file 'Other inputs' and re-upload again.<br/>Error Detail: Wrong File"))
            # messages.info(request, 'Please check Fourth file and re-upload it')
            return render(request, 'file_error.html')

        flag_status = Hfc_Status_Validation.objects.filter(Report_date=report_date).filter(LoB=role)
        if flag_status:
            Hfc_Status_Validation.objects.filter(Report_date=report_date).update(Flag='N')
        else:
            valid_flag = Hfc_Status_Validation(LoB=role, Report_date=report_date, Flag='N')
            valid_flag.save()
        return redirect('uploaded_success')
        # result = person_resource.import_data(dataset, dry_run=True)  # Test the data import

        # if not result.has_errors():
        #    person_resource.import_data(dataset, dry_run=False)  # Actually import now
    else:
        return render(request, 'Flag_check.html')
    # return redirect('uploaded_success')


# return redirect('uploaded_success')

    #     check_Mev = Mev.objects.filter(Reporting_date = report_date).delete()
    #     check_MevSce = MevVar.objects.filter(Reporting_date = report_date).filter(LOB=role).delete()
    #     check_M_pair = MicroPair.objects.filter(Reporting_date = report_date).delete()
    #     check_OtherInput = OtherInput.objects.filter(Reporting_date=report_date).delete()
    #     # print(check)
    #     for data in imported_data:
    #         print(data)
    #         x = datetime.datetime.now()
    #         # print(Bucket)
    #         values = Mev(
    #             data[0],
    #             data[1],
    #             data[2],
    #             data[3],
    #             data[4],
    #             data[5],
    #             report_date,
    #             role,
    #             x,
    #
    #
    #         )
    #         values.save()
    #
    #     for data in imported_data2:
    #         print(data)
    #         x = datetime.datetime.now()
    #         # print(Bucket)
    #         values = MevVar(
    #             data[0],
    #             data[1],
    #             data[2],
    #             report_date,
    #             role,
    #             x,
    #
    #         )
    #         values.save()
    #
    #     for data in imported_data3:
    #         print(data)
    #         x = datetime.datetime.now()
    #         # print(Bucket)
    #         values = MicroPair(
    #             data[0],
    #             data[1],
    #             data[2],
    #             report_date,
    #             role,
    #             x,
    #
    #         )
    #         values.save()
    #
    #     for data in imported_data4:
    #         print(data)
    #         x = datetime.datetime.now()
    #         # print(Bucket)
    #         values = OtherInput(
    #             data[0],
    #             data[1],
    #             report_date,
    #             role,
    #             x,
    #
    #         )
    #         values.save()
    #     return redirect('uploaded_success')
    #         # result = person_resource.import_data(dataset, dry_run=True)  # Test the data import
    #
    #     # if not result.has_errors():
    #     #    person_resource.import_data(dataset, dry_run=False)  # Actually import now
    # return render(request, 'upload.html')
    # # return redirect('uploaded_success')


def reupload_file(request):
    global imported_data, imported_data2, imported_data3, imported_data4, report_date, role
    print(imported_data, imported_data2, imported_data3, imported_data4, report_date, role)
    check_Mev = Mev.objects.filter(Reporting_date=report_date).delete()
    print('Data delete from DB')
    check_MevSce = MevVar.objects.filter(Reporting_date=report_date).filter(LOB=role).delete()
    check_M_pair = MicroPair.objects.filter(Reporting_date=report_date).delete()
    check_OtherInput = OtherInput.objects.filter(Reporting_date=report_date).delete()
    # print(check)
    for data in imported_data:
        print(data)
        x = datetime.datetime.now()
        # print(Bucket)
        values = Mev(
            data[0],
            data[1],
            data[2],
            data[3],
            data[4],
            data[5],
            report_date,
            role,
            x,

        )
        values.save()

    for data in imported_data2:
        print(data)
        x = datetime.datetime.now()
        # print(Bucket)
        values = MevVar(
            data[0],
            data[1],
            data[2],
            report_date,
            role,
            x,

        )
        values.save()

    for data in imported_data3:
        print(data)
        x = datetime.datetime.now()
        # print(Bucket)
        values = MicroPair(
            data[0],
            data[1],
            data[2],
            report_date,
            role,
            x,

        )
        values.save()

    for data in imported_data4:
        print(data)
        x = datetime.datetime.now()
        # print(Bucket)
        values = OtherInput(
            data[0],
            data[1],
            report_date,
            role,
            x,

        )
        values.save()
    Hfc_Status_Validation.objects.filter(Report_date=report_date).update(Flag='N')
    return redirect('uploaded_success')


def logout(request):
    auth.logout(request)
    messages.success(request,'Successfully logged out')
    return redirect('login')


def uploaded_success(request):
    print(request.session.get('report_date'))
    return render(request,'regression.html')


def generate_report(request):
    if request.method=='POST':
        print('*'*50)
        print(request)
        reg_var = request.POST.get('option')
        print(reg_var)
        reporting_date = (request.session.get('report_date'))
        print(request.session.get('userName'))
        LoB= (request.session.get('Role'))
        gen_Report = Generate_ECL_v1.main(reporting_date,LoB,reg_var)
        Hfc_Status_Validation.objects.filter(Report_date=reporting_date).update(Flag='E')
        print(gen_Report)
        jsonReport = json.loads(gen_Report)
        for key, value in request.session.items():
            print('{} => {}'.format(key, value))
        print('*'*50)
        msg = month_dict.get(reporting_date.split('-')[-2]) + ' ' + reporting_date.split('-')[0]
        return render(request, 'report.html', {'report':jsonReport,'mev':reg_var,'date':msg})


import os
from django.conf import settings
from django.http import HttpResponse, Http404


def download(request):
    # file_path = os.path.join(settings.MEDIA_ROOT, path)
    file_path = r'C:\Users\Administrator\Documents\pythoncode\ECL_Testing\OutputFiles\Regression_Results.csv'
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404


def chart(request):
    data = {'Python': 15, 'JavaScript': 12, 'PHP': 8, 'Java': 19, 'C#': 11, 'C++': 18}
    label =[]
    val =[]
    data_rep ={}
    for i in data:
        label.append(i)
        val.append(data[i])
        data_rep['labels'] = label
        # data_rep['range'] = val
    print(label)
    print(val)
    # (request, 'report.html', {'report':jsonReport,'mev':reg_var,'date':msg})
    return render(request, 'chart.html', {'labels1':label, 'value': val})
