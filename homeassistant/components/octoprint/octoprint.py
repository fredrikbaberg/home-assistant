import requests
import asyncio
import time

import stomper
import websockets

class OctoPrint():
    def __init__(self, host, port):
        self.base_url = 'http://{}:{}'.format(host, port)
        self.headers = {}
        self.api_key = ''
        
    def _set_api_key(self, key):
        """ Set API key and header internally. """
        self.api_key = key
        self.headers = {
            'X-Api-Key': self.api_key
        }

    def get_api_key(self, app_name, user_name=None):
        """ Retrieve API key, stored locally. """
        response = requests.get(
            self.base_url+'/plugin/appkeys/probe',
            headers=self.headers,
            timeout=9
        )
        # If response status code is 204, can continue.
        if response.status_code == 204:
            response = requests.post(
                url=self.base_url+'/plugin/appkeys/request',
                headers=self.headers,
                json={
                    'app': app_name,
                    'user': user_name
                },
                timeout=9
            )
            # If response status code is 201, token is valid.
            if response.status_code == 201:
                app_token = response.json()['app_token']
                # Request API key
                response = requests.get(
                    self.base_url+'/plugin/appkeys/request/'+app_token,
                    headers=self.headers,
                    timeout=9
                )
                # Wait for user to accept token.
                while response.status_code == 202:
                    response = requests.get(
                        self.base_url+'/plugin/appkeys/request/'+app_token,
                        headers=self.headers,
                        timeout=9
                    )
                    print("Waiting for user to accept")
                    time.sleep(1.0)
                    if response.status_code == 200:
                        self._set_api_key(response.json()['api_key'])
                        return True
        return False

    def retrieve_appkeys(self):
        response = requests.get(
            self.base_url+'/api/plugin/appkeys',
            headers=self.headers,
            timeout=9
        )
        return response.json()
        
    def deregister(self):
        """ Remove API key from OctoPrint instance """
        response = requests.post(
            url=self.base_url+'/api/plugin/appkeys',
            headers=self.headers,
            json={
                "command": "revoke",
                "key": self.api_key
            },
            timeout=9
        )
        if response.status_code == 204:
            # Successfully removed API key.
            return True
        return False
        
    def get_printer_version(self):
        return requests.get(
            url=self.base_url+'/api/version',
            headers=self.headers,
            timeout=9
        ).json()

    def get_printer_status(self):
        """ Retrieve printer status """
        response = requests.get(
            url=self.base_url+'/api/printer',
            headers=self.headers,
            timeout=9
        )
        return response.json()
        
    def get_printer_connection(self):
        """ Retrieve printer connections """
        response = requests.get(
            url=self.base_url+'/api/connection',
            headers=self.headers,
            timeout=9
        )
        return response.json()
        
    def get_printer_files(self):
        """ Retrieve printer files """
        response = requests.get(
            url=self.base_url+'/api/files?recursive=true',
            headers=self.headers,
            timeout=9
        )
        return response.json()
        
    def get_printer_job(self):
        """ Retrieve printer job information """
        response = requests.get(
            url=self.base_url+'/api/job',
            headers=self.headers,
            timeout=9
        )
        return response.json()
        
    def pause_print(self):
        """ Pause print """
        response = requests.post(
            url=self.base_url+'/api/job',
            headers=self.headers,
            json={
                'command': 'pause',
                'action': 'pause'
            },
            timeout=9
        )
        return response

    def resume_print(self):
        """ Resume print """
        response = requests.post(
            url=self.base_url+'/api/job',
            headers=self.headers,
            json={
                'command': 'pause',
                'action': 'resume'
            },
            timeout=9
        )
        return response
        
    def get_printer_tool_state(self):
        """ Get printer tool state """
        return requests.get(
            url=self.base_url+'/api/printer/tool',
            headers=self.headers,
            timeout=9
        ).json()
        
    def get_printer_bed_state(self):
        """ Get printer tool state """
        return requests.get(
            url=self.base_url+'/api/printer/bed',
            headers=self.headers,
            timeout=9
        ).json()
        
    def get_printer_chamber_state(self):
        """ Get printer tool state """
        return requests.get(
            url=self.base_url+'/api/printer/chamber',
            headers=self.headers,
            timeout=9
        ).json()
        
    def get_printer_sd_state(self):
        """ Get printer tool state """
        return requests.get(
            url=self.base_url+'/api/printer/sd',
            headers=self.headers,
            timeout=9
        ).json()
        
    def get_printer_profiles(self):
        """ Get printer profiles """
        return requests.get(
            url=self.base_url+'/api/printerprofiles',
            headers=self.headers,
            timeout=9
        ).json()
        
    def get_printer_settings(self):
        """ Get printer profiles """
        return requests.get(
            url=self.base_url+'/api/settings',
            headers=self.headers,
            timeout=9
        ).json()
        
    def set_printer_settings(self):
        """ Set settings for OctoPrint """
        response = requests.post(
            url=self.base_url+'/api/settings',
            headers=self.headers,
            json={
                'appearance': {
                    'color': 'green'
                }
            },
            timeout=9
        )
        return response
        
    def get_slicing(self):
        """ Get slicers and slicing profiles """
        return requests.get(
            url=self.base_url+'/api/slicing',
            headers=self.headers,
            timeout=9
        ).json()
        
    def get_system_commands(self):
        """ Get slicers and slicing profiles """
        return requests.get(
            url=self.base_url+'/api/system/commands',
            headers=self.headers,
            timeout=9
        ).json()
        
    def get_timelapse(self):
        """ Retrieve a list of timelapses and the current config """
        return requests.get(
            url=self.base_url+'/api/timelapse',
            headers=self.headers,
            timeout=9
        ).json()


if __name__=='__main__':
    OP = OctoPrint("127.0.0.1", 5000)
    #print(OP.get_api_key("Home-Assistant"))
    OP._set_api_key('abc')
    print(OP.retrieve_appkeys())
    print(OP.get_printer_status())
    print(OP.get_printer_version())
    print(OP.get_printer_connection())
    print(OP.get_printer_files())
    print(OP.get_printer_job())
    print(OP.pause_print())
    print(OP.resume_print())
    print(OP.get_printer_tool_state())
    print(OP.get_printer_bed_state())
    print(OP.get_printer_chamber_state())
    print(OP.get_printer_sd_state())
    print(OP.get_printer_profiles())
    print(OP.get_printer_settings())
    print(OP.set_printer_settings())
    print(OP.get_slicing())
    print(OP.get_system_commands())
    print(OP.get_timelapse())
    #print(OP.deregister())
