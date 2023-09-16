from django.contrib.auth.models import User, Group
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

class test_UserGroups(APITestCase):
     
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        
        self.domain = 'localhost:8000'

        self.validUserPassword = 'pass1234'

        self.validUserManager = []

        validUserTemp = User.objects.create_user(
            email='manager@test.com', 
            username='mrManager', 
            password=self.validUserPassword)
        validUserTemp.groups.add(Group.objects.get_or_create(name='manager')[0])
        validUserTemp.save()

        self.validUserManager.append(validUserTemp)

        validUserTemp = User.objects.create_user(
            email='manager2@test.com', 
            username='mrManager2', 
            password=self.validUserPassword)
        validUserTemp.groups.add(Group.objects.get_or_create(name='manager')[0])
        validUserTemp.save()
        self.validUserManager.append(validUserTemp)

        self.validUserDCM = []
        validUserTemp = User.objects.create_user(
            email='deliver@test.com', 
            username='msDeliveryCrew', 
            password=self.validUserPassword)
        validUserTemp.groups.add(Group.objects.get_or_create(name='delivery-crew')[0])
        validUserTemp.save()
        self.validUserDCM.append(validUserTemp)

        validUserTemp = User.objects.create_user(
            email='deliver2@test.com', 
            username='msDeliveryCrew2', 
            password=self.validUserPassword)
        validUserTemp.groups.add(Group.objects.get_or_create(name='delivery-crew')[0])
        validUserTemp.save()
        self.validUserDCM.append(validUserTemp)

        self.validUserNoGroup =  User.objects.create_user(
            email='nogroup@test.com', 
            username='mrNoGroup', 
            password=self.validUserPassword)
        self.validUserNoGroup.save()

    def test_userbygroup_list(self):
        '''
        Test GET /api/groups/{group_name}/users
        '''
        url_managers = f"https://{self.domain}/api/groups/manager/users"
        url_dcm = f"https://{self.domain}/api/groups/delivery-crew/users"

        #WITH A MANAGER ROLE
        self.client.logout()
        self.client.force_login(user=self.validUserManager[0])
        #Get Users within Manager group  
        response = self.client.get(url_managers)
        self.assertEqual(response.status_code,  status.HTTP_200_OK)
        self.assertEqual(len(response.json()), len(self.validUserManager))
        for user in response.json():
            assert any(group['name'] == "manager" for group in user['groups']) == True

        #Get Users within delivery-crew group  
        response = self.client.get(url_dcm)
        self.assertEqual(response.status_code,  status.HTTP_200_OK)
        self.assertEqual(len(response.json()), len(self.validUserDCM))
        for user in response.json():
            assert any(group['name'] == "delivery-crew" for group in user['groups']) == True


        #WITH A DCM ROLE
        self.client.logout()
        self.client.force_login(user=self.validUserDCM[0])
        #Get Users within Manager group  
        response = self.client.get(url_managers)
        self.assertEqual(response.status_code,  status.HTTP_403_FORBIDDEN)

        #Get Users within delivery-crew group  
        response = self.client.get(url_dcm)
        self.assertEqual(response.status_code,  status.HTTP_403_FORBIDDEN)


        #UNAUTHENTIFIED
        self.client.logout()
        #Get Users within Manager group  
        response = self.client.get(url_managers)
        self.assertEqual(response.status_code,  status.HTTP_401_UNAUTHORIZED)

        #Get Users within delivery-crew group  
        response = self.client.get(url_dcm)
        self.assertEqual(response.status_code,  status.HTTP_401_UNAUTHORIZED)

    def test_userbygroup_post(self):
        '''
        Test POST /api/groups/{group_name}/users
        '''
        url_managers = f"https://{self.domain}/api/groups/manager/users"
        url_dcm = f"https://{self.domain}/api/groups/delivery-crew/users"

        data={
            'username':self.validUserNoGroup.username 
            }

        #WITH A MANAGER ROLE
        self.client.logout()
        self.client.force_login(user=self.validUserManager[0])

        #Get Users within Manager group  
        response = self.client.post(url_managers, data)
        self.assertEqual(response.status_code,  status.HTTP_201_CREATED)
        self.validUserNoGroup.refresh_from_db()
        self.assertTrue(any( group['name'] == 'manager' for group in self.validUserNoGroup.groups.contains('manager')))



