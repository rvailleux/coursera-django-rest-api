from django.contrib.auth.models import User, Group
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

class test_UserGroups(APITestCase):
     
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        
        self.domain = 'localhost:8000'

        self.validUserPassword = 'pass1234'

        self.valid_user_managers = []

        self.manager_group = Group.objects.create(name='manager')
        self.manager_group.save()

        self.dc_group = Group.objects.create(name='delivery-crew')
        self.dc_group.save()

        valid_user_temp = User.objects.create_user(
            email='manager@test.com', 
            username='mrManager', 
            password=self.validUserPassword)
        valid_user_temp.groups.add(self.manager_group)
        valid_user_temp.save()

        self.valid_user_managers.append(valid_user_temp)

        valid_user_temp = User.objects.create_user(
            email='manager2@test.com', 
            username='mrManager2', 
            password=self.validUserPassword)
        valid_user_temp.groups.add(self.manager_group)
        valid_user_temp.save()
        self.valid_user_managers.append(valid_user_temp)

        self.valid_user_dcms = []
        valid_user_temp = User.objects.create_user(
            email='deliver@test.com', 
            username='msDeliveryCrew', 
            password=self.validUserPassword)
        valid_user_temp.groups.add(self.dc_group)
        valid_user_temp.save()
        self.valid_user_dcms.append(valid_user_temp)

        valid_user_temp = User.objects.create_user(
            email='deliver2@test.com', 
            username='msDeliveryCrew2', 
            password=self.validUserPassword)
        valid_user_temp.groups.add(self.dc_group)
        valid_user_temp.save()
        self.valid_user_dcms.append(valid_user_temp)

        self.valid_user_no_group_customer =  User.objects.create_user(
            email='nogroup@test.com', 
            username='mrNoGroup', 
            password=self.validUserPassword)
        self.valid_user_no_group_customer.save()

    def test_userbygroup_list(self):
        '''
        Test GET /api/groups/{group_name}/users
        '''
        url_managers = f"https://{self.domain}/api/groups/manager/users"
        url_dcm = f"https://{self.domain}/api/groups/delivery-crew/users"

        #WITH A MANAGER ROLE
        self.client.logout()
        self.client.force_login(user=self.valid_user_managers[0])
        #Get Users within Manager group  
        response = self.client.get(url_managers)
        self.assertEqual(response.status_code,  status.HTTP_200_OK)
        returned_user_ids = {int(user['id']) for user in response.json()}
        valid_user_manager_ids = {user.id for user in self.valid_user_managers}
        self.assertSetEqual(returned_user_ids, valid_user_manager_ids)

        #Get Users within delivery-crew group  
        response = self.client.get(url_dcm)
        self.assertEqual(response.status_code,  status.HTTP_200_OK)
        returned_user_ids = {int(user['id']) for user in response.json()}
        valid_user_dcm_ids = {user.id for user in self.valid_user_dcms}
        self.assertSetEqual(returned_user_ids, valid_user_dcm_ids)

        #WITH A DCM ROLE
        self.client.logout()
        self.client.force_login(user=self.valid_user_dcms[0])
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



        def test_add_to_group(client:APIClient, user_to_be_added:User, group_to_be_added_to:Group, expected_assertion:bool, expected_return_code:status):
            data={
                'username': f"{user_to_be_added.username}"
            }

            url = f"https://{self.domain}/api/groups/{group_to_be_added_to.name}/users"

            assert group_to_be_added_to not in user_to_be_added.groups.all()

            ## Add a user to manager group
            response = client.post(url, data)
            self.assertEqual(response.status_code,  expected_return_code)
            user_to_be_added.refresh_from_db()
            assert (group_to_be_added_to in user_to_be_added.groups.all()) == expected_assertion
            user_to_be_added.groups.clear()
            user_to_be_added.save()

        #WITH A UNAUTHENTICATED CLIENT - NOK
        self.client.logout()
        test_add_to_group(self.client, self.valid_user_no_group_customer, self.manager_group, False, status.HTTP_401_UNAUTHORIZED)
        test_add_to_group(self.client, self.valid_user_no_group_customer, self.dc_group, False, status.HTTP_401_UNAUTHORIZED)

        #WITH A DCM ROLE - NOK
        self.client.logout()
        self.client.force_login(user=self.valid_user_dcms[0])
        test_add_to_group(self.client, self.valid_user_no_group_customer, self.manager_group, False, status.HTTP_403_FORBIDDEN)
        test_add_to_group(self.client, self.valid_user_no_group_customer, self.dc_group, False, status.HTTP_403_FORBIDDEN)

        #WITH A MANAGER ROLE - OK
        self.client.logout()
        self.client.force_login(user=self.valid_user_managers[0])
        test_add_to_group(self.client, self.valid_user_no_group_customer, self.manager_group, True, status.HTTP_201_CREATED)
        test_add_to_group(self.client, self.valid_user_no_group_customer, self.dc_group, True, status.HTTP_201_CREATED)

        # no data or wrong data for user data
        url = f"https://{self.domain}/api/groups/manager/users"
        data={
                'username': "fakeusername"
            }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code,  status.HTTP_404_NOT_FOUND)

        data={
                'username': ""
            }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code,  status.HTTP_404_NOT_FOUND)

        #wrong group provided 
        url = f"https://{self.domain}/api/groups/fakegroupname/users"
        data={
                'username': f"{self.valid_user_managers[0].username}"
            }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code,  status.HTTP_404_NOT_FOUND)


    def test_userbygroup_delete(self):
        
        def remove_from_group(client:APIClient, 
                              user_to_remove:User,
                              group_to_be_removed_from:Group,
                              expected_assertion:bool,
                              expected_return_code:status):
                    
            url= f"https://{self.domain}/api/groups/{group_to_be_removed_from.name}/{user_to_remove.id}"

            response= client.delete(url)
            assert response.status_code == expected_return_code

            user_to_remove.refresh_from_db()
            assert (group_to_be_removed_from not in user_to_remove.groups.all()) == expected_assertion
            
            user_to_remove.groups.add(group_to_be_removed_from)
            user_to_remove.save()

        
        #WITH AN UNAUTHENTICATED USER - NOK
        self.client.logout()
        remove_from_group(client= self.client,
                          user_to_remove= self.valid_user_managers[0],
                          group_to_be_removed_from=self.manager_group, 
                          expected_assertion=False,
                          expected_return_code=status.HTTP_401_UNAUTHORIZED
                          )
        remove_from_group(client= self.client,
                          user_to_remove= self.valid_user_dcms[0],
                          group_to_be_removed_from=self.dc_group, 
                          expected_assertion=False,
                          expected_return_code=status.HTTP_401_UNAUTHORIZED
                          )
        
        #WITH A DC MEMBER USER - NOK
        self.client.logout()
        self.client.force_login(user=self.valid_user_dcms[0])
        remove_from_group(client= self.client,
                          user_to_remove= self.valid_user_managers[0],
                          group_to_be_removed_from=self.manager_group, 
                          expected_assertion=False,
                          expected_return_code=status.HTTP_403_FORBIDDEN
                          )
        remove_from_group(client= self.client,
                          user_to_remove= self.valid_user_dcms[0],
                          group_to_be_removed_from=self.dc_group, 
                          expected_assertion=False,
                          expected_return_code=status.HTTP_403_FORBIDDEN
                          )
        
        #WITH A MANAGER MEMBER USER - OK
        self.client.logout()
        self.client.force_login(user=self.valid_user_managers[0])
        remove_from_group(client= self.client,
                          user_to_remove= self.valid_user_managers[0],
                          group_to_be_removed_from=self.manager_group, 
                          expected_assertion=True,
                          expected_return_code=status.HTTP_200_OK
                          )
        remove_from_group(client= self.client,
                          user_to_remove= self.valid_user_dcms[0],
                          group_to_be_removed_from=self.dc_group, 
                          expected_assertion=True,
                          expected_return_code=status.HTTP_200_OK
                          )
        
        # WITH WRONG USER ID PROVIDED

        url= f"https://{self.domain}/api/groups/manager/12"
        response= self.client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

        # WITH WRONG GROUP PROVIDED

        url= f"https://{self.domain}/api/groups/fakegroupname/{self.valid_user_managers[0].id}"
        response= self.client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

        