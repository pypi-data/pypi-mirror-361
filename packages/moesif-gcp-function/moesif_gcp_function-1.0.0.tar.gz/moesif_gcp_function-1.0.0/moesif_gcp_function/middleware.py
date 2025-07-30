from moesifapi.moesif_api_client import *
from moesifapi.api_helper import *
from moesifapi.exceptions.api_exception import *
from moesifapi.models import *
from .client_ip import ClientIp
from .update_companies import Company
from .update_users import User
from . import global_variable as gv
from datetime import *
import base64
import json
import os
from pprint import pprint
import base64
from flask import request, make_response
import random
import math
try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode
from moesifpythonrequest.start_capture.start_capture import StartCapture
from datetime import datetime


def start_capture_outgoing(moesif_options):
    try:
        if moesif_options.get('DEBUG', False):
            print('[moesif] Start capturing outgoing requests')

        # Start capturing outgoing requests
        moesif_options['APPLICATION_ID'] = os.environ["MOESIF_APPLICATION_ID"]
        StartCapture().start_capture_outgoing(moesif_options)

        if moesif_options.get('DEBUG', False):
            print("[moesif] end capturing moesif options")
    except Exception as e:
        print('Error while starting to capture the outgoing events')
        print(e)
    return


# Initialized the client
api_client = gv.api_client

def update_user(user_profile, moesif_options):
    User().update_user(user_profile, api_client, moesif_options)


def update_users_batch(user_profiles, moesif_options):
    User().update_users_batch(user_profiles, api_client, moesif_options)


def update_company(company_profile, moesif_options):
    Company().update_company(company_profile, api_client, moesif_options)


def update_companies_batch(companies_profiles, moesif_options):
    Company().update_companies_batch(companies_profiles, api_client, moesif_options)

class MoesifLogger:
    def __init__(self, moesif_options):
        self.moesif_options = moesif_options
        self.LOG_BODY = self.moesif_options.get('LOG_BODY', True)
        self.DEBUG = self.moesif_options.get('DEBUG', False)
        self.user_id = None
        self.company_id = None
        self.session_token = None
        self.api_version = None
        self.metadata = None
        self.client_ip = ClientIp()

        # Set the client
        self.api_client = api_client

    def serialize(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, BaseModel):
            return obj.__dict__
        else:
            return obj
    
    def get_time_took_in_ms(self, start_time, end_time):
        return (end_time - start_time).total_seconds() * 1000

    def get_user_id(self, request, response):
            """Function to fetch UserId"""
            start_time_get_user_id = datetime.utcnow()
            username = None
            try:
                identify_user = self.moesif_options.get("IDENTIFY_USER")
                if identify_user is not None:
                    username = identify_user(request, response)
            except Exception as e:
                if self.DEBUG:
                    print("[moesif] cannot execute identify_user function, please check moesif settings.")
                    print(e)
            end_time_get_user_id = datetime.utcnow()
            if self.DEBUG:
                print("[moesif] Time took in fetching user id in millisecond - " + str(self.get_time_took_in_ms(start_time_get_user_id, end_time_get_user_id)))
            return username

    def get_company_id(self, request, response):
            """Function to fetch CompanyId"""
            start_time_get_company_id = datetime.utcnow()
            company_id = None
            try:
                identify_company = self.moesif_options.get("IDENTIFY_COMPANY")
                if identify_company is not None:
                    company_id = identify_company(request, response)
            except Exception as e:
                if self.DEBUG:
                    print("[moesif] cannot execute identify_company function, please check moesif settings.")
                    print(e)
            end_time_get_company_id = datetime.utcnow()
            if self.DEBUG:
                print("[moesif] Time took in fetching company id in millisecond - " + str(self.get_time_took_in_ms(start_time_get_company_id, end_time_get_company_id)))
            return company_id

    
    @classmethod
    def base64_body(cls, body):
        return base64.standard_b64encode(body).decode(encoding="UTF-8"), "base64"

    # Parse request and response body
    def parse_body(self, body):
        parsed_body = None
        transfer_encoding = None
        if self.LOG_BODY:
            try:
                parsed_body = json.loads(body)
                transfer_encoding = 'json'
            except Exception as e:
                parsed_body, transfer_encoding = self.base64_body(body)
        
        return parsed_body, transfer_encoding 

    # Build uri
    def build_uri(self, request):
        uri = ''
        try:
            query_string = request.query_string.decode('utf-8')

            if query_string:
                uri = f"{request.base_url}?{query_string}"
            else:
                uri = request.base_url
        except Exception as e:
            if self.DEBUG:
                print("[moesif] cannot read HTTP base url")
                print(e)

        return uri
    
    def __call__(self, func):
        def wrapper(*args, **kwargs):

            # Call the actual function and get the original response
            original_response = func(*args, **kwargs)

            # Create a Flask response object
            response = make_response(original_response)

            # Request Method
            request_verb = request.method
            if request_verb is None:
                print('[moesif] Google cloud function trigger must contain a http method like GET, POST, etc')
                return response
            
            # Request headers
            req_headers = {}
            try:
                req_headers = dict(request.headers.items())
            except Exception as e:
                if self.DEBUG:
                    print('[moesif] Error while fetching request headers')
                    print(e)

            # Request body
            req_body, req_transfer_encoding = self.parse_body(request.data)

            # Metadata
            start_time_get_metadata = datetime.utcnow()
            try:
                get_meta = self.moesif_options.get("GET_METADATA")
                if get_meta is not None:
                    self.metadata = get_meta(request, response)
            except Exception as e:
                if self.DEBUG:
                    print("[moesif] cannot execute GET_METADATA function, please check moesif settings.")
                    print(e)
            end_time_get_metadata = datetime.utcnow()
            if self.DEBUG:
                print("[moesif] Time took in fetching metadata in millisecond - " + str(self.get_time_took_in_ms(start_time_get_metadata, end_time_get_metadata)))

            # User Id
            start_time_identify_user = datetime.utcnow()
            self.user_id = self.get_user_id(request, response)
            end_time_identify_user = datetime.utcnow()
            if self.DEBUG:
                print("[moesif] Time took in identifying the user in millisecond - " + str(self.get_time_took_in_ms(start_time_identify_user, end_time_identify_user)))

            # Company Id
            start_time_identify_company = datetime.utcnow()
            self.company_id = self.get_company_id(request, response)
            end_time_identify_company = datetime.utcnow()
            if self.DEBUG:
                print("[moesif] Time took in identifying the company in millisecond - " + str(self.get_time_took_in_ms(start_time_identify_company, end_time_identify_company)))

            # Session Token 
            try:
                get_token = self.moesif_options.get("GET_SESSION_TOKEN")
                if get_token is not None:
                    self.session_token = get_token(request, response)
            except Exception as e:
                if self.DEBUG:
                    print("[moesif] cannot execute GET_SESSION_TOKEN function, please check moesif settings.")
                    print(e)

            # Api Version
            try:
                get_version = self.moesif_options.get("GET_API_VERSION")
                if get_version is not None:
                    self.api_version = get_version(request, response)
            except Exception as e:
                if self.DEBUG:
                    print("[moesif] cannot execute GET_API_VERSION function, please check moesif settings.")
                    print(e)

            # Response status
            try:
                resp_status = response.status_code
            except Exception as e:
                if self.DEBUG:
                    print('[moesif] Google cloud function trigger must contain a response status code')
                    return response

            # Response headers
            rsp_headers = {}
            try:
                rsp_headers = dict(response.headers.items())
            except Exception as e:
                if self.DEBUG:
                    print('[moesif] Error while fetching request headers')
                    print(e)

            # Response body
            rsp_body, rsp_transfer_encoding = self.parse_body(response.data)

            # Event Request Model
            event_req = EventRequestModel(time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3],
                uri = self.build_uri(request),
                verb = request_verb,
                api_version = self.api_version,
                ip_address = self.client_ip.get_client_address(req_headers, request.remote_addr),
                headers = req_headers,
                body = req_body,
                transfer_encoding = req_transfer_encoding)

            # Event Response Model
            event_rsp = EventResponseModel(time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3],
                status = resp_status,
                headers = rsp_headers,
                body = rsp_body,
                transfer_encoding = rsp_transfer_encoding)

            # Event Model
            event_model = EventModel(request = event_req,
                response = event_rsp,
                user_id = self.user_id,
                company_id = self.company_id,
                session_token = self.session_token,
                metadata = self.metadata)


            # Mask Event Model
            try:
                mask_event_model = self.moesif_options.get('MASK_EVENT_MODEL', None)
                if mask_event_model is not None:
                    event_model = mask_event_model(event_model)
            except Exception as e:
                if self.DEBUG:
                    print("[moesif] cannot execute MASK_EVENT_MODEL function. Please check moesif settings.", e)
            
            # Skip Event
            try:
                skip_event = self.moesif_options.get('SKIP', None)
                if skip_event is not None:
                    if skip_event(request, response):
                        if self.DEBUG:
                            print('[moesif] Skip sending event to Moesif')
                        return response
            except Exception as e:
                if self.DEBUG:
                    print("[moesif] Having difficulty executing skip_event function. Please check moesif settings.", e)

            # Add direction field
            event_model.direction = "Incoming"

            # Send event to Moesif
            if self.DEBUG:
                print('[moesif] Moesif Event Model:')
                print(json.dumps(event_model.__dict__, default=serialize, separators=(',', ':')))


            # Sampling Rate
            try:
                random_percentage = random.random() * 100
                gv.sampling_percentage = gv.app_config.get_sampling_percentage(
                    event_model,
                    json.loads(gv.config.raw_body),
                    self.user_id,
                    self.company_id,
                )

                if gv.sampling_percentage >= random_percentage:
                    event_model.weight = 1 if gv.sampling_percentage == 0 else math.floor(
                        100 / gv.sampling_percentage)

                    if datetime.utcnow() > gv.last_updated_time + timedelta(seconds=gv.refresh_config_time_seconds):
                        event_send = self.api_client.create_event(event_model)
                    else:
                        self.api_client.create_event(event_model)

                    try:
                        # Check if we need to update config
                        new_config_etag = event_send['x-moesif-config-etag']
                        if gv.config_etag is None or (gv.config_etag != new_config_etag):
                            gv.config_etag = new_config_etag
                            gv.config = gv.app_config.get_config(self.api_client, self.DEBUG)
                    except Exception as ex:
                        # ignore the error because "event_send" is not set in non-blocking call
                        pass
                    finally:
                        gv.last_updated_time = datetime.utcnow()

                else:
                    if self.DEBUG:
                        print("Skipped Event due to sampling percentage: " + str(
                            gv.sampling_percentage) + " and random percentage: " + str(random_percentage))
            except Exception as ex:
                print("[moesif] Error when fetching sampling rate from app config", ex)

            # Send response
            return response

        # Return wrapper
        return wrapper
